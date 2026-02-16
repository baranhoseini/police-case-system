from django.conf import settings
from django.db import models
from django.utils import timezone


class Case(models.Model):
    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("UNDER_REVIEW", "Under Review"),
        ("OPEN", "Open"),
        ("CLOSED", "Closed"),
        ("INVALIDATED", "Invalidated"),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="DRAFT")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="cases_created")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.id} - {self.title}"


class Complaint(models.Model):
    case = models.OneToOneField(Case, on_delete=models.CASCADE, related_name="complaint", null=True, blank=True)
    complainant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="complaints")
    details = models.TextField()
    revision_count = models.PositiveIntegerField(default=0)
    rejection_reason = models.TextField(blank=True, default="")

    def strike(self, reason: str):
        self.revision_count += 1
        self.rejection_reason = reason
        self.save(update_fields=["revision_count", "rejection_reason"])
        if self.case and self.revision_count >= 3:
            self.case.status = "INVALIDATED"
            self.case.save(update_fields=["status"])


class CrimeSceneReport(models.Model):
    case = models.OneToOneField(Case, on_delete=models.CASCADE, related_name="crime_scene", null=True, blank=True)
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="scene_reports")
    report = models.TextField()
    witnessed_phone = models.CharField(max_length=20, blank=True, default="")
    witnessed_national_id = models.CharField(max_length=20, blank=True, default="")
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_crime_scenes",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
