from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from submissions.models import Submission


class SubmissionAPITests(APITestCase):
    def setUp(self):
        self.list_url = reverse("submission-list")

    def as_user(self, user_id):
        self.client.credentials(HTTP_X_DEMO_USER=user_id)

    def create_submission(self, user_id="alice", title="Curriculum update", content="Module notes"):
        self.as_user(user_id)
        response = self.client.post(
            self.list_url,
            {"title": title, "content": content},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response

    def test_missing_demo_user_returns_401(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_demo_user_returns_401(self):
        self.as_user("mallory")
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_valid_submission_creation_returns_201(self):
        response = self.create_submission(
            title="Q3 Data Science Curriculum Update",
            content="Document content",
        )
        self.assertEqual(response.data["title"], "Q3 Data Science Curriculum Update")
        self.assertEqual(response.data["submitter"]["id"], "alice")
        self.assertEqual(response.data["reviewer"], None)

    def test_new_submissions_start_as_pending(self):
        response = self.create_submission()
        self.assertEqual(response.data["status"], "pending")
        self.assertEqual(response.data["reviewer_notes"], "")
        self.assertIsNone(response.data["reviewed_at"])

    def test_missing_title_returns_400(self):
        self.as_user("alice")
        response = self.client.post(
            self.list_url,
            {"content": "Body only"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_content_returns_400(self):
        self.as_user("alice")
        response = self.client.post(
            self.list_url,
            {"title": "Title only"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_whitespace_only_title_returns_400(self):
        self.as_user("alice")
        response = self.client.post(
            self.list_url,
            {"title": "   ", "content": "Real content"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        blank_content = self.client.post(
            self.list_url,
            {"title": "Real title", "content": " \n "},
            format="json",
        )
        self.assertEqual(blank_content.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reviewer_cannot_create_submissions(self):
        self.as_user("bob")
        response = self.client.post(
            self.list_url,
            {"title": "Should fail", "content": "Reviewers do not submit"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Submission.objects.count(), 0)

    def test_submitter_sees_only_own_submissions(self):
        alice = self.create_submission(user_id="alice", title="Alice doc", content="A")
        self.create_submission(user_id="carol", title="Carol doc", content="C")

        self.as_user("alice")
        listing = self.client.get(self.list_url)
        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        self.assertEqual(len(listing.data), 1)
        self.assertEqual(listing.data[0]["id"], alice.data["id"])

    def test_reviewer_sees_all_submissions_and_can_filter_by_status(self):
        pending = self.create_submission(title="Pending doc", content="P")
        approved = self.create_submission(title="Approved doc", content="A")
        self.as_user("bob")
        review = self.client.post(
            reverse("submission-review", args=[approved.data["id"]]),
            {"action": "approve"},
            format="json",
        )
        self.assertEqual(review.status_code, status.HTTP_200_OK)

        self.as_user("bob")
        all_items = self.client.get(self.list_url)
        self.assertEqual(len(all_items.data), 2)

        pending_only = self.client.get(self.list_url, {"status": "pending"})
        self.assertEqual(len(pending_only.data), 1)
        self.assertEqual(pending_only.data[0]["id"], pending.data["id"])

        unknown = self.client.get(self.list_url, {"status": "archived"})
        self.assertEqual(len(unknown.data), 2)

    def test_submitter_cannot_access_another_users_detail(self):
        carol = self.create_submission(user_id="carol", title="Carol private", content="Secret")
        self.as_user("alice")
        response = self.client.get(reverse("submission-detail", args=[carol.data["id"]]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.as_user("bob")
        reviewer_view = self.client.get(reverse("submission-detail", args=[carol.data["id"]]))
        self.assertEqual(reviewer_view.status_code, status.HTTP_200_OK)
        self.assertEqual(reviewer_view.data["title"], "Carol private")

    def test_reviewer_can_approve_pending_submission(self):
        created = self.create_submission()
        self.as_user("bob")
        response = self.client.post(
            reverse("submission-review", args=[created.data["id"]]),
            {"action": "approve"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "approved")
        self.assertEqual(response.data["reviewer"]["id"], "bob")
        self.assertIsNotNone(response.data["reviewed_at"])

    def test_rejection_without_notes_returns_400(self):
        created = self.create_submission()
        self.as_user("bob")
        response = self.client.post(
            reverse("submission-review", args=[created.data["id"]]),
            {"action": "reject"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        whitespace = self.client.post(
            reverse("submission-review", args=[created.data["id"]]),
            {"action": "reject", "reviewer_notes": "   "},
            format="json",
        )
        self.assertEqual(whitespace.status_code, status.HTTP_400_BAD_REQUEST)
        created_row = Submission.objects.get(pk=created.data["id"])
        self.assertEqual(created_row.status, "pending")

    def test_rejection_with_notes_succeeds(self):
        created = self.create_submission()
        self.as_user("bob")
        notes = "Please specify the prerequisites for Module 4."
        response = self.client.post(
            reverse("submission-review", args=[created.data["id"]]),
            {"action": "reject", "reviewer_notes": notes},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "rejected")
        self.assertEqual(response.data["reviewer_notes"], notes)
        self.assertEqual(response.data["reviewer"]["id"], "bob")
        self.assertIsNotNone(response.data["reviewed_at"])

    def test_terminal_submissions_cannot_be_reviewed_again(self):
        created = self.create_submission()
        self.as_user("bob")
        review_url = reverse("submission-review", args=[created.data["id"]])
        approved = self.client.post(review_url, {"action": "approve"}, format="json")
        self.assertEqual(approved.status_code, status.HTTP_200_OK)

        again = self.client.post(
            review_url,
            {"action": "reject", "reviewer_notes": "Changed my mind"},
            format="json",
        )
        self.assertEqual(again.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Submission.objects.get(pk=created.data["id"]).status, "approved")

        rejected = self.create_submission(title="Reject me", content="Needs work")
        reject_url = reverse("submission-review", args=[rejected.data["id"]])
        self.as_user("bob")
        first = self.client.post(
            reject_url,
            {"action": "reject", "reviewer_notes": "Incomplete"},
            format="json",
        )
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        second = self.client.post(reject_url, {"action": "approve"}, format="json")
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_review_action_and_submitter_review_attempts(self):
        created = self.create_submission()
        self.as_user("bob")
        invalid = self.client.post(
            reverse("submission-review", args=[created.data["id"]]),
            {"action": "archive"},
            format="json",
        )
        self.assertEqual(invalid.status_code, status.HTTP_400_BAD_REQUEST)

        self.as_user("alice")
        forbidden = self.client.post(
            reverse("submission-review", args=[created.data["id"]]),
            {"action": "approve"},
            format="json",
        )
        self.assertEqual(forbidden.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Submission.objects.get(pk=created.data["id"]).status, "pending")
