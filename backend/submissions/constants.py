STATUS_PENDING = "pending"
STATUS_APPROVED = "approved"
STATUS_REJECTED = "rejected"

STATUS_CHOICES = [
    (STATUS_PENDING, "Pending"),
    (STATUS_APPROVED, "Approved"),
    (STATUS_REJECTED, "Rejected"),
]

KNOWN_STATUSES = {STATUS_PENDING, STATUS_APPROVED, STATUS_REJECTED}

ROLE_SUBMITTER = "submitter"
ROLE_REVIEWER = "reviewer"

ACTION_APPROVE = "approve"
ACTION_REJECT = "reject"

# Server-side demo identities. The client sends only an id via X-Demo-User.
# The role is never accepted from the request body or header value beyond the id lookup.
DEMO_USERS = {
    "alice": {
        "id": "alice",
        "name": "Alice Submitter",
        "email": "alice@springboard.com",
        "role": ROLE_SUBMITTER,
    },
    "bob": {
        "id": "bob",
        "name": "Bob Reviewer",
        "email": "bob@springboard.com",
        "role": ROLE_REVIEWER,
    },
    # Internal-only identity used by visibility tests. Not exposed in the UI.
    "carol": {
        "id": "carol",
        "name": "Carol Submitter",
        "email": "carol@springboard.com",
        "role": ROLE_SUBMITTER,
    },
}
