"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { AppHeader } from "@/components/layout/AppHeader";
import { Card } from "@/components/ui/Card";
import { PatientForm } from "@/components/patients/PatientForm";
import { useCurrentUser } from "@/lib/auth";
import { createPatient } from "@/lib/patients";

export default function NewPatientPage() {
  const router = useRouter();
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
        <h1 className="mb-4 text-xl font-semibold text-foreground">Add Patient</h1>
        <Card className="max-w-lg">
          <PatientForm
            submitLabel="Create Patient"
            onCancel={() => router.push("/patients")}
            onSubmit={async (input) => {
              const patient = await createPatient(input);
              router.push(`/patients/${patient.id}`);
            }}
          />
        </Card>
      </main>
    </div>
  );
}
