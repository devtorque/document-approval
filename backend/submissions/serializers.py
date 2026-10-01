from rest_framework import serializers

from submissions.constants import ACTION_APPROVE, ACTION_REJECT, DEMO_USERS
from submissions.models import Submission


class CreateSubmissionSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    content = serializers.CharField()

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Title cannot be blank.")
        return value

    def validate_content(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Content cannot be blank.")
        return value


class ReviewSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=[ACTION_APPROVE, ACTION_REJECT])
    reviewer_notes = serializers.CharField(required=False, allow_blank=True, default="")

    def validate(self, attrs):
        notes = attrs.get("reviewer_notes", "")
        if isinstance(notes, str):
            notes = notes.strip()
        else:
            notes = ""
        attrs["reviewer_notes"] = notes
        if attrs["action"] == ACTION_REJECT and not notes:
            raise serializers.ValidationError(
                {"reviewer_notes": "Rejection notes are required."}
            )
        return attrs


class SubmissionSerializer(serializers.ModelSerializer):
    submitter = serializers.SerializerMethodField()
    reviewer = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = [
            "id",
            "title",
            "content",
            "submitter",
            "status",
            "reviewer",
            "reviewer_notes",
            "reviewed_at",
            "created_at",
            "updated_at",
        ]

    def get_submitter(self, obj):
        return DEMO_USERS[obj.submitter_id]

    def get_reviewer(self, obj):
        if not obj.reviewer_id:
            return None
        return DEMO_USERS.get(obj.reviewer_id)
