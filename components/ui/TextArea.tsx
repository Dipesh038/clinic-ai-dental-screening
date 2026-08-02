import { TextareaHTMLAttributes, useId } from "react";

interface TextAreaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label: string;
  error?: string;
}

export function TextArea({ label, error, id, className = "", ...props }: TextAreaProps) {
  const generatedId = useId();
  const textareaId = id ?? generatedId;

  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={textareaId} className="text-sm font-medium text-foreground">
        {label}
      </label>
      <textarea
        id={textareaId}
        rows={3}
        className={`rounded border px-3 py-2 text-sm text-foreground bg-surface dark:bg-[#121212] dark:placeholder-[#A0A0A0] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary dark:focus-visible:ring-[#90CAF9] ${
          error ? "border-error dark:border-error" : "border-border dark:border-[#333333]"
        } ${className}`.trim()}
        aria-invalid={error ? true : undefined}
        aria-describedby={error ? `${textareaId}-error` : undefined}
        {...props}
      />
      {error ? (
        <p id={`${textareaId}-error`} className="text-sm text-[#d32f2f] dark:text-error">
          {error}
        </p>
      ) : null}
    </div>
  );
}
