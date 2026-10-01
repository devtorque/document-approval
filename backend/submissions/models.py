import uuid

from django.db import models

from submissions.constants import STATUS_CHOICES, STATUS_PENDING


class Submission(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    submitter_id = models.CharField(max_length=50)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    reviewer_id = models.CharField(
        max_length=50,
        blank=True,
        default="",
    )
    reviewer_notes = models.TextField(blank=True, default="")
    reviewed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.status})"
