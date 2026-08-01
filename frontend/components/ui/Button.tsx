import { ButtonHTMLAttributes } from "react";

type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary: "bg-primary text-white hover:bg-[#125ea3] focus-visible:outline-primary",
  secondary:
    "bg-secondary text-white hover:bg-[#1d8377] focus-visible:outline-secondary",
  ghost:
    "bg-transparent text-primary border border-border hover:bg-surface focus-visible:outline-primary",
  danger: "bg-error text-white hover:bg-[#d32f2f] focus-visible:outline-error",
};

export function Button({
  variant = "primary",
  className = "",
  disabled,
  ...props
}: ButtonProps) {
  const base =
    "inline-flex min-h-11 items-center justify-center rounded px-4 py-2 text-sm font-medium transition-colors " +
    "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 " +
    "disabled:cursor-not-allowed disabled:opacity-50";

  return (
    <button
      className={`${base} ${variantClasses[variant]} ${className}`.trim()}
      disabled={disabled}
      {...props}
    />
  );
}
