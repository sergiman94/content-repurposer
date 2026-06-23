"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getJob, JobDetail } from "@/lib/api";
import JobProgress from "@/components/JobProgress";
import OutputCard from "@/components/OutputCard";
import CopyButton from "@/components/CopyButton";

const TERMINAL = ["completed", "failed"];
const POLL_MS = 2000;

export default function JobPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = params.id as string;

  const [job, setJob] = useState<JobDetail | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!jobId) return;

    let timer: ReturnType<typeof setInterval>;

    const fetchJob = async () => {
      try {
        const data = await getJob(jobId);
        setJob(data);

        if (TERMINAL.includes(data.status)) {
          clearInterval(timer);
        }
      } catch {
        setError("Failed to load job");
        clearInterval(timer);
      }
    };

    fetchJob();
    timer = setInterval(fetchJob, POLL_MS);

    return () => clearInterval(timer);
  }, [jobId]);

  if (error) {
    return (
      <div className="text-center py-20">
        <p className="text-red-600 mb-4">{error}</p>
        <button
          onClick={() => router.push("/")}
          className="text-blue-600 hover:underline"
        >
          Go back
        </button>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="text-center py-20 text-gray-500">Loading...</div>
    );
  }

  const isProcessing = !TERMINAL.includes(job.status);
  const isCompleted = job.status === "completed";
  const isFailed = job.status === "failed";

  // Build "copy all" text
  const allText = [
    job.outputs?.blog_post && `## Blog Post\n\n${job.outputs.blog_post}`,
    job.outputs?.twitter_thread &&
      `## Twitter Thread\n\n${job.outputs.twitter_thread.join("\n\n---\n\n")}`,
    job.outputs?.linkedin_post &&
      `## LinkedIn Post\n\n${job.outputs.linkedin_post}`,
    job.outputs?.newsletter_section &&
      `## Newsletter\n\n${job.outputs.newsletter_section}`,
  ]
    .filter(Boolean)
    .join("\n\n---\n\n");

  return (
    <div className="py-6 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Job Results</h1>
          <p className="text-sm text-gray-500 mt-1">
            {job.input_type} &middot; {new Date(job.created_at).toLocaleString()}
          </p>
        </div>
        {isCompleted && allText && <CopyButton text={allText} />}
      </div>

      {/* Progress */}
      {isProcessing && (
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <JobProgress status={job.status} />
          <p className="text-center text-sm text-gray-500 mt-4">
            Processing your content... This usually takes 15-30 seconds.
          </p>
        </div>
      )}

      {/* Error */}
      {isFailed && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="font-semibold text-red-700 mb-2">Processing Failed</h2>
          <p className="text-red-600 text-sm">{job.error}</p>
          <button
            onClick={() => router.push("/")}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
          >
            Try Again
          </button>
        </div>
      )}

      {/* Outputs */}
      {isCompleted && job.outputs && (
        <div className="grid grid-cols-1 gap-6">
          <OutputCard title="Blog Post" content={job.outputs.blog_post} />
          <OutputCard
            title="Twitter/X Thread"
            content={job.outputs.twitter_thread}
            type="tweets"
          />
          <OutputCard title="LinkedIn Post" content={job.outputs.linkedin_post} />
          <OutputCard
            title="Newsletter Section"
            content={job.outputs.newsletter_section}
          />
        </div>
      )}

      {/* Token usage */}
      {isCompleted && job.token_usage && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-sm text-gray-500">
          <span className="font-medium">Usage:</span>{" "}
          {job.token_usage.total_tokens.toLocaleString()} tokens
          &middot; ${job.token_usage.estimated_cost_usd.toFixed(4)} estimated cost
        </div>
      )}
    </div>
  );
}
