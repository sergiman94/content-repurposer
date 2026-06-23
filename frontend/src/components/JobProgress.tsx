"use client";

const STEPS = [
  { key: "resolve_input", label: "Input" },
  { key: "transcribe", label: "Transcribe" },
  { key: "analyze", label: "Analyze" },
  { key: "gen_blog", label: "Blog" },
  { key: "gen_twitter", label: "Twitter" },
  { key: "gen_linkedin", label: "LinkedIn" },
  { key: "gen_newsletter", label: "Newsletter" },
  { key: "completed", label: "Done" },
];

function getStepIndex(status: string): number {
  const idx = STEPS.findIndex((s) => s.key === status);
  return idx >= 0 ? idx : 0;
}

export default function JobProgress({ status }: { status: string }) {
  const currentIdx = getStepIndex(status);
  const isFailed = status === "failed";

  return (
    <div className="w-full">
      <div className="flex items-center justify-between">
        {STEPS.map((step, i) => {
          const isActive = i === currentIdx && !isFailed;
          const isDone = i < currentIdx;

          return (
            <div key={step.key} className="flex items-center flex-1 last:flex-none">
              <div className="flex flex-col items-center">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium transition-colors ${
                    isDone
                      ? "bg-green-500 text-white"
                      : isActive
                      ? "bg-blue-500 text-white animate-pulse"
                      : "bg-gray-200 text-gray-500"
                  }`}
                >
                  {isDone ? "\u2713" : i + 1}
                </div>
                <span
                  className={`mt-1 text-xs ${
                    isDone || isActive ? "text-gray-900 font-medium" : "text-gray-400"
                  }`}
                >
                  {step.label}
                </span>
              </div>
              {i < STEPS.length - 1 && (
                <div
                  className={`flex-1 h-0.5 mx-2 mt-[-12px] ${
                    isDone ? "bg-green-500" : "bg-gray-200"
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
      {isFailed && (
        <p className="text-red-600 text-sm mt-3 text-center">
          Processing failed. You can retry the job.
        </p>
      )}
    </div>
  );
}
