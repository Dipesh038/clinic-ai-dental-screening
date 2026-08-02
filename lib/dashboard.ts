import { apiFetch } from "@/lib/api";

export interface DashboardStats {
  total_patients: number;
  total_visits: number;
  pending_reviews: number;
}

export function getDashboardStats(): Promise<DashboardStats> {
  return apiFetch<DashboardStats>("/api/dashboard/stats");
}
