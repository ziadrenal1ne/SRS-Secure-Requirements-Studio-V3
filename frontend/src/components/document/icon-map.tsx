import {
  Building2,
  Target,
  ListChecks,
  Cpu,
  ShieldCheck,
  KeyRound,
  Workflow,
  Database,
  Braces,
  Network,
  type LucideIcon,
} from "lucide-react";

const iconMap: Record<string, LucideIcon> = {
  Building2,
  Target,
  ListChecks,
  Cpu,
  ShieldCheck,
  KeyRound,
  Workflow,
  Database,
  Braces,
  Network,
};

function getSectionIcon(name: string): LucideIcon {
  return iconMap[name] ?? ListChecks;
}

export { getSectionIcon };
