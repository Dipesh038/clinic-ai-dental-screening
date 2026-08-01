"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { AppHeader } from "@/components/layout/AppHeader";
import { CurrentUser, getCurrentUser } from "@/lib/auth";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<CurrentUser | null>(null);

  useEffect(() => {
    getCurrentUser()
      .then(setUser)
      .catch(() => router.replace("/login"));
  }, [router]);

  if (!user) {
    return null;
  }

  return (
    <div className="flex flex-1 flex-col">
      <AppHeader user={user} />
      <main className="flex-1 p-6">
        <h1 className="text-xl font-semibold text-foreground">
          Welcome, {user.username}
        </h1>
        <p className="mt-2 text-text-secondary">
          Patient and visit management coming up next.
        </p>
      </main>
    </div>
  );
}
