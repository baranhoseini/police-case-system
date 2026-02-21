from django.conf import settings
from django.db import models
from django.utils import timezone
import secrets


class PaymentRequest(models.Model):
    PURPOSE_BAIL = "BAIL"
    PURPOSE_FINE = "FINE"
    PURPOSES = [(PURPOSE_BAIL, "Bail"), (PURPOSE_FINE, "Fine")]

    STATUS_DRAFT = "DRAFT"
    STATUS_APPROVED = "APPROVED"
    STATUS_INITIATED = "INITIATED"
    STATUS_PAID = "PAID"
    STATUS_FAILED = "FAILED"
    STATUS = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_INITIATED, "Initiated"),
        (STATUS_PAID, "Paid"),
        (STATUS_FAILED, "Failed"),
    ]

    payer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payment_requests",
    )

    case_id = models.IntegerField(null=True, blank=True)
    suspect_id = models.IntegerField(null=True, blank=True)
    crime_level = models.PositiveSmallIntegerField()  # 1..4

    purpose = models.CharField(max_length=10, choices=PURPOSES)
    amount_rials = models.PositiveBigIntegerField()

    status = models.CharField(max_length=20, choices=STATUS, default=STATUS_DRAFT)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_payment_requests",
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="approved_payment_requests",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    public_id = models.CharField(max_length=32, unique=True, blank=True, default="")
    gateway = models.CharField(max_length=30, default="mock")
    authority = models.CharField(max_length=128, blank=True, default="")
    ref_id = models.CharField(max_length=128, blank=True, default="")

    created_at = models.DateTimeField(default=timezone.now)
    paid_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.public_id:
            self.public_id = secrets.token_hex(8)
        super().save(*args, **kwargs)

    def mark_paid(self, ref_id: str = "", authority: str = ""):
        self.status = self.STATUS_PAID
        self.ref_id = ref_id or self.ref_id
        self.authority = authority or self.authority
        self.paid_at = timezone.now()
        self.save(update_fields=["status", "ref_id", "authority", "paid_at"])