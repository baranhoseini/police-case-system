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
            plate = (
                attrs.get("plate_number")
                if "plate_number" in attrs
                else getattr(self.instance, "plate_number", "")
            ).strip()
            serial = (
                attrs.get("serial_number")
                if "serial_number" in attrs
                else getattr(self.instance, "serial_number", "")
            ).strip()

            if plate and serial:
                raise serializers.ValidationError(
                    {"vehicle": "Vehicle evidence cannot have both plate_number and serial_number."}
                )
            if not plate and not serial:
                raise serializers.ValidationError(
                    {"vehicle": "Vehicle evidence must have either plate_number or serial_number."}
                )

        if evidence_type == "WITNESS":
            statement = (
                attrs.get("witness_statement")
                if "witness_statement" in attrs
                else getattr(self.instance, "witness_statement", "")
            )
            if not (statement or "").strip():
                raise serializers.ValidationError(
                    {"witness_statement": "This field is required for WITNESS evidence."}
                )

            media_urls = (
                attrs.get("media_urls")
                if "media_urls" in attrs
                else getattr(self.instance, "media_urls", [])
            )
            if media_urls is None:
                media_urls = []
            if not isinstance(media_urls, list):
                raise serializers.ValidationError({"media_urls": "media_urls must be a list of URLs."})

        if evidence_type == "MEDICAL":
            single = (
                attrs.get("image_url")
                if "image_url" in attrs
                else getattr(self.instance, "image_url", "")
            )
            image_urls = (
                attrs.get("image_urls")
                if "image_urls" in attrs
                else getattr(self.instance, "image_urls", [])
            )

            if image_urls is None:
                image_urls = []
            if not isinstance(image_urls, list):
                raise serializers.ValidationError({"image_urls": "image_urls must be a list of URLs."})

            has_single = bool((single or "").strip())
            has_list = any(isinstance(u, str) and u.strip() for u in image_urls)
            if not has_single and not has_list:
                raise serializers.ValidationError(
                    {"medical": "Medical evidence must include at least one image URL."}
                )

        if evidence_type == "ID_DOC":
            id_fields = (
                attrs.get("id_fields")
                if "id_fields" in attrs
                else getattr(self.instance, "id_fields", {})
            )
            if id_fields is None:
                id_fields = {}
            if not isinstance(id_fields, dict):
                raise serializers.ValidationError({"id_fields": "id_fields must be an object/dict."})

        return attrs
