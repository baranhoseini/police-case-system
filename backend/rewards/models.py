from django.conf import settings
from django.db import models
from django.utils import timezone
import secrets


class RewardTip(models.Model):
    STATUS_SUBMITTED = "SUBMITTED"
    STATUS_OFFICER_REJECTED = "OFFICER_REJECTED"
    STATUS_OFFICER_APPROVED = "OFFICER_APPROVED"
    STATUS_DETECTIVE_APPROVED = "DETECTIVE_APPROVED"

    STATUS = [
        (STATUS_SUBMITTED, "Submitted"),
        (STATUS_OFFICER_REJECTED, "Officer Rejected"),
        (STATUS_OFFICER_APPROVED, "Officer Approved"),
        (STATUS_DETECTIVE_APPROVED, "Detective Approved"),
    ]

    citizen = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="tips",
    )

    citizen_name = models.CharField(max_length=200)
    citizen_national_id = models.CharField(max_length=50)
    citizen_phone = models.CharField(max_length=50)

    suspect_name = models.CharField(max_length=200)
    suspect_last_seen = models.CharField(max_length=500, blank=True, default="")
    message = models.TextField()

    status = models.CharField(max_length=30, choices=STATUS, default=STATUS_SUBMITTED)
    unique_code = models.CharField(max_length=32, blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now)

    def __init__(self, *args, **kwargs):
        # Backward-compat: tests/older code may pass `info` instead of `message`.
        if "info" in kwargs and "message" not in kwargs:
            kwargs["message"] = kwargs.pop("info")
        super().__init__(*args, **kwargs)

    reviewed_by_officer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="reviewed_tips_as_officer",
    )
    officer_reviewed_at = models.DateTimeField(null=True, blank=True)
    officer_note = models.TextField(blank=True, default="")

    approved_by_detective = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="approved_tips_as_detective",
    )
    detective_approved_at = models.DateTimeField(null=True, blank=True)
    detective_note = models.TextField(blank=True, default="")

    def approve_by_detective(self):
        self.status = self.STATUS_DETECTIVE_APPROVED
        if not self.unique_code:
            self.unique_code = secrets.token_hex(8)
        self.save(update_fields=["status", "unique_code"])