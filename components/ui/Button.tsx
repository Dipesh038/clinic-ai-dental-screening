import { ButtonHTMLAttributes } from "react";

type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";
type ButtonSize = "default" | "icon";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
}

// Kept separate from variantClasses: sizing utilities (padding/height) must
// never be passed in via className overrides on top of these, since Tailwind's
// cascade order (not JSX string order) decides which utility wins and a
// caller's "p-2 w-9 h-9" can silently lose to this base's "px-4 py-2 min-h-11".
const sizeClasses: Record<ButtonSize, string> = {
  default: "min-h-11 px-4 py-2",
  icon: "h-9 w-9 p-0",
};

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
  size = "default",
  className = "",
  disabled,
  ...props
}: ButtonProps) {
  const base =
    "inline-flex items-center justify-center rounded text-sm font-medium transition-colors " +
    "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 " +
    "disabled:cursor-not-allowed disabled:opacity-50";

  return (
    <button
      className={`${base} ${sizeClasses[size]} ${variantClasses[variant]} ${className}`.trim()}
      disabled={disabled}
      {...props}
    />
  );
}
