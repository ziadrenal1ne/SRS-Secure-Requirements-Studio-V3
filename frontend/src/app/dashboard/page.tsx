"use client";

import * as React from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  FolderKanban,
  Loader2,
  ShieldCheck,
  FileCheck2,
  Plus,
  SlidersHorizontal,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { SearchBar } from "@/components/ui/search-bar";
import { StatCard } from "@/components/dashboard/stat-card";
import { ProjectCard } from "@/components/dashboard/project-card";
import { EmptyState } from "@/components/ui/empty-state";
import { Avatar } from "@/components/ui/avatar";
import { projects as seededProjects, recentActivity } from "@/lib/mock-data";
import type { Project, ProjectStatus } from "@/lib/types";
import { cn } from "@/lib/utils";
import { projectsApi, ApiError } from "@/lib/api";
import { toDisplayProject } from "@/lib/adapters";

const filters: { value: ProjectStatus | "tous"; label: string }[] = [
  { value: "tous", label: "Tous" },
  { value: "brouillon", label: "Brouillon" },
  { value: "en_cours", label: "En cours" },
  { value: "en_revue", label: "En revue" },
  { value: "valide", label: "Validé" },
];

export default function DashboardPage() {
  const [query, setQuery] = React.useState("");
  const [statusFilter, setStatusFilter] = React.useState<ProjectStatus | "tous">("tous");
  const [projects, setProjects] = React.useState<Project[]>(seededProjects);
  const [loadingProjects, setLoadingProjects] = React.useState(true);
  const [loadError, setLoadError] = React.useState<string | null>(null);

  const loadProjects = React.useCallback(async () => {
    setLoadingProjects(true);
    setLoadError(null);
    try {
      const apiProjects = await projectsApi.list();
      setProjects(apiProjects.map((p) => toDisplayProject(p)));
    } catch (err) {
      setProjects(seededProjects);
      setLoadError(err instanceof ApiError ? err.message : null);
    } finally {
      setLoadingProjects(false);
    }
  }, []);

  React.useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  const dashboardStats = {
    totalProjects: projects.length,
    inProgress: projects.filter((p) => p.status === "en_cours").length,
    avgSecurityScore: projects.length
      ? Math.round(projects.reduce((sum, p) => sum + p.securityScore, 0) / projects.length)
      : 0,
    requirementsGenerated: projects.reduce((sum, p) => sum + p.estimatedRequirements, 0),
  };

  const filtered = projects.filter((p) => {
    const matchesQuery =
      p.name.toLowerCase().includes(query.toLowerCase()) ||
      p.department.toLowerCase().includes(query.toLowerCase());
    const matchesStatus = statusFilter === "tous" || p.status === statusFilter;
    return matchesQuery && matchesStatus;
  });

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 lg:px-8">
      {/* Header */}
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="font-display text-2xl font-bold tracking-tight">
            Studio Fondation OCP
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Voici l&apos;état de vos cahiers des charges aujourd&apos;hui.
          </p>
        </div>
        <Link href="/projects/new">
          <Button size="lg" className="gap-2">
            <Plus className="h-4 w-4" />
            Créer un projet
          </Button>
        </Link>
      </div>

      {/* Stats */}
      <div className="mt-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Projets actifs" value={dashboardStats.totalProjects} icon={FolderKanban} accent="primary" delay={0} />
        <StatCard label="En cours de rédaction" value={dashboardStats.inProgress} icon={Loader2} accent="warning" delay={0.05} />
        <StatCard label="Score sécurité moyen" value={dashboardStats.avgSecurityScore} suffix="/100" icon={ShieldCheck} accent="accent" trend="+6 ce mois" delay={0.1} />
        <StatCard label="Exigences générées" value={dashboardStats.requirementsGenerated} icon={FileCheck2} accent="primary" delay={0.15} />
      </div>

      <div className="mt-8 grid grid-cols-1 gap-8 xl:grid-cols-3">
        {/* Projects */}
        <div className="xl:col-span-2">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <h2 className="font-display text-lg font-semibold">Vos projets</h2>
            <div className="flex items-center gap-2">
              <SearchBar value={query} onChange={setQuery} className="w-full sm:w-56" />
              <Button variant="secondary" size="icon" aria-label="Filtres">
                <SlidersHorizontal className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            {filters.map((f) => (
              <button
                key={f.value}
                onClick={() => setStatusFilter(f.value)}
                className={cn(
                  "rounded-full border px-3.5 py-1.5 text-xs font-medium transition-colors",
                  statusFilter === f.value
                    ? "border-primary bg-primary-soft text-primary"
                    : "border-border text-muted-foreground hover:border-border-strong hover:text-foreground"
                )}
              >
                {f.label}
              </button>
            ))}
          </div>

          {loadingProjects ? (
            <p className="mt-5 text-sm text-muted-foreground">Chargement des projets...</p>
          ) : loadError ? (
            <EmptyState
              className="mt-5"
              icon={<FolderKanban className="h-6 w-6" />}
              title="Impossible de charger les projets"
              description={loadError}
              action={
                <Button variant="secondary" onClick={loadProjects}>
                  Réessayer
                </Button>
              }
            />
          ) : filtered.length > 0 ? (
            <div className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2">
              {filtered.map((project, i) => (
                <ProjectCard key={project.id} project={project} delay={i * 0.05} />
              ))}
            </div>
          ) : (
            <EmptyState
              className="mt-5"
              icon={<FolderKanban className="h-6 w-6" />}
              title="Aucun projet ne correspond"
              description={
                projects.length === 0
                  ? "Créez votre premier projet pour commencer."
                  : "Essayez un autre mot-clé ou réinitialisez les filtres."
              }
              action={
                <Button variant="secondary" onClick={() => { setQuery(""); setStatusFilter("tous"); }}>
                  Réinitialiser
                </Button>
              }
            />
          )}
        </div>

        {/* Recent activity */}
        <div>
          <h2 className="font-display text-lg font-semibold">Activité récente</h2>
          <div className="mt-4 rounded-2xl border border-border bg-surface p-5">
            <ol className="relative flex flex-col gap-5 before:absolute before:left-[15px] before:top-2 before:h-[calc(100%-2rem)] before:w-px before:bg-border">
              {recentActivity.map((activity, i) => (
                <motion.li
                  key={activity.id}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.35, delay: i * 0.05 }}
                  className="relative flex gap-3 pl-0"
                >
                  <Avatar initials={activity.initials} size="sm" className="z-10" />
                  <div className="min-w-0 pt-0.5">
                    <p className="text-sm leading-snug">
                      <span className="font-medium">{activity.actor}</span>{" "}
                      <span className="text-muted-foreground">{activity.action}</span>{" "}
                      <span className="font-medium">{activity.target}</span>
                    </p>
                    <p className="mt-0.5 text-xs text-muted-foreground">{activity.time}</p>
                  </div>
                </motion.li>
              ))}
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
}
