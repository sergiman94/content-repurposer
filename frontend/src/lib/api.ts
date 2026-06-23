const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface JobOutputs {
  blog_post: string | null;
  twitter_thread: string[] | null;
  linkedin_post: string | null;
  newsletter_section: string | null;
}

export interface TokenSummary {
  total_prompt_tokens: number;
  total_completion_tokens: number;
  total_tokens: number;
  estimated_cost_usd: number;
}

export interface JobDetail {
  job_id: string;
  status: string;
  input_type: string;
  outputs: JobOutputs | null;
  error: string | null;
  token_usage: TokenSummary | null;
  created_at: string;
  completed_at: string | null;
}

export interface JobListItem {
  job_id: string;
  input_type: string;
  status: string;
  error: string | null;
  created_at: string;
  completed_at: string | null;
}

export async function createJob(
  inputType: string,
  content: string
): Promise<{ job_id: string }> {
  const res = await fetch(`${API_BASE}/api/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ input_type: inputType, content }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to create job");
  }
  return res.json();
}

export async function uploadFile(
  file: File,
  inputType: "video" | "audio"
): Promise<{ job_id: string }> {
  const form = new FormData();
  form.append("file", file);
  form.append("input_type", inputType);

  const res = await fetch(`${API_BASE}/api/jobs/upload`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to upload file");
  }
  return res.json();
}

export async function getJob(jobId: string): Promise<JobDetail> {
  const res = await fetch(`${API_BASE}/api/jobs/${jobId}`);
  if (!res.ok) throw new Error("Job not found");
  return res.json();
}

export async function listJobs(
  limit = 20,
  offset = 0
): Promise<JobListItem[]> {
  const res = await fetch(
    `${API_BASE}/api/jobs?limit=${limit}&offset=${offset}`
  );
  if (!res.ok) throw new Error("Failed to list jobs");
  return res.json();
}

export async function deleteJob(jobId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/jobs/${jobId}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to delete job");
}
