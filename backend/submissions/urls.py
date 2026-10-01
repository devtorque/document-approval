from django.urls import path

from submissions.views import (
    SubmissionDetailView,
    SubmissionListCreateView,
    SubmissionReviewView,
)

urlpatterns = [
    path("submissions/", SubmissionListCreateView.as_view(), name="submission-list"),
    path(
        "submissions/<uuid:pk>/",
        SubmissionDetailView.as_view(),
        name="submission-detail",
    ),
    path(
        "submissions/<uuid:pk>/review/",
        SubmissionReviewView.as_view(),
        name="submission-review",
    ),
]
