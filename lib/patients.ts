import { apiFetch } from "@/lib/api";

export type Gender = "male" | "female" | "other";

export interface Patient {
  id: string;
  name: string;
  dob: string;
  gender: Gender;
  contact: string;
  notes: string;
}

export type PatientInput = {
  name: string;
  dob: string;
  gender: Gender;
  contact: string;
  notes: string;
};

export function listPatients(): Promise<Patient[]> {
  return apiFetch<Patient[]>("/api/patients");
}

export function createPatient(input: PatientInput): Promise<Patient> {
  return apiFetch<Patient>("/api/patients", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function getPatient(id: string): Promise<Patient> {
  return apiFetch<Patient>(`/api/patients/${id}`);
}

export function updatePatient(id: string, input: Partial<PatientInput>): Promise<Patient> {
  return apiFetch<Patient>(`/api/patients/${id}`, {
    method: "PUT",
    body: JSON.stringify(input),
  });
}

export function deletePatient(id: string): Promise<void> {
  return apiFetch<void>(`/api/patients/${id}`, { method: "DELETE" });
}
