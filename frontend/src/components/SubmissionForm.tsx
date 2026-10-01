import { useState, type FormEvent } from "react";

import { createSubmission, formatApiError } from "../api/client";

interface SubmissionFormProps {
  onCreated: () => void;
  onError: (message: string) => void;
}

export function SubmissionForm({ onCreated, onError }: SubmissionFormProps) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const trimmedTitle = title.trim();
    const trimmedContent = content.trim();
    if (!trimmedTitle || !trimmedContent) {
      onError("Title and content are required.");
      return;
    }

    setSubmitting(true);
    onError("");
    try {
      await createSubmission({ title: trimmedTitle, content: trimmedContent });
      setTitle("");
      setContent("");
      onCreated();
    } catch (error) {
      onError(formatApiError(error));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 rounded-xl border border-line bg-panel p-5 shadow-sm"
    >
      <div>
        <h2 className="text-lg font-semibold">New submission</h2>
        <p className="mt-1 text-sm text-ink/70">
          Submit a document for review. It starts as pending.
        </p>
      </div>
      <label className="block text-sm font-medium">
        Title
        <input
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          className="mt-1 w-full rounded-lg border border-line bg-white px-3 py-2 text-sm"
          placeholder="Q3 Data Science Curriculum Update"
        />
      </label>
      <label className="block text-sm font-medium">
        Content
        <textarea
          value={content}
          onChange={(event) => setContent(event.target.value)}
          rows={6}
          className="mt-1 w-full rounded-lg border border-line bg-white px-3 py-2 text-sm"
          placeholder="Document content..."
        />
      </label>
      <button
        type="submit"
        disabled={submitting}
        className="rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-white hover:bg-accent-dark disabled:opacity-60"
      >
        {submitting ? "Submitting..." : "Submit document"}
      </button>
    </form>
  );
}
