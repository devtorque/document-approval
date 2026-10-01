import { useState } from "react";

import { reviewSubmission, formatApiError } from "../api/client";
import type { Submission, SubmissionStatus } from "../types";
import { StatusBadge } from "./StatusBadge";

type StatusFilter = "all" | SubmissionStatus;

const FILTERS: { id: StatusFilter; label: string }[] = [
  { id: "all", label: "All" },
  { id: "pending", label: "Pending" },
  { id: "approved", label: "Approved" },
  { id: "rejected", label: "Rejected" },
];

interface ReviewPanelProps {
  submissions: Submission[];
  statusFilter: StatusFilter;
  onFilterChange: (filter: StatusFilter) => void;
  onReview: () => void;
  onError: (message: string) => void;
}

export function ReviewPanel({
  submissions,
  statusFilter,
  onFilterChange,
  onReview,
  onError,
}: ReviewPanelProps) {
  const [notesById, setNotesById] = useState<Record<string, string>>({});
  const [busyId, setBusyId] = useState<string | null>(null);

  const visible =
    statusFilter === "all"
      ? submissions
      : submissions.filter((submission) => submission.status === statusFilter);

  async function decide(
    submission: Submission,
    action: "approve" | "reject",
  ) {
    const notes = (notesById[submission.id] ?? "").trim();
    setBusyId(submission.id);
    onError("");
    try {
      await reviewSubmission(submission.id, {
        action,
        reviewer_notes: action === "reject" ? notes : undefined,
      });
      setNotesById((current) => ({ ...current, [submission.id]: "" }));
      onReview();
    } catch (error) {
      onError(formatApiError(error));
    } finally {
      setBusyId(null);
    }
  }

  return (
    <section className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {FILTERS.map((filter) => (
          <button
            key={filter.id}
            type="button"
            onClick={() => onFilterChange(filter.id)}
            className={`rounded-full px-3 py-1 text-sm font-medium ${
              statusFilter === filter.id
                ? "bg-accent text-white"
                : "border border-line bg-panel text-ink"
            }`}
            aria-pressed={statusFilter === filter.id}
          >
            {filter.label}
          </button>
        ))}
      </div>

      {visible.length === 0 ? (
        <p className="rounded-xl border border-dashed border-line bg-panel px-5 py-8 text-center text-sm text-ink/70">
          No submissions in this view.
        </p>
      ) : (
        <ul className="space-y-3">
          {visible.map((submission) => {
            const pending = submission.status === "pending";
            const busy = busyId === submission.id;
            return (
              <li
                key={submission.id}
                className="rounded-xl border border-line bg-panel p-5 shadow-sm"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="text-base font-semibold">{submission.title}</h3>
                    <p className="mt-1 text-xs text-ink/60">
                      {submission.submitter.name} · {submission.submitter.email}
                    </p>
                  </div>
                  <StatusBadge status={submission.status} />
                </div>
                <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-ink/80">
                  {submission.content}
                </p>
                {submission.reviewer_notes && (
                  <p className="mt-3 text-sm text-ink/70">
                    Notes: {submission.reviewer_notes}
                  </p>
                )}
                {pending && (
                  <div className="mt-4 space-y-3">
                    <label className="block text-sm font-medium">
                      Rejection notes
                      <textarea
                        value={notesById[submission.id] ?? ""}
                        onChange={(event) =>
                          setNotesById((current) => ({
                            ...current,
                            [submission.id]: event.target.value,
                          }))
                        }
                        rows={3}
                        className="mt-1 w-full rounded-lg border border-line bg-white px-3 py-2 text-sm"
                        placeholder="Required when rejecting"
                      />
                    </label>
                    <div className="flex gap-2">
                      <button
                        type="button"
                        disabled={busy}
                        onClick={() => decide(submission, "approve")}
                        className="rounded-lg bg-emerald-700 px-3 py-2 text-sm font-semibold text-white disabled:opacity-60"
                      >
                        {busy ? "Saving..." : "Approve"}
                      </button>
                      <button
                        type="button"
                        disabled={busy}
                        onClick={() => decide(submission, "reject")}
                        className="rounded-lg bg-rose-700 px-3 py-2 text-sm font-semibold text-white disabled:opacity-60"
                      >
                        Reject
                      </button>
                    </div>
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
