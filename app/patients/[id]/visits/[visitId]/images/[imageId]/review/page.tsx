"use client";

import { MouseEvent, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";

import { AppHeader } from "@/components/layout/AppHeader";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useToast } from "@/components/ui/Toast";
import { useCurrentUser } from "@/lib/auth";
import {
  BoundingBox,
  Correction,
  CorrectionItem,
  Prediction,
  getImage,
  getLatestCorrections,
  getLatestPrediction,
  markImageReviewed,
  saveCorrections,
  getHeatmap,
} from "@/lib/images";
import { VisitImage } from "@/lib/visits";

interface ImageSize {
  width: number;
  height: number;
}

function boxStyle(box: BoundingBox, imageSize: ImageSize) {
  const { x1, y1, x2, y2 } = box;
  return {
    left: `${(x1 / imageSize.width) * 100}%`,
    top: `${(y1 / imageSize.height) * 100}%`,
    width: `${((x2 - x1) / imageSize.width) * 100}%`,
    height: `${((y2 - y1) / imageSize.height) * 100}%`,
  };
}

export default function AiReviewPage() {
  const router = useRouter();
  const params = useParams<{ id: string; visitId: string; imageId: string }>();
  const { user, failed } = useCurrentUser();
  const { addToast } = useToast();
  const [image, setImage] = useState<VisitImage | null>(null);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [correction, setCorrection] = useState<Correction | null>(null);
  const [imageSize, setImageSize] = useState<ImageSize | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Edit mode state
  const [isEditing, setIsEditing] = useState(false);
  const [activeBoxes, setActiveBoxes] = useState<CorrectionItem[]>([]);
  const [isSaving, setIsSaving] = useState(false);
  
  // Heatmap state
  const [heatmapUrl, setHeatmapUrl] = useState<string | null>(null);
  const [heatmapBoxIndex, setHeatmapBoxIndex] = useState<number | null>(null);
  const [isLoadingHeatmap, setIsLoadingHeatmap] = useState(false);

  // Drawing state
  const imgRef = useRef<HTMLImageElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [drawStart, setDrawStart] = useState<{ x: number; y: number } | null>(null);
  const [drawCurrent, setDrawCurrent] = useState<{ x: number; y: number } | null>(null);
  const [newLabel, setNewLabel] = useState("caries");

  useEffect(() => {
    if (failed) router.replace("/login");
  }, [failed, router]);

  useEffect(() => {
    if (!user) return;

    getImage(params.imageId)
      .then(setImage)
      .catch(() => setError("Image not found."));

    Promise.allSettled([
      getLatestPrediction(params.imageId),
      getLatestCorrections(params.imageId),
    ]).then(([predResult, corrResult]) => {
      const pred = predResult.status === "fulfilled" ? predResult.value : null;
      const corr = corrResult.status === "fulfilled" ? corrResult.value : null;
      setPrediction(pred);
      setCorrection(corr);
      if (corr) {
        setActiveBoxes(corr.corrections);
      } else if (pred) {
        setActiveBoxes(
          pred.detections.map((d) => ({
            class_id: d.class_id,
            disease_name: d.disease_name,
            box: { ...d.box },
          }))
        );
      }
    });
  }, [user, params.imageId]);

  if (!user) {
    return null;
  }

  const handleEditClick = () => setIsEditing(true);

  const handleCancel = () => {
    setIsEditing(false);
    // Revert changes
    if (correction) {
      setActiveBoxes(correction.corrections);
    } else if (prediction) {
      setActiveBoxes(
        prediction.detections.map((d) => ({
          class_id: d.class_id,
          disease_name: d.disease_name,
          box: { ...d.box },
        }))
      );
    } else {
      setActiveBoxes([]);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const saved = await saveCorrections(params.imageId, activeBoxes);
      setCorrection(saved);
      setIsEditing(false);
      addToast("Corrections saved successfully", "success");
    } catch {
      addToast("Failed to save corrections", "error");
    } finally {
      setIsSaving(false);
    }
  };

  const handleMarkReviewed = async () => {
    try {
      const updatedImage = await markImageReviewed(params.imageId);
      setImage(updatedImage);
      addToast("Image marked as reviewed", "success");
    } catch {
      addToast("Failed to mark as reviewed", "error");
    }
  };

  const handleDeleteBox = (index: number) => {
    setActiveBoxes((prev) => prev.filter((_, i) => i !== index));
    if (heatmapBoxIndex === index) {
      setHeatmapUrl(null);
      setHeatmapBoxIndex(null);
    }
  };

  const handleToggleHeatmap = async (index: number) => {
    if (heatmapBoxIndex === index) {
      // Toggle off
      setHeatmapUrl(null);
      setHeatmapBoxIndex(null);
      return;
    }

    // Since our backend generates heatmap based on the *prediction* index,
    // we only support heatmap for raw predictions right now (not edited ones).
    // The index corresponds to prediction.detections array.
    if (isEditing || correction) {
      addToast("Grad-CAM heatmaps are only available for raw AI predictions.", "error");
      return;
    }

    setIsLoadingHeatmap(true);
    setHeatmapBoxIndex(index);
    try {
      const url = await getHeatmap(params.imageId, index);
      setHeatmapUrl(url);
    } catch {
      addToast("Failed to load heatmap", "error");
      setHeatmapBoxIndex(null);
    } finally {
      setIsLoadingHeatmap(false);
    }
  };

  const getCoordinates = (e: MouseEvent<HTMLDivElement>) => {
    if (!imgRef.current || !imageSize) return null;
    const rect = imgRef.current.getBoundingClientRect();
    // Calculate x and y based on the natural image size
    const scaleX = imageSize.width / rect.width;
    const scaleY = imageSize.height / rect.height;
    
    return {
      x: (e.clientX - rect.left) * scaleX,
      y: (e.clientY - rect.top) * scaleY,
    };
  };

  const handleMouseDown = (e: MouseEvent<HTMLDivElement>) => {
    if (!isEditing) return;
    const coords = getCoordinates(e);
    if (coords) {
      setIsDrawing(true);
      setDrawStart(coords);
      setDrawCurrent(coords);
    }
  };

  const handleMouseMove = (e: MouseEvent<HTMLDivElement>) => {
    if (!isEditing || !isDrawing) return;
    const coords = getCoordinates(e);
    if (coords) {
      setDrawCurrent(coords);
    }
  };

  const handleMouseUp = () => {
    if (!isEditing || !isDrawing || !drawStart || !drawCurrent) {
      setIsDrawing(false);
      return;
    }
    
    const x1 = Math.min(drawStart.x, drawCurrent.x);
    const y1 = Math.min(drawStart.y, drawCurrent.y);
    const x2 = Math.max(drawStart.x, drawCurrent.x);
    const y2 = Math.max(drawStart.y, drawCurrent.y);

    if (x2 - x1 > 10 && y2 - y1 > 10) {
      setActiveBoxes((prev) => [
        ...prev,
        {
          class_id: newLabel === "caries" ? 0 : 1, // basic mapping for demo
          disease_name: newLabel,
          box: { x1, y1, x2, y2 },
        },
      ]);
    }
    
    setIsDrawing(false);
    setDrawStart(null);
    setDrawCurrent(null);
  };

  return (
    <div className="flex flex-1 flex-col">
      <AppHeader user={user} />
      <main className="flex-1 p-6">
        <Link
          href={`/patients/${params.id}/visits/${params.visitId}`}
          className="mb-4 inline-block text-sm text-primary hover:underline"
        >
          ← Back to visit
        </Link>

        {error ? <p className="text-[#d32f2f] dark:text-[#ef5350]">{error}</p> : null}
        {!image && !error ? <p className="text-text-secondary">Loading…</p> : null}

        {image ? (
          <Card className="max-w-6xl">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <h1 className="text-xl font-semibold text-foreground flex items-center gap-3">
                AI review
                {image.reviewed_at && (
                  <span className="rounded-full bg-success/10 px-2 py-0.5 text-xs font-medium text-[#2e7d32] dark:text-[#66bb6a] border border-success/20">
                    Reviewed
                  </span>
                )}
              </h1>

              <div className="flex flex-wrap items-center gap-2">
                {!isEditing && (
                  <>
                    <Button variant="ghost" onClick={handleEditClick}>
                      Edit Corrections
                    </Button>
                    {!image.reviewed_at && (
                      <Button variant="primary" onClick={handleMarkReviewed}>
                        Mark as Reviewed
                      </Button>
                    )}
                  </>
                )}
                {isEditing && (
                  <>
                    <div className="mr-4 flex items-center gap-2">
                      <label className="text-sm text-text-secondary">New box label:</label>
                      <select 
                        value={newLabel}
                        onChange={(e) => setNewLabel(e.target.value)}
                        className="rounded border border-border px-2 py-1 text-sm bg-background"
                      >
                        <option value="caries">Caries</option>
                        <option value="periodontitis">Periodontitis</option>
                      </select>
                    </div>
                    <Button variant="ghost" onClick={handleCancel}>Cancel</Button>
                    <Button variant="primary" onClick={handleSave} disabled={isSaving}>
                      {isSaving ? "Saving..." : "Save Corrections"}
                    </Button>
                  </>
                )}
              </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-[minmax(0,2fr)_minmax(320px,1fr)]">
              <div 
                className={`relative overflow-hidden rounded border border-border bg-surface ${isEditing ? 'cursor-crosshair' : ''}`}
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                onMouseLeave={handleMouseUp}
              >
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  ref={imgRef}
                  src={image.image_url}
                  alt="Dental image for AI review"
                  className="block w-full pointer-events-none select-none"
                  draggable={false}
                  onLoad={(event) =>
                    setImageSize({
                      width: event.currentTarget.naturalWidth,
                      height: event.currentTarget.naturalHeight,
                    })
                  }
                />

                {imageSize && activeBoxes.map((box, index) => (
                    <div
                      key={index}
                      className="absolute border-2 border-error bg-error/10"
                      style={boxStyle(box.box, imageSize)}
                    >
                      <span className="absolute left-0 top-0 bg-[#d32f2f] px-1 py-0.5 text-xs font-medium text-white whitespace-nowrap">
                        {box.disease_name}
                      </span>
                      {isEditing && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteBox(index);
                          }}
                          className="absolute -right-2 -top-2 flex h-5 w-5 items-center justify-center rounded-full bg-[#d32f2f] text-white hover:bg-[#b71c1c] text-xs font-bold leading-none cursor-pointer z-10"
                        >
                          ×
                        </button>
                      )}
                      {heatmapBoxIndex === index && heatmapUrl && (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img 
                          src={heatmapUrl} 
                          alt="Grad-CAM Heatmap"
                          className="absolute inset-0 w-full h-full object-cover opacity-60 mix-blend-multiply"
                        />
                      )}
                    </div>
                ))}
                
                {/* Drawing overlay */}
                {isEditing && isDrawing && drawStart && drawCurrent && imageSize && (
                   <div
                     className="absolute border-2 border-primary border-dashed bg-primary/10 pointer-events-none"
                     style={boxStyle({
                       x1: Math.min(drawStart.x, drawCurrent.x),
                       y1: Math.min(drawStart.y, drawCurrent.y),
                       x2: Math.max(drawStart.x, drawCurrent.x),
                       y2: Math.max(drawStart.y, drawCurrent.y)
                     }, imageSize)}
                   />
                )}
              </div>

              <div>
                <h2 className="mb-3 text-base font-semibold text-foreground">
                  {isEditing ? "Corrections" : "Detections"}
                </h2>
                {activeBoxes.length === 0 ? (
                  <p className="text-sm text-text-secondary">No conditions detected.</p>
                ) : (
                  <ul className="flex flex-col gap-3">
                    {activeBoxes.map((box, index) => (
                      <li key={index} className="rounded border border-border p-3">
                        <div className="flex items-center justify-between gap-3">
                          <span className="font-medium capitalize text-foreground flex items-center gap-2">
                            {box.disease_name}
                            {correction && !isEditing && (
                              <span className="text-[10px] uppercase tracking-wide bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 px-1.5 py-0.5 rounded border border-blue-200 dark:border-blue-800">
                                corrected
                              </span>
                            )}
                          </span>
                          {!isEditing && !correction && (
                             <Button 
                               variant="ghost" 
                               className="px-2 py-1 text-xs" 
                               onClick={() => handleToggleHeatmap(index)}
                               disabled={isLoadingHeatmap && heatmapBoxIndex !== index}
                             >
                               {isLoadingHeatmap && heatmapBoxIndex === index 
                                 ? "Loading..." 
                                 : heatmapBoxIndex === index 
                                   ? "Hide Heatmap" 
                                   : "Show Heatmap"}
                             </Button>
                          )}
                        </div>
                        <p className="mt-2 text-xs text-text-secondary">
                          Box: {Math.round(box.box.x1)}, {Math.round(box.box.y1)} -{" "}
                          {Math.round(box.box.x2)}, {Math.round(box.box.y2)}
                        </p>
                      </li>
                    ))}
                  </ul>
                )}
                
                {!isEditing && !correction && prediction && (
                  <p className="mt-4 text-xs text-text-secondary bg-surface p-3 rounded border border-border">
                    Showing raw AI predictions. Click &quot;Edit Corrections&quot; to modify and save changes.
                  </p>
                )}
              </div>
            </div>
          </Card>
        ) : null}
      </main>
    </div>
  );
}
