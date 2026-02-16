from rest_framework import serializers
from .models import Case, Complaint, CrimeSceneReport

class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = ("id","title","description","status","created_by","created_at")
        read_only_fields = ("id","status","created_by","created_at")

class ComplaintCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ("details",)

class CrimeSceneCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrimeSceneReport
        fields = ("report","witnessed_phone","witnessed_national_id")

class CaseFromComplaintSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    details = serializers.CharField()
