"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowUpRight, ShieldCheck } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { StatusChip } from "@/components/ui/status-chip";
import { Avatar } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import type { Project } from "@/lib/types";
import { formatDate } from "@/lib/utils";

function ProjectCard({ project, delay = 0 }: { project: Project; delay?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      whileHover={{ y: -3 }}
      className="group relative flex flex-col rounded-2xl border border-border bg-surface p-5 transition-shadow hover:shadow-lg"
    >
      <Link href={`/projects/${project.id}/interview`} className="absolute inset-0 z-10" aria-label={project.name}>
        <span className="sr-only">Ouvrir {project.name}</span>
      </Link>

      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="truncate text-xs font-medium text-muted-foreground">{project.department}</p>
          <h3 className="mt-0.5 truncate font-display text-base font-semibold">{project.shortName}</h3>
        </div>
        <ArrowUpRight className="h-4 w-4 shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" />
      </div>

      <p className="mt-2 line-clamp-2 text-sm text-muted-foreground">{project.description}</p>

      <div className="mt-4 flex flex-wrap gap-1.5">
        {project.tags.slice(0, 3).map((tag) => (
          <Badge key={tag} variant="outline">{tag}</Badge>
        ))}
      </div>

      <div className="mt-5 flex items-center justify-between text-xs">
        <span className="text-muted-foreground">Progression</span>
        <span className="font-medium">{project.progress}%</span>
      </div>
      <Progress value={project.progress} className="mt-1.5" />

      <div className="mt-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Avatar initials={project.owner.initials} size="sm" />
          <span className="text-xs text-muted-foreground">{formatDate(project.updatedAt)}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1 text-xs font-medium text-accent">
            <ShieldCheck className="h-3.5 w-3.5" />
            {project.securityScore}
          </span>
          <StatusChip status={project.status} />
        </div>
      </div>
    </motion.div>
  );
}

export { ProjectCard };
