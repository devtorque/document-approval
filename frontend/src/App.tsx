import { useCallback, useEffect, useState } from "react";

import { formatApiError, listSubmissions, setDemoUser } from "./api/client";
import { ErrorBanner } from "./components/ErrorBanner";
import { ReviewPanel } from "./components/ReviewPanel";
import { SubmissionForm } from "./components/SubmissionForm";
import { SubmissionList } from "./components/SubmissionList";
import { UserSwitcher } from "./components/UserSwitcher";
import { USERS, type DemoUserId, type Submission, type SubmissionStatus } from "./types";

type StatusFilter = "all" | SubmissionStatus;

export default function App() {
  const [activeUserId, setActiveUserId] = useState<DemoUserId>("alice");
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");

  const activeUser = USERS[activeUserId];

  const refresh = useCallback(async (mode: "initial" | "silent" = "silent") => {
    if (mode === "initial") {
      setLoading(true);
    }
    try {
      const response = await listSubmissions();
      setSubmissions(response.data);
    } catch (requestError) {
      setError(formatApiError(requestError));
      setSubmissions([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    setDemoUser(activeUser.id);
    setStatusFilter("all");
    setError("");
    void refresh("initial");
  }, [activeUser.id, refresh]);

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <header className="mb-8">
        <div className="grid items-start gap-4 sm:grid-cols-[minmax(0,1fr)_auto]">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.16em] text-accent">
              Document approval
            </p>
            <h1 className="mt-1 text-3xl font-semibold tracking-tight">Review queue</h1>
          </div>
          <UserSwitcher activeUserId={activeUserId} onChange={setActiveUserId} />
        </div>
        <p className="mt-2 max-w-xl text-sm leading-6 text-ink/70">
          <span className="block h-6">Signed in as {activeUser.name}.</span>
          <span className="block">
            The browser sends only{" "}
            <code className="rounded bg-white px-1">X-Demo-User</code>; the server
            assigns the role.
          </span>
        </p>
      </header>

      <div className="mb-4">
        {error ? (
          <ErrorBanner message={error} />
        ) : (
          <p className="flex h-11 items-center text-sm text-ink/70" aria-live="polite">
            {loading ? "Loading submissions..." : ""}
          </p>
        )}
      </div>

      <div key={activeUser.id} className="space-y-6">
        {activeUser.role === "submitter" ? (
          <>
            <SubmissionForm onCreated={() => void refresh("silent")} onError={setError} />
            <SubmissionList submissions={submissions} />
          </>
        ) : (
          <ReviewPanel
            submissions={submissions}
            statusFilter={statusFilter}
            onFilterChange={setStatusFilter}
            onReview={() => void refresh("silent")}
            onError={setError}
          />
        )}
      </div>
    </div>
  );
}
