from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Case(models.Model):
    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("UNDER_REVIEW", "Under Review"),
        ("OPEN", "Open"),
        ("CLOSED", "Closed"),
        ("INVALIDATED", "Invalidated"),
    ]

    CRIME_LEVEL_CHOICES = [
        (1, "Level 1"),
        (2, "Level 2"),
        (3, "Level 3"),
        (4, "Critical"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="DRAFT")

    # ✅ Added in Step 2
    crime_level = models.PositiveSmallIntegerField(
        choices=CRIME_LEVEL_CHOICES,
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(4)],
    )

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="cases_created")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.id} - {self.title}"

    @property
    def is_critical(self) -> bool:
        return self.crime_level == 4




class CaseComplainant(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    case = models.ForeignKey("cases.Case", on_delete=models.CASCADE, related_name="complainant_links")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="case_complainant_links")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    cadet_message = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_case_complainants",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("case", "user")
        indexes = [
            models.Index(fields=["case", "status"]),
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self) -> str:
        return f"CaseComplainant(case_id={self.case_id}, user_id={self.user_id}, status={self.status})"


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


class DetectiveBoard(models.Model):
    case = models.OneToOneField(Case, on_delete=models.CASCADE, related_name="detective_board")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="detective_boards_created")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


class DetectiveBoardItem(models.Model):
    ITEM_TYPES = [
        ("NOTE", "Note"),
        ("EVIDENCE", "Evidence"),
        ("SUSPECT", "Suspect"),
        ("COMPLAINT", "Complaint"),
        ("CRIME_SCENE", "CrimeScene"),
        ("CUSTOM", "Custom"),
    ]

    board = models.ForeignKey(DetectiveBoard, on_delete=models.CASCADE, related_name="items")
    item_type = models.CharField(max_length=30, choices=ITEM_TYPES, default="NOTE")

    title = models.CharField(max_length=200, blank=True, default="")
    content = models.TextField(blank=True, default="")

    ref_model = models.CharField(max_length=50, blank=True, default="")
    ref_id = models.PositiveIntegerField(null=True, blank=True)

    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    meta = models.JSONField(blank=True, default=dict)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="detective_board_items_created")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


class DetectiveBoardLink(models.Model):
    board = models.ForeignKey(DetectiveBoard, on_delete=models.CASCADE, related_name="links")
    source = models.ForeignKey(DetectiveBoardItem, on_delete=models.CASCADE, related_name="outgoing_links")
    target = models.ForeignKey(DetectiveBoardItem, on_delete=models.CASCADE, related_name="incoming_links")
    label = models.CharField(max_length=200, blank=True, default="")
    meta = models.JSONField(blank=True, default=dict)
    created_by = models.ForeignKey(settings.AUTH_user_MODEL if hasattr(settings, "AUTH_user_MODEL") else settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="detective_board_links_created")
    created_at = models.DateTimeField(default=timezone.now)


# =========================
# Step 2: Flow Models
# =========================

class SolveRequest(models.Model):
    STATUS_CHOICES = [
        ("SUBMITTED", "Submitted"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="solve_requests")
    suspect_ids = models.JSONField(default=list, blank=True)  # list[int]
    note = models.TextField(blank=True, default="")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="SUBMITTED")

    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="solve_requests_submitted")
    submitted_at = models.DateTimeField(default=timezone.now)

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="solve_requests_reviewed",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_comment = models.TextField(blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["case"],
                condition=Q(status="SUBMITTED"),
                name="uniq_pending_solve_request_per_case",
            )
        ]


class Interrogation(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="interrogations")
    suspect_id = models.PositiveIntegerField()

    detective_score = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(10)])
    sergent_score = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(10)])

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["case", "suspect_id"], name="uniq_interrogation_case_suspect")
        ]


class CaptainDecision(models.Model):
    DECISION_CHOICES = [
        ("SEND_TO_TRIAL", "Send to trial"),
        ("RELEASE", "Release"),
    ]

    case = models.OneToOneField(Case, on_delete=models.CASCADE, related_name="captain_decision")
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES)
    comment = models.TextField(blank=True, default="")

    decided_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="captain_decisions")
    decided_at = models.DateTimeField(default=timezone.now)

    # Chief step (only required for critical crimes when SEND_TO_TRIAL)
    chief_approved = models.BooleanField(null=True, blank=True)
    chief_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="chief_approvals",
    )
    chief_at = models.DateTimeField(null=True, blank=True)
    chief_comment = models.TextField(blank=True, default="")


class Trial(models.Model):
    VERDICT_CHOICES = [
        ("GUILTY", "Guilty"),
        ("INNOCENT", "Innocent"),
    ]

    case = models.OneToOneField(Case, on_delete=models.CASCADE, related_name="trial")
    verdict = models.CharField(max_length=20, choices=VERDICT_CHOICES)
    punishment_title = models.CharField(max_length=200, blank=True, default="")
    punishment_description = models.TextField(blank=True, default="")

    judged_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="trials_judged")
    judged_at = models.DateTimeField(default=timezone.now)


class CaseNotification(models.Model):
    TYPE_CHOICES = [
        ("EVIDENCE_ADDED", "Evidence added"),
        ("INFO", "Info"),
    ]

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="notifications")
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="case_notifications")

    notif_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default="INFO")
    message = models.TextField()

    ref_model = models.CharField(max_length=50, blank=True, default="")
    ref_id = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    read_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_read(self) -> bool:
        return self.read_at is not None
