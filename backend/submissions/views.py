from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from submissions.constants import (
    ACTION_APPROVE,
    ACTION_REJECT,
    KNOWN_STATUSES,
    ROLE_REVIEWER,
    ROLE_SUBMITTER,
    STATUS_APPROVED,
    STATUS_PENDING,
    STATUS_REJECTED,
)
from submissions.models import Submission
from submissions.serializers import (
    CreateSubmissionSerializer,
    ReviewSerializer,
    SubmissionSerializer,
)


class SubmissionListCreateView(APIView):
    def get(self, request):
        user = request.demo_user
        queryset = Submission.objects.all()
        if user["role"] == ROLE_SUBMITTER:
            queryset = queryset.filter(submitter_id=user["id"])

        status_filter = (
            request.query_params.get("status", "")
            .strip()
            .lower()
        )
        if status_filter in KNOWN_STATUSES:
            queryset = queryset.filter(status=status_filter)

        serializer = SubmissionSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        user = request.demo_user
        if user["role"] != ROLE_SUBMITTER:
            return Response(
                {"detail": "Only submitters can create submissions."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = CreateSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        submission = Submission.objects.create(
            title=serializer.validated_data["title"],
            content=serializer.validated_data["content"],
            submitter_id=user["id"],
            status=STATUS_PENDING,
        )
        return Response(
            SubmissionSerializer(submission).data,
            status=status.HTTP_201_CREATED,
        )


class SubmissionDetailView(APIView):
    def get(self, request, pk):
        submission = get_object_or_404(Submission, pk=pk)
        user = request.demo_user
        if user["role"] == ROLE_SUBMITTER and submission.submitter_id != user["id"]:
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(SubmissionSerializer(submission).data)


class SubmissionReviewView(APIView):
    """Apply a pending -> approved|rejected transition.

    Review rules live here because this prototype has a single review entry
    point. If admin actions, scheduled jobs, or event consumers also review
    submissions, move this transition into a domain service.
    """

    def post(self, request, pk):
        user = request.demo_user
        if user["role"] != ROLE_REVIEWER:
            return Response(
                {"detail": "Only reviewers can review submissions."},
                status=status.HTTP_403_FORBIDDEN,
            )

        submission = get_object_or_404(Submission, pk=pk)
        if submission.status != STATUS_PENDING:
            return Response(
                {"detail": "Only pending submissions can be reviewed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action = serializer.validated_data["action"]

        if action == ACTION_APPROVE:
            submission.status = STATUS_APPROVED
            submission.reviewer_notes = ""
        elif action == ACTION_REJECT:
            submission.status = STATUS_REJECTED
            submission.reviewer_notes = serializer.validated_data["reviewer_notes"]

        submission.reviewer_id = user["id"]
        submission.reviewed_at = timezone.now()
        submission.save()
        return Response(SubmissionSerializer(submission).data)
