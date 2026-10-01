import type { Submission } from "../types";
import { StatusBadge } from "./StatusBadge";

export function SubmissionList({ submissions }: { submissions: Submission[] }) {
  if (submissions.length === 0) {
    return (
      <p className="rounded-xl border border-dashed border-line bg-panel px-5 py-8 text-center text-sm text-ink/70">
        No submissions yet. Create one to start the review workflow.
      </p>
    );
  }

  return (
    <ul className="space-y-3">
      {submissions.map((submission) => (
        <li
          key={submission.id}
          className="rounded-xl border border-line bg-panel p-5 shadow-sm"
        >
          <div className="flex items-start justify-between gap-3">
            <h3 className="text-base font-semibold">{submission.title}</h3>
            <StatusBadge status={submission.status} />
          </div>
          <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-ink/80">
            {submission.content}
          </p>
          {submission.status === "rejected" && submission.reviewer_notes && (
            <div className="mt-4 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-900">
              <p className="font-semibold">
                Reviewer feedback
                {submission.reviewer ? ` from ${submission.reviewer.name}` : ""}
              </p>
              <p className="mt-1">{submission.reviewer_notes}</p>
            </div>
          )}
          {submission.status === "approved" && submission.reviewer && (
            <p className="mt-4 text-sm text-emerald-800">
              Approved by {submission.reviewer.name}.
            </p>
          )}
        </li>
      ))}
    </ul>
  );
}
