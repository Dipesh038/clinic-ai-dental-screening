import { useEffect, useState } from "react";

import { apiFetch } from "@/lib/api";

export type Role = "dentist" | "receptionist" | "admin";

export interface CurrentUser {
  username: string;
  role: Role;
}

export function login(username: string, password: string): Promise<CurrentUser> {
  return apiFetch<CurrentUser>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

export function getCurrentUser(): Promise<CurrentUser> {
  return apiFetch<CurrentUser>("/api/auth/me");
}

export function logout(): Promise<void> {
  return apiFetch<void>("/api/auth/logout", { method: "POST" });
}

export function useCurrentUser() {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    getCurrentUser()
      .then(setUser)
      .catch(() => setFailed(true));
  }, []);

  return { user, failed };
}
