export type UserRole = "submitter" | "reviewer";

export type SubmissionStatus = "pending" | "approved" | "rejected";

export type DemoUserId = "alice" | "bob";

export interface User {
  id: DemoUserId;
  name: string;
  email: string;
  role: UserRole;
}

export const USERS: Record<DemoUserId, User> = {
  alice: {
    id: "alice",
    name: "Alice Submitter",
    email: "alice@example.com",
    role: "submitter",
  },
  bob: {
    id: "bob",
    name: "Bob Reviewer",
    email: "bob@example.com",
    role: "reviewer",
  },
};

export interface Submission {
  id: string;
  title: string;
  content: string;
  submitter: User;
  status: SubmissionStatus;
  reviewer: User | null;
  reviewer_notes: string;
  reviewed_at: string | null;
  created_at: string;
  updated_at: string;
}
