from rest_framework import serializers
from .models import (
    Case,
    Complaint,
    CrimeSceneReport,
    DetectiveBoard,
    DetectiveBoardItem,
    DetectiveBoardLink,
    SolveRequest,
    Interrogation,
    CaptainDecision,
    Trial,
    CaseNotification,
)


class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = ("id", "title", "description", "status", "crime_level", "created_by", "created_at")
        read_only_fields = ("id", "status", "created_by", "created_at")


class ComplaintCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = ("details",)


class CrimeSceneCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrimeSceneReport
        fields = ("report", "witnessed_phone", "witnessed_national_id")


class CaseFromComplaintSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    details = serializers.CharField()


class ComplaintResubmitSerializer(serializers.Serializer):
    details = serializers.CharField()


class DetectiveBoardItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetectiveBoardItem
        fields = (
            "id",
            "board",
            "item_type",
            "title",
            "content",
            "ref_model",
            "ref_id",
            "x",
            "y",
            "meta",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "board", "created_by", "created_at", "updated_at")

    def validate(self, attrs):
        ref_id = attrs.get("ref_id", getattr(self.instance, "ref_id", None))
        ref_model = attrs.get("ref_model", getattr(self.instance, "ref_model", ""))

        if ref_id is not None and not (ref_model or "").strip():
            raise serializers.ValidationError({"ref_model": "ref_model is required when ref_id is provided."})

        return attrs


class DetectiveBoardLinkSerializer(serializers.ModelSerializer):
    source_id = serializers.IntegerField(write_only=True, required=True)
    target_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = DetectiveBoardLink
        fields = (
            "id",
            "board",
            "source",
            "target",
            "source_id",
            "target_id",
            "label",
            "meta",
            "created_by",
            "created_at",
        )
        read_only_fields = ("id", "board", "source", "target", "created_by", "created_at")

    def validate(self, attrs):
        board = self.context.get("board")
        if board is None:
            raise serializers.ValidationError("board context is required.")

        source_id = attrs.get("source_id")
        target_id = attrs.get("target_id")

        try:
            source = DetectiveBoardItem.objects.get(id=source_id, board=board)
        except DetectiveBoardItem.DoesNotExist:
            raise serializers.ValidationError({"source_id": "Invalid source_id for this board."})

        try:
            target = DetectiveBoardItem.objects.get(id=target_id, board=board)
        except DetectiveBoardItem.DoesNotExist:
            raise serializers.ValidationError({"target_id": "Invalid target_id for this board."})

        attrs["_source_obj"] = source
        attrs["_target_obj"] = target
        return attrs

    def create(self, validated_data):
        board = self.context["board"]
        request = self.context["request"]

        source = validated_data.pop("_source_obj")
        target = validated_data.pop("_target_obj")
        validated_data.pop("source_id", None)
        validated_data.pop("target_id", None)

        link = DetectiveBoardLink.objects.create(
            board=board,
            source=source,
            target=target,
            created_by=request.user,
            **validated_data,
        )
        return link


class DetectiveBoardSerializer(serializers.ModelSerializer):
    items = DetectiveBoardItemSerializer(many=True, read_only=True)
    links = serializers.SerializerMethodField()

    class Meta:
        model = DetectiveBoard
        fields = ("id", "case", "created_by", "created_at", "updated_at", "items", "links")
        read_only_fields = fields

    def get_links(self, obj):
        qs = obj.links.all().order_by("id")
        return [
            {
                "id": l.id,
                "source": l.source_id,
                "target": l.target_id,
                "label": l.label,
                "meta": l.meta,
                "created_by": l.created_by_id,
                "created_at": l.created_at,
            }
            for l in qs
        ]


# =========================
# Step 2: Flow Serializers
# =========================

class SolveSubmitSerializer(serializers.Serializer):
    suspect_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
    )
    note = serializers.CharField(required=False, allow_blank=True, default="")


class SolveReviewSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=["approve", "reject"])
    comment = serializers.CharField(required=False, allow_blank=True, default="")


class SolveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolveRequest
        fields = (
            "id",
            "case",
            "suspect_ids",
            "note",
            "status",
            "submitted_by",
            "submitted_at",
            "reviewed_by",
            "reviewed_at",
            "review_comment",
        )
        read_only_fields = fields


class InterrogationScoreSerializer(serializers.Serializer):
    score = serializers.IntegerField(min_value=1, max_value=10)


class InterrogationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interrogation
        fields = ("id", "case", "suspect_id", "detective_score", "sergent_score", "created_at", "updated_at")
        read_only_fields = fields


class CaptainDecisionCreateSerializer(serializers.Serializer):
    decision = serializers.ChoiceField(choices=["SEND_TO_TRIAL", "RELEASE"])
    comment = serializers.CharField(required=False, allow_blank=True, default="")


class ChiefApprovalSerializer(serializers.Serializer):
    approve = serializers.BooleanField()
    comment = serializers.CharField(required=False, allow_blank=True, default="")


class CaptainDecisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaptainDecision
        fields = (
            "case",
            "decision",
            "comment",
            "decided_by",
            "decided_at",
            "chief_approved",
            "chief_by",
            "chief_at",
            "chief_comment",
        )
        read_only_fields = fields


class TrialVerdictSerializer(serializers.Serializer):
    verdict = serializers.ChoiceField(choices=["GUILTY", "INNOCENT"])
    punishment_title = serializers.CharField(required=False, allow_blank=True, default="")
    punishment_description = serializers.CharField(required=False, allow_blank=True, default="")


class TrialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trial
        fields = ("case", "verdict", "punishment_title", "punishment_description", "judged_by", "judged_at")
        read_only_fields = fields


class CaseNotificationSerializer(serializers.ModelSerializer):
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = CaseNotification
        fields = ("id", "case", "notif_type", "message", "ref_model", "ref_id", "created_at", "read_at", "is_read")
        read_only_fields = fields

    def get_is_read(self, obj):
        return obj.read_at is not None
