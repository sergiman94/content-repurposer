"use client";

import CopyButton from "./CopyButton";

interface OutputCardProps {
  title: string;
  content: string | string[] | null;
  type?: "text" | "tweets";
}

export default function OutputCard({
  title,
  content,
  type = "text",
}: OutputCardProps) {
  if (content === null) {
    return (
      <div className="border border-red-200 rounded-lg p-4 bg-red-50">
        <h3 className="font-semibold text-red-700 mb-2">{title}</h3>
        <p className="text-red-500 text-sm">Generation failed for this output.</p>
      </div>
    );
  }

  const copyText =
    type === "tweets" && Array.isArray(content)
      ? content.join("\n\n---\n\n")
      : (content as string);

  return (
    <div className="border border-gray-200 rounded-lg p-4 bg-white">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-gray-900">{title}</h3>
        <CopyButton text={copyText} />
      </div>

      {type === "tweets" && Array.isArray(content) ? (
        <div className="space-y-3">
          {content.map((tweet, i) => (
            <div
              key={i}
              className="p-3 bg-gray-50 rounded border border-gray-100"
            >
              <div className="flex items-start gap-2">
                <span className="text-xs text-gray-400 font-mono mt-0.5">
                  {i + 1}.
                </span>
                <p className="text-sm text-gray-800 whitespace-pre-wrap">
                  {tweet}
                </p>
              </div>
              <div className="text-right mt-1">
                <span
                  className={`text-xs ${
                    tweet.length > 280 ? "text-red-500" : "text-gray-400"
                  }`}
                >
                  {tweet.length}/280
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap">
          {content as string}
        </div>
      )}
    </div>
  );
}
