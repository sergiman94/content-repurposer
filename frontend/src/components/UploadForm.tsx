"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createJob, uploadFile } from "@/lib/api";

type Tab = "text" | "url" | "file";

export default function UploadForm() {
  const router = useRouter();
  const [tab, setTab] = useState<Tab>("text");
  const [text, setText] = useState("");
  const [url, setUrl] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    setError("");
    setLoading(true);

    try {
      let result: { job_id: string };

      if (tab === "text") {
        if (text.trim().length < 50) {
          setError("Text must be at least 50 characters.");
          setLoading(false);
          return;
        }
        result = await createJob("text", text);
      } else if (tab === "url") {
        if (!url.trim()) {
          setError("Please enter a URL.");
          setLoading(false);
          return;
        }
        const inputType = url.includes("vimeo.com") ? "vimeo_url" : "youtube_url";
        result = await createJob(inputType, url);
      } else {
        if (!file) {
          setError("Please select a file.");
          setLoading(false);
          return;
        }
        const inputType = file.type.startsWith("video/") ? "video" : "audio";
        result = await uploadFile(file, inputType);
      }

      router.push(`/jobs/${result.job_id}`);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Something went wrong");
      setLoading(false);
    }
  };

  const tabs: { key: Tab; label: string }[] = [
    { key: "text", label: "Paste Text" },
    { key: "url", label: "Enter URL" },
    { key: "file", label: "Upload File" },
  ];

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* Tabs */}
      <div className="flex border-b border-gray-200 mb-6">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => { setTab(t.key); setError(""); }}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              tab === t.key
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="space-y-4">
        {tab === "text" && (
          <div>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste your transcript, article, or any long-form content here..."
              className="w-full h-64 p-4 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            />
            <p className="text-xs text-gray-400 mt-1 text-right">
              {text.length} characters {text.length < 50 && text.length > 0 && "(min 50)"}
            </p>
          </div>
        )}

        {tab === "url" && (
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://youtube.com/watch?v=... or https://vimeo.com/..."
            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
          />
        )}

        {tab === "file" && (
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
            <input
              type="file"
              accept="video/*,audio/*,.mp3,.mp4,.wav,.m4a,.webm,.ogg"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="hidden"
              id="file-upload"
            />
            <label
              htmlFor="file-upload"
              className="cursor-pointer text-sm text-gray-600"
            >
              {file ? (
                <span className="text-blue-600 font-medium">{file.name} ({(file.size / 1024 / 1024).toFixed(1)} MB)</span>
              ) : (
                <>
                  <span className="text-blue-600 font-medium">Click to upload</span>
                  {" "}or drag and drop
                  <br />
                  <span className="text-xs text-gray-400">
                    MP4, MP3, WAV, WebM up to 500MB
                  </span>
                </>
              )}
            </label>
          </div>
        )}

        {error && (
          <p className="text-red-600 text-sm">{error}</p>
        )}

        <button
          onClick={handleSubmit}
          disabled={loading}
          className="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? "Processing..." : "Repurpose Content"}
        </button>
      </div>
    </div>
  );
}
