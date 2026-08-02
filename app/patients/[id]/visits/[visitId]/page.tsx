"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";

import { AppHeader } from "@/components/layout/AppHeader";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { VisitImageUpload } from "@/components/visits/VisitImageUpload";
import { useCurrentUser } from "@/lib/auth";
import { Patient, getPatient } from "@/lib/patients";
import { Visit, getVisit } from "@/lib/visits";

export default function VisitDetailPage() {
  const router = useRouter();
  const params = useParams<{ id: string; visitId: string }>();
  const { user, failed } = useCurrentUser();
  const [patient, setPatient] = useState<Patient | null>(null);
  const [visit, setVisit] = useState<Visit | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleDownloadReport = () => {
    window.print();
  };

  useEffect(() => {
    if (failed) router.replace("/login");
  }, [failed, router]);

  useEffect(() => {
    if (!user) return;
    getVisit(params.visitId)
      .then(setVisit)
      .catch(() => setError("Visit not found."));
    getPatient(params.id)
      .then(setPatient)
      .catch(console.error);
  }, [user, params.visitId, params.id]);

  if (!user) {
    return null;
  }

  return (
    <div className="flex flex-1 flex-col">
      <AppHeader user={user} />
      <main className="flex-1 p-6 print:p-0 print:m-0">
        <div className="print:hidden">
          <Link
            href={`/patients/${params.id}`}
            className="mb-4 inline-block text-sm text-primary hover:underline"
          >
            ← Back to patient
          </Link>

          {error ? <p className="text-[#d32f2f] dark:text-[#ef5350]">{error}</p> : null}

          {!visit && !error ? <p className="text-text-secondary">Loading…</p> : null}

          {visit ? (
            <Card className="max-w-lg">
              <div className="mb-4 flex items-center justify-between">
                <h1 className="text-xl font-semibold text-foreground">{visit.complaint}</h1>
                <Button variant="secondary" onClick={handleDownloadReport}>
                  Print / Download Report
                </Button>
              </div>
              <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 text-sm">
                <dt className="text-text-secondary">Date</dt>
                <dd className="text-foreground">{visit.date}</dd>
                <dt className="text-text-secondary">Notes</dt>
                <dd className="text-foreground">{visit.notes || "—"}</dd>
              </dl>
              <VisitImageUpload patientId={params.id} visitId={visit.id} />
            </Card>
          ) : null}
        </div>

        {/* Print Only Layout */}
        <div className="hidden print:block text-black bg-white min-h-screen p-8 max-w-[8.5in] mx-auto">
          <div className="border-b-2 border-black pb-4 mb-6">
            <h1 className="text-3xl font-bold">Clinic-AI Dental Screening</h1>
            <p className="text-gray-600 text-lg">Official Patient Report</p>
          </div>

          {patient && (
            <div className="mb-8">
              <h2 className="text-xl font-bold mb-2 border-b border-gray-300 pb-1">Patient Information</h2>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div><span className="font-semibold">Name:</span> {patient.name}</div>
                <div><span className="font-semibold">DOB:</span> {patient.dob}</div>
                <div><span className="font-semibold">Gender:</span> {patient.gender}</div>
                <div><span className="font-semibold">Contact:</span> {patient.contact}</div>
              </div>
            </div>
          )}

          {visit && (
            <div className="mb-8">
              <h2 className="text-xl font-bold mb-2 border-b border-gray-300 pb-1">Visit Information</h2>
              <div className="grid grid-cols-1 gap-2 text-sm">
                <div><span className="font-semibold">Date:</span> {visit.date}</div>
                <div><span className="font-semibold">Complaint:</span> {visit.complaint}</div>
                <div><span className="font-semibold">Notes:</span> {visit.notes || "None provided"}</div>
              </div>
            </div>
          )}
          
          <div className="mb-8">
            <h2 className="text-xl font-bold mb-2 border-b border-gray-300 pb-1">Clinical Images & Diagnoses</h2>
            <p className="text-sm italic text-gray-600 mb-4">
              Detailed AI heatmap reviews and manual dentist corrections can be viewed securely in the portal.
            </p>
          </div>

          <div className="mt-24 pt-8 border-t border-gray-400 flex justify-between items-end">
            <div>
              <p className="text-sm font-semibold mb-8">Dentist Signature</p>
              <div className="w-64 border-b border-black"></div>
            </div>
            <div className="text-right text-sm">
              <p className="font-semibold">Generated On</p>
              <p>{new Date().toLocaleDateString()}</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
