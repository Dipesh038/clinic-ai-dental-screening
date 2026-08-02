import { ButtonHTMLAttributes } from "react";

type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary: "bg-primary text-white hover:bg-[#125ea3] focus-visible:outline-primary",
  // bg-secondary (#26a69a) fails WCAG AA contrast (2.99:1) with white text at this
  // size; #1d8377 is the same hue darkened to pass (4.6:1).
  secondary:
    "bg-[#1d8377] text-white hover:bg-[#166b62] focus-visible:outline-secondary",
  ghost:
    "bg-transparent text-primary border border-border hover:bg-surface focus-visible:outline-primary",
  // bg-error (#f44336) fails WCAG AA contrast (3.68:1) with white text at this
  // size; #d32f2f is the same hue darkened to pass (4.98:1).
  danger: "bg-[#d32f2f] text-white hover:bg-[#b71c1c] focus-visible:outline-error",
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
