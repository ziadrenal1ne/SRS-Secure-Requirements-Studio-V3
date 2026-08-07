"use client";

import { getSectionIcon } from "./icon-map";
import { cn } from "@/lib/utils";
import type { DocumentSection } from "@/lib/types";

function Toc({
  sections,
  activeId,
  onSelect,
}: {
  sections: DocumentSection[];
  activeId: string;
  onSelect: (id: string) => void;
}) {
  return (
    <nav className="flex flex-col gap-0.5">
      <p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        Sommaire
      </p>
      {sections.map((section, i) => {
        const Icon = getSectionIcon(section.icon);
        const active = activeId === section.id;
        return (
          <button
            key={section.id}
            onClick={() => onSelect(section.id)}
            className={cn(
              "flex items-center gap-2.5 rounded-lg px-3 py-2 text-left text-sm transition-colors",
              active ? "bg-primary-soft font-medium text-primary" : "text-muted-foreground hover:bg-surface-2 hover:text-foreground"
            )}
          >
            <span className={cn("flex h-5 w-5 shrink-0 items-center justify-center rounded-md text-[10px] font-semibold", active ? "bg-primary text-white" : "bg-surface-2 text-muted-foreground")}>
              {i + 1}
            </span>
            <Icon className="h-3.5 w-3.5 shrink-0" />
            <span className="truncate">{section.title}</span>
          </button>
        );
      })}
    </nav>
  );
}

export { Toc };
