import { apiFetch } from "@/lib/api";
import { VisitImage } from "@/lib/visits";

export interface BoundingBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface Detection {
  class_id: number;
  disease_name: string;
  confidence: number;
  box: BoundingBox;
}

export interface Prediction {
  id: string;
  image_id: string;
  detections: Detection[];
  latency_ms: number;
  created_at: string;
}

export interface CorrectionItem {
  class_id: number;
  disease_name: string;
  box: BoundingBox;
}

export interface Correction {
  id: string;
  image_id: string;
  corrections: CorrectionItem[];
  created_at: string;
}

export function getImage(imageId: string): Promise<VisitImage> {
  return apiFetch<VisitImage>(`/api/images/${imageId}`);
}

export function getLatestPrediction(imageId: string): Promise<Prediction> {
  return apiFetch<Prediction>(`/api/images/${imageId}/predictions/latest`);
}

export function getLatestCorrections(imageId: string): Promise<Correction> {
  return apiFetch<Correction>(`/api/images/${imageId}/corrections/latest`);
}

export function saveCorrections(imageId: string, corrections: CorrectionItem[]): Promise<Correction> {
  return apiFetch<Correction>(`/api/images/${imageId}/corrections`, {
    method: "POST",
    body: JSON.stringify({ corrections }),
  });
}

export function markImageReviewed(imageId: string): Promise<VisitImage> {
  return apiFetch<VisitImage>(`/api/images/${imageId}/mark-reviewed`, {
    method: "POST",
  });
}
