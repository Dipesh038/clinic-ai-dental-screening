"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/Button";
import { Select } from "@/components/ui/Select";
import { TextArea } from "@/components/ui/TextArea";
import { TextInput } from "@/components/ui/TextInput";
import { Gender, PatientInput } from "@/lib/patients";

interface PatientFormProps {
  initialValues?: PatientInput;
  submitLabel: string;
  onSubmit: (input: PatientInput) => Promise<void>;
  onCancel: () => void;
}

const EMPTY_VALUES: PatientInput = {
  name: "",
  dob: "",
  gender: "female",
  contact: "",
  notes: "",
};

export function PatientForm({
  initialValues = EMPTY_VALUES,
  submitLabel,
  onSubmit,
  onCancel,
}: PatientFormProps) {
  const [values, setValues] = useState<PatientInput>(initialValues);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await onSubmit(values);
    } catch {
      setError("Unable to save patient. Please check the details and try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
      <TextInput
        label="Full name"
        required
        value={values.name}
        onChange={(e) => setValues({ ...values, name: e.target.value })}
      />
      <TextInput
        label="Date of birth"
        type="date"
        required
        value={values.dob}
        onChange={(e) => setValues({ ...values, dob: e.target.value })}
      />
      <Select
        label="Gender"
        value={values.gender}
        onChange={(e) => setValues({ ...values, gender: e.target.value as Gender })}
      >
        <option value="female">Female</option>
        <option value="male">Male</option>
        <option value="other">Other</option>
      </Select>
      <TextInput
        label="Contact"
        required
        placeholder="Phone or email"
        value={values.contact}
        onChange={(e) => setValues({ ...values, contact: e.target.value })}
      />
      <TextArea
        label="Notes"
        value={values.notes}
        onChange={(e) => setValues({ ...values, notes: e.target.value })}
      />
      {error ? (
        <p role="alert" className="text-sm text-[#d32f2f] dark:text-[#ef5350]">
          {error}
        </p>
      ) : null}
      <div className="mt-2 flex gap-3">
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Saving…" : submitLabel}
        </Button>
        <Button type="button" variant="ghost" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </form>
  );
}
