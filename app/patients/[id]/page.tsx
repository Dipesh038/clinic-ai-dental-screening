"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";

import { AppHeader } from "@/components/layout/AppHeader";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useCurrentUser } from "@/lib/auth";
import { Patient, getPatient } from "@/lib/patients";
import { Visit, listVisits } from "@/lib/visits";

export default function PatientProfilePage() {
  const router = useRouter();
  const params = useParams<{ id: string }>();
  const { user, failed } = useCurrentUser();
  const [patient, setPatient] = useState<Patient | null>(null);
  const [visits, setVisits] = useState<Visit[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (failed) router.replace("/login");
  }, [failed, router]);

  useEffect(() => {
    if (!user) return;
    getPatient(params.id)
      .then(setPatient)
      .catch(() => setError("Patient not found."));
    listVisits(params.id)
      .then(setVisits)
      .catch(() => setVisits([]));
  }, [user, params.id]);

  if (!user) {
    return null;
  }

  return (
    <div className="flex flex-1 flex-col">
      <AppHeader user={user} />
      <main className="flex-1 p-6">
        <Link href="/patients" className="mb-4 inline-block text-sm text-primary hover:underline">
          ← Back to patients
        </Link>

        {error ? <p className="text-[#d32f2f] dark:text-[#ef5350]">{error}</p> : null}

        {!patient && !error ? (
          <p className="text-text-secondary">Loading…</p>
        ) : null}

        {patient ? (
          <Card className="max-w-lg">
            <div className="mb-4 flex items-start justify-between">
              <h1 className="text-xl font-semibold text-foreground">{patient.name}</h1>
              <Link href={`/patients/${patient.id}/edit`}>
                <Button variant="ghost">Edit</Button>
              </Link>
            </div>
            <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 text-sm">
              <dt className="text-text-secondary">Date of birth</dt>
              <dd className="text-foreground">{patient.dob}</dd>
              <dt className="text-text-secondary">Gender</dt>
              <dd className="capitalize text-foreground">{patient.gender}</dd>
              <dt className="text-text-secondary">Contact</dt>
              <dd className="text-foreground">{patient.contact}</dd>
              <dt className="text-text-secondary">Notes</dt>
              <dd className="text-foreground">{patient.notes || "—"}</dd>
            </dl>
          </Card>
        ) : null}

        {patient ? (
          <div className="mt-6 max-w-lg">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-foreground">Visits</h2>
              <Link href={`/patients/${patient.id}/visits/new`}>
                <Button variant="secondary">Add Visit</Button>
              </Link>
            </div>
            {visits === null ? (
              <p className="text-text-secondary">Loading visits…</p>
            ) : visits.length === 0 ? (
              <p className="text-text-secondary">No visits recorded yet.</p>
            ) : (
              <ul className="flex flex-col gap-2">
                {visits.map((visit) => (
                  <li key={visit.id}>
                    <Link href={`/patients/${patient.id}/visits/${visit.id}`}>
                      <Card className="p-4 transition-colors hover:bg-surface">
                        <div className="flex items-center justify-between">
                          <span className="font-medium text-foreground">{visit.date}</span>
                          <span className="text-sm text-text-secondary">{visit.complaint}</span>
                        </div>
                      </Card>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </div>
        ) : null}
      </main>
    </div>
  );
}
