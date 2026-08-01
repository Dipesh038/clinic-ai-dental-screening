"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";

import { AppHeader } from "@/components/layout/AppHeader";
import { Card } from "@/components/ui/Card";
import { useCurrentUser } from "@/lib/auth";
import { Visit, getVisit } from "@/lib/visits";

export default function VisitDetailPage() {
  const router = useRouter();
  const params = useParams<{ id: string; visitId: string }>();
  const { user, failed } = useCurrentUser();
  const [visit, setVisit] = useState<Visit | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (failed) router.replace("/login");
  }, [failed, router]);

  useEffect(() => {
    if (!user) return;
    getVisit(params.visitId)
      .then(setVisit)
      .catch(() => setError("Visit not found."));
  }, [user, params.visitId]);

  if (!user) {
    return null;
  }

  return (
    <div className="flex flex-1 flex-col">
      <AppHeader user={user} />
      <main className="flex-1 p-6">
        <Link
          href={`/patients/${params.id}`}
          className="mb-4 inline-block text-sm text-primary hover:underline"
        >
          ← Back to patient
        </Link>

        {error ? <p className="text-error">{error}</p> : null}

        {!visit && !error ? <p className="text-text-secondary">Loading…</p> : null}

        {visit ? (
          <Card className="max-w-lg">
            <h1 className="mb-4 text-xl font-semibold text-foreground">{visit.complaint}</h1>
            <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 text-sm">
              <dt className="text-text-secondary">Date</dt>
              <dd className="text-foreground">{visit.date}</dd>
              <dt className="text-text-secondary">Notes</dt>
              <dd className="text-foreground">{visit.notes || "—"}</dd>
            </dl>
            <p className="mt-4 text-sm text-text-secondary">
              Image upload coming up next.
            </p>
          </Card>
        ) : null}
      </main>
    </div>
  );
}
