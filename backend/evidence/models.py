from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
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

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="evidence_created")

    # MEDICAL
    image_url = models.URLField(blank=True, default="")  # keep simple for now
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
            has_plate = bool(self.plate_number.strip())
            has_serial = bool(self.serial_number.strip())
            if has_plate and has_serial:
                raise ValidationError("Vehicle evidence cannot have both plate_number and serial_number.")
            if not has_plate and not has_serial:
                raise ValidationError("Vehicle evidence must have either plate_number or serial_number.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
