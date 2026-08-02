"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { AppHeader } from "@/components/layout/AppHeader";
import { Button } from "@/components/ui/Button";
import { Table } from "@/components/ui/Table";
import { TextInput } from "@/components/ui/TextInput";
import { useCurrentUser } from "@/lib/auth";
import { Patient, listPatients } from "@/lib/patients";

export default function PatientListPage() {
  const router = useRouter();
  const { user, failed } = useCurrentUser();
  const [patients, setPatients] = useState<Patient[] | null>(null);
  const [search, setSearch] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (failed) router.replace("/login");
  }, [failed, router]);

  useEffect(() => {
    if (!user) return;
    listPatients()
      .then(setPatients)
      .catch(() => setError("Unable to load patients."));
  }, [user]);

  const filtered = useMemo(() => {
    if (!patients) return [];
    const query = search.trim().toLowerCase();
    if (!query) return patients;
    return patients.filter((p) => p.name.toLowerCase().includes(query));
  }, [patients, search]);

  if (!user) {
    return null;
  }

  return (
    <div className="flex flex-1 flex-col">
      <AppHeader user={user} />
      <main className="flex-1 p-6">
        <h1 className="mb-4 text-xl font-semibold text-foreground">Patients</h1>
        <div className="mb-6 flex items-end justify-between gap-4">
          <div className="max-w-xs flex-1">
            <TextInput
              label="Search patients"
              placeholder="Search by name…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <Link href="/patients/new">
            <Button>Add Patient</Button>
          </Link>
        </div>

        {error ? <p className="text-[#d32f2f]">{error}</p> : null}

        {patients === null && !error ? (
          <p className="text-text-secondary">Loading patients…</p>
        ) : (
          <Table>
            <thead>
              <tr className="border-b border-border">
                <th className="px-4 py-3 font-medium text-text-secondary">Name</th>
                <th className="px-4 py-3 font-medium text-text-secondary">Date of birth</th>
                <th className="px-4 py-3 font-medium text-text-secondary">Gender</th>
                <th className="px-4 py-3 font-medium text-text-secondary">Contact</th>
                <th className="px-4 py-3">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-6 text-center text-text-secondary">
                    No patients found.
                  </td>
                </tr>
              ) : (
                filtered.map((patient) => (
                  <tr key={patient.id} className="border-b border-border last:border-0">
                    <td className="px-4 py-3 text-foreground">{patient.name}</td>
                    <td className="px-4 py-3 text-foreground">{patient.dob}</td>
                    <td className="px-4 py-3 capitalize text-foreground">{patient.gender}</td>
                    <td className="px-4 py-3 text-foreground">{patient.contact}</td>
                    <td className="px-4 py-3 text-right">
                      <Link
                        href={`/patients/${patient.id}`}
                        className="text-sm font-medium text-primary hover:underline"
                      >
                        View
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </Table>
        )}
      </main>
    </div>
  );
}
