from rest_framework import serializers
from .models import Evidence

class EvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evidence
        fields = "__all__"
        read_only_fields = ("id", "created_at", "created_by")

    def validate(self, attrs):
        evidence_type = attrs.get("evidence_type", getattr(self.instance, "evidence_type", None))

        if evidence_type == "VEHICLE":
            plate = (attrs.get("plate_number") or "").strip()
            serial = (attrs.get("serial_number") or "").strip()

            if plate and serial:
                raise serializers.ValidationError(
                    {"vehicle": "Vehicle evidence cannot have both plate_number and serial_number."}
                )
            if not plate and not serial:
                raise serializers.ValidationError(
                    {"vehicle": "Vehicle evidence must have either plate_number or serial_number."}
                )

        return attrs
