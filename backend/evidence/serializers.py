from rest_framework import serializers
from .models import Evidence


class EvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evidence
        fields = "__all__"
        read_only_fields = ("id", "created_at", "created_by")

    def validate(self, attrs):
        evidence_type = attrs.get("evidence_type", getattr(self.instance, "evidence_type", None))

        if evidence_type == Evidence.TYPE_VEHICLE:
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

        if evidence_type == Evidence.TYPE_MEDICAL:
            single = (
                attrs.get("image_url") if "image_url" in attrs else getattr(self.instance, "image_url", "")
            ).strip()
            urls = attrs.get("image_urls") if "image_urls" in attrs else getattr(self.instance, "image_urls", [])
            if urls is None:
                urls = []
            if not isinstance(urls, list):
                raise serializers.ValidationError({"image_urls": "image_urls must be a list of URLs."})

            has_single = bool(single)
            has_list = any(isinstance(u, str) and u.strip() for u in urls)
            if not has_single and not has_list:
                raise serializers.ValidationError({"medical": "Medical evidence must include at least one image URL."})

        if evidence_type == Evidence.TYPE_ID_DOC:
            id_fields = attrs.get("id_fields") if "id_fields" in attrs else getattr(self.instance, "id_fields", {})
            if id_fields is None:
                id_fields = {}
            if not isinstance(id_fields, dict):
                raise serializers.ValidationError({"id_fields": "id_fields must be an object/dict."})

        if evidence_type == Evidence.TYPE_WITNESS:
            transcription = (
                attrs.get("transcription")
                if "transcription" in attrs
                else getattr(self.instance, "transcription", "")
            )
            media_urls = (
                attrs.get("media_urls") if "media_urls" in attrs else getattr(self.instance, "media_urls", [])
            )
            if media_urls is None:
                media_urls = []
            if not isinstance(media_urls, list):
                raise serializers.ValidationError({"media_urls": "media_urls must be a list of URLs."})

            has_text = bool((transcription or "").strip())
            has_media = any(isinstance(u, str) and u.strip() for u in media_urls)
            if not has_text and not has_media:
                raise serializers.ValidationError(
                    {"witness": "Witness evidence must include transcription or at least one media URL."}
                )

        return attrs

    def create(self, validated_data):
        if validated_data.get("evidence_type") == Evidence.TYPE_MEDICAL:
            urls = validated_data.get("image_urls") or []
            single = (validated_data.get("image_url") or "").strip()
            if (not urls) and single:
                validated_data["image_urls"] = [single]
            if (not single) and urls:
                first = next((u for u in urls if isinstance(u, str) and u.strip()), "")
                validated_data["image_url"] = first or ""
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if (validated_data.get("evidence_type", instance.evidence_type)) == Evidence.TYPE_MEDICAL:
            urls = validated_data.get("image_urls", instance.image_urls) or []
            single = (validated_data.get("image_url", instance.image_url) or "").strip()
            if (not urls) and single:
                validated_data["image_urls"] = [single]
            if (not single) and urls:
                first = next((u for u in urls if isinstance(u, str) and u.strip()), "")
                validated_data["image_url"] = first or ""
        return super().update(instance, validated_data)
