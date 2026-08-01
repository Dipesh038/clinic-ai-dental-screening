"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/Button";
import { TextArea } from "@/components/ui/TextArea";
import { TextInput } from "@/components/ui/TextInput";
import { VisitInput } from "@/lib/visits";

interface VisitFormProps {
  initialValues?: VisitInput;
  submitLabel: string;
  onSubmit: (input: VisitInput) => Promise<void>;
  onCancel: () => void;
}

const EMPTY_VALUES: VisitInput = {
  date: new Date().toISOString().slice(0, 10),
  complaint: "",
  notes: "",
};

export function VisitForm({
  initialValues = EMPTY_VALUES,
  submitLabel,
  onSubmit,
  onCancel,
}: VisitFormProps) {
  const [values, setValues] = useState<VisitInput>(initialValues);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await onSubmit(values);
    } catch {
      setError("Unable to save visit. Please check the details and try again.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
      <TextInput
        label="Visit date"
        type="date"
        required
        value={values.date}
        onChange={(e) => setValues({ ...values, date: e.target.value })}
      />
      <TextInput
        label="Chief complaint"
        required
        value={values.complaint}
        onChange={(e) => setValues({ ...values, complaint: e.target.value })}
      />
      <TextArea
        label="Notes"
        value={values.notes}
        onChange={(e) => setValues({ ...values, notes: e.target.value })}
      />
      {error ? (
        <p role="alert" className="text-sm text-error">
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
