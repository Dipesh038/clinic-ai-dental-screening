import { InputHTMLAttributes, useId } from "react";

interface TextInputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export function TextInput({ label, error, id, className = "", ...props }: TextInputProps) {
  const generatedId = useId();
  const inputId = id ?? generatedId;

  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={inputId} className="text-sm font-medium text-foreground">
        {label}
      </label>
      <input
        id={inputId}
        className={`min-h-11 rounded border px-3 py-2 text-sm text-foreground bg-surface dark:bg-[#121212] dark:placeholder-[#A0A0A0] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary ${
          error ? "border-error dark:border-error" : "border-border dark:border-[#333333]"
        } ${className}`.trim()}
        aria-invalid={error ? true : undefined}
        aria-describedby={error ? `${inputId}-error` : undefined}
        {...props}
      />
      {error ? (
        <p id={`${inputId}-error`} className="text-sm text-[#d32f2f] dark:text-error">
          {error}
        </p>
      ) : null}
    </div>
  );
}
