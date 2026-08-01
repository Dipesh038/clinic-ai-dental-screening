"use client";

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
      <span className="text-lg font-semibold text-primary">Clinic-AI</span>
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
