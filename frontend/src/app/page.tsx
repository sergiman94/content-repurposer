import UploadForm from "@/components/UploadForm";

export default function Home() {
  return (
    <div className="py-8">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold text-gray-900 mb-3">
          Repurpose Your Content
        </h1>
        <p className="text-gray-500 max-w-lg mx-auto">
          Paste a transcript, enter a YouTube URL, or upload a video/audio file.
          Get a blog post, Twitter thread, LinkedIn post, and newsletter section
          in seconds.
        </p>
      </div>
      <UploadForm />
    </div>
  );
}
