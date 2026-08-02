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
  primary:
    "bg-[#1976d2] text-white hover:bg-[#125ea3] focus-visible:outline-[#1976d2] " +
    "dark:bg-primary dark:text-[#121212] dark:hover:bg-[#BBDEFB] dark:focus-visible:outline-primary " +
    "dark:disabled:bg-[#333333] dark:disabled:text-[#666666] dark:disabled:border-none",
  secondary:
    "bg-transparent border border-border text-foreground hover:bg-surface focus-visible:outline-secondary " +
    "dark:border-primary dark:text-primary dark:hover:bg-primary/8 dark:focus-visible:outline-primary " +
    "dark:disabled:bg-transparent dark:disabled:border-[#333333] dark:disabled:text-[#666666]",
  ghost:
    "bg-transparent text-primary hover:bg-surface focus-visible:outline-primary " +
    "dark:text-primary dark:hover:bg-primary/8 dark:focus-visible:outline-primary " +
    "dark:disabled:bg-transparent dark:disabled:text-[#666666]",
  danger: 
    "bg-[#d32f2f] text-white hover:bg-[#b71c1c] focus-visible:outline-error " +
    "dark:bg-error dark:text-[#121212] dark:hover:bg-[#EF9A9A] dark:focus-visible:outline-error " +
    "dark:disabled:bg-[#333333] dark:disabled:text-[#666666]",
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
    "disabled:cursor-not-allowed light:disabled:opacity-50";

  return (
    <button
      className={`${base} ${sizeClasses[size]} ${variantClasses[variant]} ${className}`.trim()}
      disabled={disabled}
      {...props}
    />
  );
}
