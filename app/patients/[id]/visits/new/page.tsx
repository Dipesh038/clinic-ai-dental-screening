"use client";

import { useEffect } from "react";
import { useParams, useRouter } from "next/navigation";

import { AppHeader } from "@/components/layout/AppHeader";
import { Card } from "@/components/ui/Card";
import { VisitForm } from "@/components/visits/VisitForm";
import { useCurrentUser } from "@/lib/auth";
import { createVisit } from "@/lib/visits";

export default function NewVisitPage() {
  const router = useRouter();
  const params = useParams<{ id: string }>();
  const { user, failed } = useCurrentUser();

  useEffect(() => {
    if (failed) router.replace("/login");
  }, [failed, router]);

  if (!user) {
    return null;
  }

  return (
    <div className="flex flex-1 flex-col">
      <AppHeader user={user} />
      <main className="flex-1 p-6">
        <h1 className="mb-4 text-xl font-semibold text-foreground">Add Visit</h1>
        <Card className="max-w-lg">
          <VisitForm
            submitLabel="Create Visit"
            onCancel={() => router.push(`/patients/${params.id}`)}
            onSubmit={async (input) => {
              await createVisit(params.id, input);
              router.push(`/patients/${params.id}`);
            }}
          />
        </Card>
      </main>
    </div>
  );
}
