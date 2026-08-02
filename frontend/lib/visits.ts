import { apiFetch } from "@/lib/api";

export interface Visit {
  id: string;
  patient_id: string;
  date: string;
  complaint: string;
  notes: string;
}

export interface VisitImage {
  id: string;
  visit_id: string;
  image_url: string;
  top_prediction: string | null;
  reviewed_at: string | null;
}

export type VisitInput = {
  date: string;
  complaint: string;
  notes: string;
};

export function listVisits(patientId: string): Promise<Visit[]> {
  return apiFetch<Visit[]>(`/api/patients/${patientId}/visits`);
}

export function createVisit(patientId: string, input: VisitInput): Promise<Visit> {
  return apiFetch<Visit>(`/api/patients/${patientId}/visits`, {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function getVisit(visitId: string): Promise<Visit> {
  return apiFetch<Visit>(`/api/visits/${visitId}`);
}

export function updateVisit(visitId: string, input: Partial<VisitInput>): Promise<Visit> {
  return apiFetch<Visit>(`/api/visits/${visitId}`, {
    method: "PUT",
    body: JSON.stringify(input),
  });
}

export function uploadVisitImage(visitId: string, file: File): Promise<VisitImage> {
  const formData = new FormData();
  formData.append("file", file);

  return apiFetch<VisitImage>(`/api/visits/${visitId}/images`, {
    method: "POST",
    body: formData,
  });
}
