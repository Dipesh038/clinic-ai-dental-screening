"use client";

import { ChangeEvent, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { TrashIcon } from "lucide-react";

import { Button } from "@/components/ui/Button";
import { useToast } from "@/components/ui/Toast";
import { Role } from "@/lib/auth";
import { getLatestPrediction } from "@/lib/images";
import { VisitImage, uploadVisitImage, listVisitImages, deleteVisitImage } from "@/lib/visits";

const PREDICTION_POLL_INTERVAL_MS = 3000;
const PREDICTION_POLL_MAX_ATTEMPTS = 20; // ~60s -- AI inference on the free-tier backend can take 20-30s+

interface VisitImageUploadProps {
  patientId: string;
  visitId: string;
  role: Role;
}

export function VisitImageUpload({ patientId, visitId, role }: VisitImageUploadProps) {
  // Backend enforces the same split: receptionist can't view clinical images/AI
  // data at all; admin has read-only oversight (no upload/delete); dentist has
  // full access. Mirror it here so the UI doesn't offer actions the API will 403.
  const canView = role === "dentist" || role === "admin";
  const canManage = role === "dentist";

  if (!canView) {
    return (
      <section className="mt-6 border-t border-border pt-5">
        <h2 className="text-base font-semibold text-foreground">Dental image</h2>
        <p className="mt-1 text-sm text-text-secondary">
          Clinical images and AI review are managed by the dentist.
        </p>
      </section>
    );
  }

  return <VisitImageUploadContent patientId={patientId} visitId={visitId} canManage={canManage} />;
}

function VisitImageUploadContent({
  patientId,
  visitId,
  canManage,
}: {
  patientId: string;
  visitId: string;
  canManage: boolean;
}) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const previewUrlRef = useRef<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [uploadedImage, setUploadedImage] = useState<VisitImage | null>(null);
  const [existingImages, setExistingImages] = useState<VisitImage[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isDeletingId, setIsDeletingId] = useState<string | null>(null);
  const [analyzingIds, setAnalyzingIds] = useState<Set<string>>(new Set());
  const { addToast } = useToast();

  useEffect(() => {
    listVisitImages(visitId)
      .then(setExistingImages)
      .catch((err) => console.error("Failed to list existing images", err));
  }, [visitId]);

  useEffect(() => {
    return () => {
      if (previewUrlRef.current) URL.revokeObjectURL(previewUrlRef.current);
    };
  }, []);

  function applyPrediction(imageId: string, topPrediction: string | null) {
    setExistingImages((prev) =>
      prev.map((img) => (img.id === imageId ? { ...img, top_prediction: topPrediction } : img))
    );
    setUploadedImage((prev) =>
      prev && prev.id === imageId ? { ...prev, top_prediction: topPrediction } : prev
    );
  }

  function pollForPrediction(imageId: string) {
    setAnalyzingIds((prev) => new Set(prev).add(imageId));

    let attempts = 0;
    const stop = () => {
      setAnalyzingIds((prev) => {
        const next = new Set(prev);
        next.delete(imageId);
        return next;
      });
      clearInterval(timer);
    };

    const timer = setInterval(async () => {
      attempts += 1;
      try {
        const prediction = await getLatestPrediction(imageId);
        const top = prediction.detections.reduce<typeof prediction.detections[number] | null>(
          (best, detection) => (!best || detection.confidence > best.confidence ? detection : best),
          null
        );
        applyPrediction(imageId, top?.disease_name ?? null);
        stop();
      } catch {
        // 404 = AI analysis hasn't finished yet; keep polling until the cap.
        if (attempts >= PREDICTION_POLL_MAX_ATTEMPTS) stop();
      }
    }, PREDICTION_POLL_INTERVAL_MS);
  }

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
      setExistingImages((prev) => [image, ...prev]);
      setSelectedFile(null);
      clearPreviewUrl();
      if (inputRef.current) inputRef.current.value = "";
      addToast("Image uploaded successfully", "success");
      pollForPrediction(image.id);
    } catch {
      setError("Unable to upload image. Please choose a JPEG or PNG under 5 MB.");
      addToast("Upload failed", "error");
    } finally {
      setIsUploading(false);
    }
  }

  async function handleDelete(imageId: string) {
    if (!confirm("Are you sure you want to delete this image?")) return;
    
    setIsDeletingId(imageId);
    try {
      await deleteVisitImage(imageId);
      setExistingImages((prev) => prev.filter((img) => img.id !== imageId));
      addToast("Image deleted successfully", "success");
    } catch {
      addToast("Failed to delete image", "error");
    } finally {
      setIsDeletingId(null);
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
        {existingImages.length > 0 && (
          <div className="flex flex-col gap-4 border-b border-border pb-4">
            <h3 className="text-sm font-semibold text-foreground">Previously Uploaded Images</h3>
            {existingImages.map((img) => (
              <div key={img.id} className="flex flex-col gap-2 rounded border border-border p-3 bg-background">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={img.image_url}
                  alt="Existing dental image"
                  className="aspect-[4/3] w-full rounded border border-border bg-background dark:bg-black object-contain"
                />
                <div className="flex items-center justify-between">
                  {analyzingIds.has(img.id) ? (
                    <span className="text-sm text-text-secondary italic">AI: Analyzing…</span>
                  ) : img.top_prediction ? (
                    <span className="text-sm font-medium text-foreground">AI: {img.top_prediction}</span>
                  ) : (
                    <span className="text-sm text-text-secondary">AI: No conditions detected</span>
                  )}
                  <div className="flex items-center gap-3">
                    <Link
                      href={`/patients/${patientId}/visits/${visitId}/images/${img.id}/review`}
                      className="text-sm font-medium text-primary hover:underline"
                    >
                      Review
                    </Link>
                    {canManage && (
                      <button
                        type="button"
                        onClick={() => handleDelete(img.id)}
                        disabled={isDeletingId === img.id}
                        className="text-[#d32f2f] dark:text-error hover:bg-error/10 p-1 rounded transition-colors disabled:opacity-50"
                        title="Delete Image"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {canManage && (
          <>
            <h3 className="text-sm font-semibold text-foreground mt-2">Upload New Image</h3>

            {displayedImageUrl ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={displayedImageUrl}
                alt={uploadedImage ? "Uploaded dental image" : "Selected dental image preview"}
                className="aspect-[4/3] w-full rounded border border-border bg-surface dark:bg-black object-contain"
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
              <p role="status" className="text-sm text-[#2e7d32] dark:text-[#66bb6a]">
                Image uploaded successfully.
              </p>
            ) : null}

            {uploadedImage && analyzingIds.has(uploadedImage.id) ? (
              <div className="flex items-center gap-2 rounded border border-border bg-background p-3">
                <p className="text-sm text-text-secondary italic">
                  Analyzing image for AI detections… this can take up to a minute.
                </p>
              </div>
            ) : uploadedImage?.top_prediction ? (
              <div className="flex flex-col gap-2 rounded border border-border bg-background p-3">
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
              <p role="alert" className="text-sm text-[#d32f2f] dark:text-error">
                {error}
              </p>
            ) : null}

            <div>
              <Button type="button" onClick={handleUpload} disabled={!selectedFile || isUploading}>
                {isUploading ? "Uploading..." : "Upload Image"}
              </Button>
            </div>
          </>
        )}
      </div>
    </section>
  );
}
