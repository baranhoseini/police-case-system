from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from cases.models import Case


class Evidence(models.Model):
    TYPE_GENERIC = "GENERIC"
    TYPE_MEDICAL = "MEDICAL"
    TYPE_VEHICLE = "VEHICLE"
    TYPE_ID_DOC = "ID_DOC"
    TYPE_WITNESS = "WITNESS"

    TYPE_CHOICES = [
        (TYPE_GENERIC, "Generic"),
        (TYPE_MEDICAL, "Medical/Biological"),
        (TYPE_VEHICLE, "Vehicle"),
        (TYPE_ID_DOC, "ID Document"),
        (TYPE_WITNESS, "Witness"),
    ]

    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="evidence")
    evidence_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_GENERIC)

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="evidence_created"
    )

    image_url = models.URLField(blank=True, default="")
    image_urls = models.JSONField(blank=True, default=list)
    medical_result = models.TextField(blank=True, default="")

    vehicle_model = models.CharField(max_length=100, blank=True, default="")
    vehicle_color = models.CharField(max_length=50, blank=True, default="")
    plate_number = models.CharField(max_length=30, blank=True, default="")
    serial_number = models.CharField(max_length=50, blank=True, default="")

    id_fields = models.JSONField(blank=True, default=dict)

    transcription = models.TextField(blank=True, default="")
    media_urls = models.JSONField(blank=True, default=list)

    def clean(self):
        if self.evidence_type == self.TYPE_VEHICLE:
            has_plate = bool((self.plate_number or "").strip())
            has_serial = bool((self.serial_number or "").strip())
            if has_plate and has_serial:
                raise ValidationError("Vehicle evidence cannot have both plate_number and serial_number.")
            if not has_plate and not has_serial:
                raise ValidationError("Vehicle evidence must have either plate_number or serial_number.")

        if self.evidence_type == self.TYPE_MEDICAL:
            urls = self.image_urls if self.image_urls is not None else []
            if not isinstance(urls, list):
                raise ValidationError("image_urls must be a list of URLs.")
            has_single = bool((self.image_url or "").strip())
            has_list = any(isinstance(u, str) and u.strip() for u in urls)
            if not has_single and not has_list:
                raise ValidationError("Medical evidence must include at least one image URL.")

        if self.evidence_type == self.TYPE_ID_DOC:
            if self.id_fields is None:
                self.id_fields = {}
            if not isinstance(self.id_fields, dict):
                raise ValidationError("id_fields must be an object/dict.")

        if self.evidence_type == self.TYPE_WITNESS:
            if not isinstance(self.media_urls, list):
                raise ValidationError("media_urls must be a list of URLs.")
            has_text = bool((self.transcription or "").strip())
            has_media = any(isinstance(u, str) and u.strip() for u in (self.media_urls or []))
            if not has_text and not has_media:
                raise ValidationError("Witness evidence must include transcription or at least one media URL.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
