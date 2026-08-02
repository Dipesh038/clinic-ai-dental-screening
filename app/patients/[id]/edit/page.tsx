"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import { AppHeader } from "@/components/layout/AppHeader";
import { Card } from "@/components/ui/Card";
import { PatientForm } from "@/components/patients/PatientForm";
import { useCurrentUser } from "@/lib/auth";
import { Patient, getPatient, updatePatient } from "@/lib/patients";

export default function EditPatientPage() {
  const router = useRouter();
  const params = useParams<{ id: string }>();
  const { user, failed } = useCurrentUser();
  const [patient, setPatient] = useState<Patient | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (failed) router.replace("/login");
  }, [failed, router]);

  useEffect(() => {
    if (!user) return;
    getPatient(params.id)
      .then(setPatient)
      .catch(() => setError("Patient not found."));
  }, [user, params.id]);

  if (!user) {
    return null;
  }

  return (
    <div className="flex flex-1 flex-col">
      <AppHeader user={user} />
      <main className="flex-1 p-6">
        <h1 className="mb-4 text-xl font-semibold text-foreground">Edit Patient</h1>

        {error ? <p className="text-[#d32f2f] dark:text-[#ef5350]">{error}</p> : null}

        {patient ? (
          <Card className="max-w-lg">
            <PatientForm
              initialValues={patient}
              submitLabel="Save Changes"
              onCancel={() => router.push(`/patients/${patient.id}`)}
              onSubmit={async (input) => {
                await updatePatient(patient.id, input);
                router.push(`/patients/${patient.id}`);
              }}
            />
          </Card>
        ) : !error ? (
          <p className="text-text-secondary">Loading…</p>
        ) : null}
      </main>
    </div>
  );
}
