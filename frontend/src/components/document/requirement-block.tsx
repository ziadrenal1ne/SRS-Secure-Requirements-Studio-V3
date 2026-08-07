import { Badge } from "@/components/ui/badge";
import type { DocumentRequirement } from "@/lib/types";
import { cn } from "@/lib/utils";

const priorityConfig = {
  critique: { label: "Critique", variant: "danger" as const },
  haute: { label: "Haute", variant: "warning" as const },
  moyenne: { label: "Moyenne", variant: "default" as const },
};

function RequirementBlock({ requirement }: { requirement: DocumentRequirement }) {
  const priority = priorityConfig[requirement.priority];
  return (
    <div className="flex flex-col gap-2 rounded-xl border border-border bg-surface-2/60 p-4 sm:flex-row sm:items-start sm:gap-4">
      <code
        className={cn(
          "inline-flex h-fit shrink-0 items-center rounded-md bg-surface px-2 py-1 font-mono text-[11px] font-semibold text-primary",
          "border border-border"
        )}
      >
        {requirement.code}
      </code>
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <p className="text-sm font-semibold">{requirement.label}</p>
          <Badge variant={priority.variant}>{priority.label}</Badge>
        </div>
        <p className="mt-1 text-sm text-muted-foreground">{requirement.detail}</p>
      </div>
    </div>
  );
}

export { RequirementBlock };
