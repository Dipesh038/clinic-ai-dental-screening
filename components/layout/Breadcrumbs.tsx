"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export function Breadcrumbs() {
  const pathname = usePathname();
  
  if (!pathname || pathname === "/" || pathname === "/login") {
    return null;
  }

  const segments = pathname.split("/").filter(Boolean);
  
  // Exclude dashboard as it's the root for logged-in users, but add it explicitly as the first item
  const breadcrumbItems = [{ label: "Dashboard", href: "/dashboard" }];
  
  let currentPath = "";
  segments.forEach((segment) => {
    currentPath += `/${segment}`;
    if (segment === "dashboard") return; // already added

    // Format the segment for display
    let label = segment.charAt(0).toUpperCase() + segment.slice(1);
    
    // If it looks like a Mongo ObjectID (24 hex chars) or UUID, simplify it
    if (/^[0-9a-fA-F]{24}$/.test(segment)) {
      label = "Details";
    }

    breadcrumbItems.push({
      label,
      href: currentPath,
    });
  });

  return (
    <nav aria-label="Breadcrumb" className="bg-surface px-6 py-2 border-b border-border print:hidden">
      <ol className="flex items-center space-x-2 text-sm text-text-secondary">
        {breadcrumbItems.map((item, index) => {
          const isLast = index === breadcrumbItems.length - 1;
          return (
            <li key={item.href} className="flex items-center">
              {isLast ? (
                <span className="text-foreground font-medium" aria-current="page">
                  {item.label}
                </span>
              ) : (
                <>
                  <Link href={item.href} className="hover:text-primary hover:underline transition-colors">
                    {item.label}
                  </Link>
                  <span className="mx-2 text-border">/</span>
                </>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
