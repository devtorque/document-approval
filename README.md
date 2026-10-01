# Document Approval Workflow

A small document review workflow. Submitters create text submissions. Reviewers approve or reject pending submissions. Approved and rejected submissions are terminal.

## Features

- Create a submission with a title and text body.
- Submitters see only their own submissions and can read rejection notes.
- Reviewers see every submission and can filter by status in the UI.
- Approve a pending submission, or reject it with mandatory notes.
- Pending submissions are the only ones that can be reviewed.

## Tech stack

- Backend: Django 5.2, Django REST Framework, SQLite
- Frontend: React 19, TypeScript, Vite, Tailwind CSS v4, Axios
- Tests: Django `APITestCase`, plus a production frontend build for type checking

The Vite React template resolved to React 19. The UI uses the same component split the plan described for React 18.

## Backend setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The API listens on `http://localhost:8000`.

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The app listens on `http://localhost:5173`.

## Tests

From the repository root, with the backend virtualenv available:

```bash
./run_tests.sh
```

That command runs the backend API tests and `npm run build` in the frontend. The frontend step checks TypeScript and the production build. It is not a browser test suite.

## Demo identity limitation

There is no real authentication. The frontend sends:

```http
X-Demo-User: alice
```

or:

```http
X-Demo-User: bob
```

The server maps that id to a fixed user. The client never sends a role. The header is spoofable and is only a demo substitute for authentication.

| Id | Name | Role |
|---|---|---|
| alice | Alice Submitter | submitter |
| bob | Bob Reviewer | reviewer |

A third identity, Carol, exists only for backend visibility tests. She is not shown in the UI.

## API

### Create a submission

```http
POST /api/submissions/
X-Demo-User: alice
Content-Type: application/json
```

```json
{
  "title": "Q3 Data Science Curriculum Update",
  "content": "Document content..."
}
```

Only submitters can create submissions. Title and content are required and cannot be whitespace. Status always starts as `pending`. Response: `201 Created`.

### List submissions

```http
GET /api/submissions/
X-Demo-User: alice
```

Submitters see their own submissions. Reviewers see all of them.

```http
GET /api/submissions/?status=pending
```

Known statuses are `pending`, `approved`, and `rejected`. Any other value is ignored and the role-scoped list is returned. The reviewer screen filters locally after one fetch. The query parameter remains implemented and tested.

### Submission detail

```http
GET /api/submissions/{uuid}/
X-Demo-User: alice
```

A submitter who asks for someone else's submission receives `404`. Reviewers can open any submission.

### Review

```http
POST /api/submissions/{uuid}/review/
X-Demo-User: bob
Content-Type: application/json
```

Approve:

```json
{ "action": "approve" }
```

Reject:

```json
{
  "action": "reject",
  "reviewer_notes": "Please specify the prerequisites for Module 4."
}
```

Only reviewers can review. Only `pending` submissions can change. Rejection notes are mandatory. `reviewed_at` is set when the decision is saved.

## State machine

```text
pending -> approved
pending -> rejected
approved -> terminal
rejected -> terminal
```

## Data model

`Submission` stores the title, content, submitter id, status, reviewer id, reviewer notes, review timestamp, and created/updated timestamps. Names and emails are resolved from the demo user map during serialization. They are not columns on the submission table.

## Design decisions

- Demo identity lives in server-side constants. Middleware resolves `X-Demo-User` on `/api/` requests and returns `401` when the id is missing or unknown.
- DRF's default authentication and permission classes are disabled because this demo does not use Django users.
- Review transition rules live in the review view. This prototype has one review entry point. If admin actions, scheduled jobs, or event consumers also review submissions, that logic should move into a domain service.
- SQLite does not support PostgreSQL-style row locks, so the code does not call `select_for_update()`. A production PostgreSQL version would review inside a transaction that locks the row.
- CORS allows `http://localhost:5173` and `http://127.0.0.1:5173`, plus the `x-demo-user` header, so the browser preflight succeeds.

## Two-hour trade-offs

- Demo identity instead of JWT or OAuth.
- SQLite instead of PostgreSQL.
- Text input instead of file storage.
- No real-time updates or pagination.
- No deployment, Swagger, audit-history table, or notification worker.

## Production roadmap

- OAuth or JWT with role-based access.
- S3 or GCS presigned uploads.
- PostgreSQL row locking around review transitions.
- Audit history.
- Celery notifications.
- CI/CD and Sentry.

## AI tools used

I used AI-assisted development for scaffolding, API design review, test-case identification, debugging, and documentation review. I reviewed and adapted the generated suggestions and verified the resulting behavior with automated tests and manual browser checks.

## Loom

Loom walkthrough: add the link after recording.
