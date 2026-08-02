import { HTMLAttributes } from "react";

export function Card({ className = "", ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={`rounded-lg border border-border bg-background p-6 shadow-sm ${className}`.trim()}
      {...props}
    />
  );
}
