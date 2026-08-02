"use client";

import { ChangeEvent, useEffect, useRef, useState } from "react";
import Link from "next/link";

import { Button } from "@/components/ui/Button";
import { useToast } from "@/components/ui/Toast";
import { VisitImage, uploadVisitImage } from "@/lib/visits";

interface VisitImageUploadProps {
  patientId: string;
  visitId: string;
}

export function VisitImageUpload({ patientId, visitId }: VisitImageUploadProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const previewUrlRef = useRef<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [uploadedImage, setUploadedImage] = useState<VisitImage | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const { addToast } = useToast();

  useEffect(() => {
    return () => {
      if (previewUrlRef.current) URL.revokeObjectURL(previewUrlRef.current);
    };
  }, []);

  function clearPreviewUrl() {
    if (previewUrlRef.current) URL.revokeObjectURL(previewUrlRef.current);
    previewUrlRef.current = null;
    setPreviewUrl(null);
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0] ?? null;
    clearPreviewUrl();
    setSelectedFile(file);
    setUploadedImage(null);
    setError(null);

    if (file) {
      const nextPreviewUrl = URL.createObjectURL(file);
      previewUrlRef.current = nextPreviewUrl;
      setPreviewUrl(nextPreviewUrl);
    }
  }

  async function handleUpload() {
    if (!selectedFile) return;

    setError(null);
    setIsUploading(true);
    try {
      const image = await uploadVisitImage(visitId, selectedFile);
      setUploadedImage(image);
      setSelectedFile(null);
      clearPreviewUrl();
      if (inputRef.current) inputRef.current.value = "";
      addToast("Image uploaded successfully", "success");
    } catch {
      setError("Unable to upload image. Please choose a JPEG or PNG under 5 MB.");
      addToast("Upload failed", "error");
    } finally {
      setIsUploading(false);
    }
  }

  const displayedImageUrl = uploadedImage?.image_url ?? previewUrl;

  return (
    <section className="mt-6 border-t border-border pt-5">
      <div className="mb-3">
        <h2 className="text-base font-semibold text-foreground">Dental image</h2>
        <p className="text-sm text-text-secondary">Upload an intraoral JPEG or PNG.</p>
      </div>

      <div className="flex flex-col gap-4">
        {displayedImageUrl ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={displayedImageUrl}
            alt={uploadedImage ? "Uploaded dental image" : "Selected dental image preview"}
            className="aspect-[4/3] w-full rounded border border-border bg-surface object-cover"
          />
        ) : (
          <div className="flex aspect-[4/3] w-full items-center justify-center rounded border border-dashed border-border bg-background text-sm text-text-secondary">
            No image selected
          </div>
        )}

        <label className="flex flex-col gap-2 text-sm font-medium text-foreground">
          Image file
          <input
            ref={inputRef}
            type="file"
            accept="image/jpeg,image/png"
            onChange={handleFileChange}
            className="rounded border border-border bg-background px-3 py-2 text-sm text-foreground file:mr-3 file:rounded file:border-0 file:bg-primary file:px-3 file:py-2 file:text-sm file:font-medium file:text-white"
          />
        </label>

        {selectedFile ? (
          <p className="text-sm text-text-secondary">
            Selected {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
          </p>
        ) : null}

        {uploadedImage ? (
          <p role="status" className="text-sm text-[#2e7d32]">
            Image uploaded successfully.
          </p>
        ) : null}

        {uploadedImage?.top_prediction ? (
          <div className="flex flex-col gap-2 rounded border border-border bg-surface p-3">
            <p className="text-sm font-medium text-foreground">
              Top AI prediction: {uploadedImage.top_prediction}
            </p>
            <Link
              href={`/patients/${patientId}/visits/${visitId}/images/${uploadedImage.id}/review`}
              className="text-sm font-medium text-primary hover:underline"
            >
              Review AI detections
            </Link>
          </div>
        ) : null}

        {error ? (
          <p role="alert" className="text-sm text-[#d32f2f]">
            {error}
          </p>
        ) : null}

        <div>
          <Button type="button" onClick={handleUpload} disabled={!selectedFile || isUploading}>
            {isUploading ? "Uploading..." : "Upload Image"}
          </Button>
        </div>
      </div>
    </section>
  );
}
