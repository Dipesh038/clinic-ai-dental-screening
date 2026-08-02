"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/Button";
import { CurrentUser, logout } from "@/lib/auth";

interface AppHeaderProps {
  user: CurrentUser;
}

export function AppHeader({ user }: AppHeaderProps) {
  const router = useRouter();

  async function handleLogout() {
    await logout();
    router.push("/login");
  }

  return (
    <header className="flex min-h-16 flex-wrap items-center justify-between gap-x-4 gap-y-2 border-b border-border bg-background px-4 py-2 sm:px-6">
      <div className="flex items-center gap-4 sm:gap-8">
        <span className="text-lg font-semibold text-primary">Clinic-AI</span>
        <nav className="flex items-center gap-3 sm:gap-4">
          <Link href="/dashboard" className="text-sm font-medium text-foreground hover:text-primary transition-colors">
            Dashboard
          </Link>
          <Link href="/patients" className="text-sm font-medium text-foreground hover:text-primary transition-colors">
            Patients
          </Link>
        </nav>
      </div>
      <div className="flex items-center gap-2 sm:gap-4">
        <span className="hidden text-sm text-text-secondary sm:inline">
          {user.username} <span className="capitalize">({user.role})</span>
        </span>
        <Button variant="ghost" onClick={handleLogout}>
          Log out
        </Button>
      </div>
    </header>
  );
}
