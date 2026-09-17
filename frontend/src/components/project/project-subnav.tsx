"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const TABS = [
  { segment: "interview", label: "Entretien" },
  { segment: "documents", label: "Cahier des Charges" },
];

export function ProjectSubNav({ projectId }: { projectId: string }) {
  const pathname = usePathname();

  return (
    <nav className="flex items-center gap-1 overflow-x-auto">
      {TABS.map((tab) => {
        const href = `/projects/${projectId}/${tab.segment}`;
        const active = pathname?.startsWith(href);
        return (
          <Link
            key={tab.segment}
            href={href}
            className={cn(
              "shrink-0 rounded-lg px-3 py-1.5 text-xs font-medium transition-colors",
              active
                ? "bg-accent-soft text-accent"
                : "text-muted-foreground hover:bg-surface-2 hover:text-foreground"
            )}
          >
            {tab.label}
          </Link>
        );
      })}
    </nav>
  );
}
