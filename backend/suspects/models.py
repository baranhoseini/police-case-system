from django.db import models
from django.utils import timezone
from datetime import timedelta
from cases.models import Case

class Suspect(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="suspects")
    full_name = models.CharField(max_length=200)
    chase_started_at = models.DateTimeField(default=timezone.now)

    # Minimal inputs for ranking formula:
    max_l = models.PositiveIntegerField(default=1)  # Lj
    max_d = models.PositiveIntegerField(default=1)  # Di

    @property
    def is_most_wanted(self) -> bool:
        return timezone.now() - self.chase_started_at >= timedelta(days=30)

    @property
    def rank_score(self) -> int:
        return int(self.max_l) * int(self.max_d)

    @property
    def reward_amount_rials(self) -> int:
        return self.rank_score * 20_000_000
