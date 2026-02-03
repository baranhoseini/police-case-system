from django.conf import settings
from django.db import models
from django.utils import timezone
import secrets

class RewardTip(models.Model):
    STATUS = [
        ("SUBMITTED","Submitted"),
        ("OFFICER_REJECTED","Officer Rejected"),
        ("OFFICER_APPROVED","Officer Approved"),
        ("DETECTIVE_APPROVED","Detective Approved"),
    ]
    citizen = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="tips")
    suspect_name = models.CharField(max_length=200)
    info = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS, default="SUBMITTED")
    unique_code = models.CharField(max_length=32, blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now)

    def approve_by_detective(self):
        self.status = "DETECTIVE_APPROVED"
        if not self.unique_code:
            self.unique_code = secrets.token_hex(8)
        self.save(update_fields=["status","unique_code"])
