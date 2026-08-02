"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { AppHeader } from "@/components/layout/AppHeader";
import { Card } from "@/components/ui/Card";
import { useCurrentUser } from "@/lib/auth";
import { DashboardStats, getDashboardStats } from "@/lib/dashboard";

export default function DashboardPage() {
  const router = useRouter();
  const { user, failed } = useCurrentUser();
  const [stats, setStats] = useState<DashboardStats | null>(null);

  useEffect(() => {
    if (failed) router.replace("/login");
  }, [failed, router]);

  useEffect(() => {
    if (!user) return;
    getDashboardStats().then(setStats).catch(console.error);
  }, [user]);

  if (!user) {
    return null;
  }

  return (
    <div className="flex flex-1 flex-col">
      <AppHeader user={user} />
      <main className="flex-1 p-6">
        <h1 className="text-2xl font-semibold text-foreground mb-6">
          Welcome, {user.username}
        </h1>
        
        {!stats ? (
          <p className="text-text-secondary">Loading statistics...</p>
        ) : (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <Card className="flex flex-col">
              <h2 className="text-sm font-medium text-text-secondary uppercase tracking-wider mb-2">Total Patients</h2>
              <p className="text-4xl font-bold text-primary">{stats.total_patients}</p>
            </Card>
            
            <Card className="flex flex-col">
              <h2 className="text-sm font-medium text-text-secondary uppercase tracking-wider mb-2">Total Visits</h2>
              <p className="text-4xl font-bold text-primary">{stats.total_visits}</p>
            </Card>
            
            <Card className="flex flex-col">
              <h2 className="text-sm font-medium text-text-secondary uppercase tracking-wider mb-2">Pending Reviews</h2>
              <p className={`text-4xl font-bold ${stats.pending_reviews > 0 ? 'text-error' : 'text-success'}`}>
                {stats.pending_reviews}
              </p>
            </Card>
          </div>
        )}
      </main>
    </div>
  );
}
