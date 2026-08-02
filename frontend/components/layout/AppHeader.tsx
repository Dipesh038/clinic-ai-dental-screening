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
    <header className="flex min-h-16 items-center justify-between border-b border-border bg-background px-6">
      <div className="flex items-center gap-8">
        <span className="text-lg font-semibold text-primary">Clinic-AI</span>
        <nav className="flex items-center gap-4">
          <Link href="/dashboard" className="text-sm font-medium text-foreground hover:text-primary transition-colors">
            Dashboard
          </Link>
          <Link href="/patients" className="text-sm font-medium text-foreground hover:text-primary transition-colors">
            Patients
          </Link>
        </nav>
      </div>
      <div className="flex items-center gap-4">
        <span className="text-sm text-text-secondary">
          {user.username} <span className="capitalize">({user.role})</span>
        </span>
        <Button variant="ghost" onClick={handleLogout}>
          Log out
        </Button>
      </div>
    </header>
  );
}
