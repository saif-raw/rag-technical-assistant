// frontend/src/components/UploadPanel.jsx
import { useState } from "react";
import { uploadDocument } from "../api/ragApi";

export default function UploadPanel({ onUploadStart, onUploadEnd }) {
  const [progress, setProgress] = useState(0);
  const [uploading, setUploading] = useState(false);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setProgress(0);
    onUploadStart?.();

    try {
      await uploadDocument(file, setProgress);
      alert("Manual ingested successfully");
    } finally {
      setUploading(false);
      onUploadEnd?.();
      setProgress(100);
    }
  };

  return (
    <div className="border rounded-lg p-4 bg-white shadow">
      <h2 className="font-semibold mb-3">Upload Manual</h2>

      <input
        type="file"
        onChange={handleUpload}
        disabled={uploading}
        className="mb-3"
      />

      {uploading && (
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className="bg-freudenberg h-3 rounded-full transition-all"
            style={{ width: `${progress}%` }}
          />
        </div>
      )}

      {uploading && (
        <p className="text-sm mt-2 text-gray-600">
          Uploading & ingesting… {progress}%
        </p>
      )}
    </div>
  );
}
