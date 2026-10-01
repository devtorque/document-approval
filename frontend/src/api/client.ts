import axios from "axios";

import type { Submission } from "../types";

const api = axios.create({
  baseURL: "http://localhost:8000/api",
});

export const setDemoUser = (userId: string) => {
  api.defaults.headers.common["X-Demo-User"] = userId;
};

export const createSubmission = (data: { title: string; content: string }) =>
  api.post<Submission>("/submissions/", data);

export const listSubmissions = () => api.get<Submission[]>("/submissions/");

export const reviewSubmission = (
  id: string,
  data: {
    action: "approve" | "reject";
    reviewer_notes?: string;
  },
) => api.post<Submission>(`/submissions/${id}/review/`, data);

export function formatApiError(error: unknown): string {
  if (!axios.isAxiosError(error)) {
    return "Something went wrong. Please try again.";
  }

  const data = error.response?.data;
  if (!data) {
    return "The API is unreachable. Start the Django server on port 8000.";
  }
  if (typeof data.detail === "string") {
    return data.detail;
  }
  if (typeof data === "object") {
    const parts = Object.entries(data as Record<string, unknown>).map(
      ([field, value]) => {
        const message = Array.isArray(value) ? value.join(" ") : String(value);
        return `${field}: ${message}`;
      },
    );
    if (parts.length > 0) {
      return parts.join(" ");
    }
  }
  return "Request failed.";
}

export default api;
