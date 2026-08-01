import { TableHTMLAttributes } from "react";

export function Table({ className = "", ...props }: TableHTMLAttributes<HTMLTableElement>) {
  return (
    <div className="overflow-x-auto rounded-lg border border-border bg-background">
      <table className={`w-full text-left text-sm ${className}`.trim()} {...props} />
    </div>
  );
}
