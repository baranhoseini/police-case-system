from rest_framework import serializers

from .models import Complaint


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = [
            "id",
            "created_by",
            "created_at",
            "payload",
            "status",
            "bad_submission_count",
            "cadet_error_message",
            "officer_error_message",
            "cadet",
            "officer",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "created_at",
            "status",
            "bad_submission_count",
            "cadet_error_message",
            "officer_error_message",
            "cadet",
            "officer",
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
    status = serializers.ChoiceField(choices=["approve", "request_changes"])
    error_message = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if attrs["status"] == "request_changes" and not attrs.get("error_message"):
            raise serializers.ValidationError({"error_message": "This field is required."})
        return attrs


class OfficerReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["approve", "defect"])
    error_message = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        if attrs["status"] == "defect" and not attrs.get("error_message"):
            raise serializers.ValidationError({"error_message": "This field is required."})
        return attrs
