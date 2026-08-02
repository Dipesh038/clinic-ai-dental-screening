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
    return (
      <div className="flex flex-1 flex-col">
        <header className="border-b border-border bg-background px-6 py-4 flex items-center justify-between">
          <div className="h-6 w-36 bg-border animate-pulse rounded"></div>
          <div className="h-8 w-20 bg-border animate-pulse rounded"></div>
        </header>
        <main className="flex-1 p-6">
          <div className="h-8 w-48 bg-border animate-pulse rounded mb-6"></div>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <Card className="flex flex-col h-32 animate-pulse bg-border"></Card>
            <Card className="flex flex-col h-32 animate-pulse bg-border"></Card>
            <Card className="flex flex-col h-32 animate-pulse bg-border"></Card>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col">
      <AppHeader user={user} />
      <main className="flex-1 p-6">
        <h1 className="text-2xl font-semibold text-foreground mb-6">
          Welcome, {user.username}
        </h1>
        
        {!stats ? (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <Card className="flex flex-col h-32 animate-pulse bg-border"></Card>
            <Card className="flex flex-col h-32 animate-pulse bg-border"></Card>
            <Card className="flex flex-col h-32 animate-pulse bg-border"></Card>
          </div>
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
              <p className={`text-4xl font-bold ${stats.pending_reviews > 0 ? 'text-[#d32f2f] dark:text-[#ef5350]' : 'text-[#2e7d32] dark:text-[#66bb6a]'}`}>
                {stats.pending_reviews}
              </p>
            </Card>
          </div>
        )}
      </main>
    </div>
  );
}
