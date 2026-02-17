from django.conf import settings
from django.db import models


class ComplaintStatus(models.TextChoices):
    SUBMITTED = "SUBMITTED", "Submitted"
    NEEDS_FIX = "NEEDS_FIX", "Needs Fix"
    INVALIDATED = "INVALIDATED", "Invalidated"
    CADET_APPROVED = "CADET_APPROVED", "Cadet Approved"
    OFFICER_DEFECT = "OFFICER_DEFECT", "Officer Defect"
    OFFICER_APPROVED = "OFFICER_APPROVED", "Officer Approved"


class Complaint(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="intake_complaints", 
    )

    payload = models.JSONField(default=dict, blank=True)

    status = models.CharField(
        max_length=32, choices=ComplaintStatus.choices, default=ComplaintStatus.SUBMITTED
    )

    bad_submission_count = models.PositiveSmallIntegerField(default=0)

    cadet_error_message = models.TextField(blank=True, default="")
    officer_error_message = models.TextField(blank=True, default="")

    cadet = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cadet_assigned_intake_complaints",
    )
    officer = models.ForeignKey(
        settings.AUTH_USER_MODEL,  
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="officer_assigned_intake_complaints",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def invalidate_if_needed(self) -> bool:
        if self.bad_submission_count >= 3:
            self.status = ComplaintStatus.INVALIDATED
            return True
        return False

    def __str__(self) -> str:
        return f"Complaint #{self.pk} ({self.status})"
