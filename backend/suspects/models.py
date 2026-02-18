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
        # Keep max_l/max_d aligned with current chase duration and case severity
        if self.chase_started_at:
            self.max_l = max(1, (timezone.now() - self.chase_started_at).days)
        if self.case_id and self.case:
            self.max_d = int(getattr(self.case, "crime_level", 1) or 1)
        super().save(*args, **kwargs)

def __str__(self) -> str:
        return self.full_name
