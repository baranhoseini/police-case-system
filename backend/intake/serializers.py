from rest_framework import serializers
from .models import Complaint


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = [
            "id",
            "created_by",
            "payload",
            "status",
            "bad_submission_count",
            "cadet_error_message",
            "officer_error_message",
            "cadet",
            "officer",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "status",
            "bad_submission_count",
            "cadet_error_message",
            "officer_error_message",
            "cadet",
            "officer",
            "created_at",
            "updated_at",
        ]


class ComplaintCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ["payload"]


class ResubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ["payload"]


class CadetReviewSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["approve", "request_changes"])
    error_message = serializers.CharField(required=False, allow_blank=True)


class OfficerReviewSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["approve", "defect"])
    error_message = serializers.CharField(required=False, allow_blank=True)
