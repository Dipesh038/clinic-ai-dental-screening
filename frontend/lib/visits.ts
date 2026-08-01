import { apiFetch } from "@/lib/api";

export interface Visit {
  id: string;
  patient_id: string;
  date: string;
  complaint: string;
  notes: string;
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
