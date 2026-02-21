from rest_framework import serializers
from .models import PaymentRequest


class PaymentRequestCreateSerializer(serializers.Serializer):
    payer_user_id = serializers.IntegerField()
    purpose = serializers.ChoiceField(choices=[PaymentRequest.PURPOSE_BAIL, PaymentRequest.PURPOSE_FINE])
    amount_rials = serializers.IntegerField(min_value=1)
    crime_level = serializers.IntegerField(min_value=1, max_value=4)
    case_id = serializers.IntegerField(required=False, allow_null=True)
    suspect_id = serializers.IntegerField(required=False, allow_null=True)


class PaymentRequestPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentRequest
        fields = (
            "id",
            "public_id",
            "payer_id",
            "purpose",
            "amount_rials",
            "crime_level",
            "case_id",
            "suspect_id",
            "status",
            "gateway",
            "authority",
            "ref_id",
            "created_at",
            "approved_at",
            "paid_at",
        )
        read_only_fields = fields