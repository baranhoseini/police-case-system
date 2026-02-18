from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from cases.models import Case


class Evidence(models.Model):
    TYPE_CHOICES = [
        ("GENERIC", "Generic"),
        ("MEDICAL", "Medical/Biological"),
        ("VEHICLE", "Vehicle"),
        ("ID_DOC", "ID Document"),
    ]

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="evidence")
    evidence_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="GENERIC")

    # common
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="evidence_created"
    )

    # MEDICAL
    image_url = models.URLField(blank=True, default="")          # backward-compatible
    image_urls = models.JSONField(blank=True, default=list)      # ✅ supports multiple images
    medical_result = models.TextField(blank=True, default="")

    # VEHICLE
    vehicle_model = models.CharField(max_length=100, blank=True, default="")
    vehicle_color = models.CharField(max_length=50, blank=True, default="")
    plate_number = models.CharField(max_length=30, blank=True, default="")
    serial_number = models.CharField(max_length=50, blank=True, default="")

    # ID_DOC (flexible fields)
    id_fields = models.JSONField(blank=True, default=dict)

    def clean(self):
        # Vehicle constraint: plate XOR serial (not both)
        if self.evidence_type == "VEHICLE":
            has_plate = bool((self.plate_number or "").strip())
            has_serial = bool((self.serial_number or "").strip())
            if has_plate and has_serial:
                raise ValidationError("Vehicle evidence cannot have both plate_number and serial_number.")
            if not has_plate and not has_serial:
                raise ValidationError("Vehicle evidence must have either plate_number or serial_number.")

        # Medical must have at least one image (single or list)
        if self.evidence_type == "MEDICAL":
            urls = self.image_urls if self.image_urls is not None else []
            if not isinstance(urls, list):
                raise ValidationError("image_urls must be a list of URLs.")
            has_single = bool((self.image_url or "").strip())
            has_list = any(isinstance(u, str) and u.strip() for u in urls)
            if not has_single and not has_list:
                raise ValidationError("Medical evidence must include at least one image URL.")

        # ID_DOC fields must be dict
        if self.evidence_type == "ID_DOC":
            if self.id_fields is None:
                self.id_fields = {}
            if not isinstance(self.id_fields, dict):
                raise ValidationError("id_fields must be an object/dict.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
