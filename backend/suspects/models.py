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

    def __str__(self) -> str:
        return self.full_name
