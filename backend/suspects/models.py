from datetime import timedelta

from django.db import models
from django.utils import timezone

from cases.models import Case

MOST_WANTED_DAYS = 30


class SuspectQuerySet(models.QuerySet):
    def most_wanted(self):
        cutoff = timezone.now() - timedelta(days=MOST_WANTED_DAYS)
        return self.filter(chase_started_at__lte=cutoff)


class Suspect(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="suspects")
    full_name = models.CharField(max_length=200)
    national_id = models.CharField(max_length=20, blank=True, db_index=True)
    phone = models.CharField(max_length=20, blank=True)
    photo_url = models.URLField(blank=True)
    chase_started_at = models.DateTimeField(default=timezone.now)

    max_l = models.PositiveIntegerField(default=1)
    max_d = models.PositiveIntegerField(default=1)

    objects = SuspectQuerySet.as_manager()

    def _group_qs(self):
        if self.national_id:
            return Suspect.objects.filter(national_id=self.national_id)
        return Suspect.objects.filter(full_name=self.full_name, phone=self.phone)

    @property
    def is_most_wanted(self) -> bool:
        return timezone.now() - self.chase_started_at >= timedelta(days=MOST_WANTED_DAYS)

    @property
    def rank_score(self) -> int:
        return int(self.max_l) * int(self.max_d)

    @property
    def reward_amount_rials(self) -> int:
        return self.rank_score * 20_000_000

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        now = timezone.now()
        qs = self._group_qs().select_related("case").only("id", "chase_started_at", "case__crime_level")

        max_l = 1
        max_d = 1

        for s in qs:
            if s.chase_started_at:
                days = (now - s.chase_started_at).days
                max_l = max(max_l, days if days > 0 else 1)

            crime_level = getattr(s.case, "crime_level", 1) if s.case_id else 1
            max_d = max(max_d, int(crime_level or 1))

        qs.update(max_l=max_l, max_d=max_d)

        self.max_l = max_l
        self.max_d = max_d

    def __str__(self) -> str:
        return self.full_name
