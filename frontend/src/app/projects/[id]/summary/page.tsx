"use client";

import * as React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { motion } from "framer-motion";
import {
  ArrowRight,
  Pencil,
  Building2,
  Calendar,
  UserRound,
  Layers,
  Users,
  ShieldCheck,
  FileCheck2,
  CheckCircle2,
  FilePlus2,
  ClipboardCheck,
  Rocket,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { StatusChip } from "@/components/ui/status-chip";
import { Avatar } from "@/components/ui/avatar";
import { ScoreRing } from "@/components/ui/score-ring";
import { EmptyState } from "@/components/ui/empty-state";
import { projects } from "@/lib/mock-data";
import { formatDate } from "@/lib/utils";

const timelineSteps = [
  { label: "Création du projet", icon: FilePlus2 },
  { label: "Questionnaire complété", icon: ClipboardCheck },
  { label: "Résumé validé", icon: CheckCircle2 },
  { label: "Cahier des charges généré", icon: Rocket },
];

export default function ProjectSummaryPage() {
  const params = useParams<{ id: string }>();
  const project = projects.find((p) => p.id === params.id);

  if (!project) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16">
        <EmptyState title="Projet introuvable" description="Ce projet n'existe pas ou a été supprimé." />
      </div>
    );
  }

  const timelineProgress = project.progress >= 100 ? 4 : project.progress >= 60 ? 2 : 1;

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-20 border-b border-border bg-surface/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center gap-4 px-4 py-4 lg:px-8">
          <Link href="/dashboard" className="text-sm text-muted-foreground hover:text-foreground">Tableau de bord</Link>
          <span className="text-muted-foreground">/</span>
          <span className="text-sm font-medium">Résumé du projet</span>
        </div>
      </header>

      <div className="mx-auto max-w-6xl px-4 py-8 lg:px-8">
        <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-start">
          <div>
            <div className="flex flex-wrap items-center gap-2.5">
              <h1 className="font-display text-2xl font-bold tracking-tight">{project.name}</h1>
              <StatusChip status={project.status} />
            </div>
            <p className="mt-2 max-w-2xl text-sm text-muted-foreground">{project.description}</p>
            <div className="mt-3 flex flex-wrap gap-1.5">
              {project.tags.map((tag) => <Badge key={tag} variant="primary">{tag}</Badge>)}
            </div>
          </div>
          <div className="flex shrink-0 gap-2.5">
            <Link href="/projects/new">
              <Button variant="secondary" className="gap-2">
                <Pencil className="h-4 w-4" />
                Modifier
              </Button>
            </Link>
            <Link href={`/projects/${project.id}/document`}>
              <Button className="gap-2">
                Voir le cahier des charges
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>

        {/* Timeline */}
        <div className="mt-8 rounded-2xl border border-border bg-surface p-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            {timelineSteps.map((step, i) => {
              const active = i < timelineProgress;
              return (
                <div key={step.label} className="flex flex-1 items-center gap-3">
                  <div className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-full ${active ? "bg-accent text-white" : "bg-surface-2 text-muted-foreground"}`}>
                    <step.icon className="h-4.5 w-4.5" />
                  </div>
                  <span className={`text-sm font-medium ${active ? "text-foreground" : "text-muted-foreground"}`}>{step.label}</span>
                  {i < timelineSteps.length - 1 && <div className="hidden h-px flex-1 bg-border sm:block" />}
                </div>
              );
            })}
          </div>
        </div>

        <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Project info */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }} className="rounded-2xl border border-border bg-surface p-6 lg:col-span-2">
            <h2 className="font-display text-base font-semibold">Informations du projet</h2>
            <dl className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div className="flex items-start gap-3">
                <Building2 className="mt-0.5 h-4 w-4 text-muted-foreground" />
                <div>
                  <dt className="text-xs text-muted-foreground">Département</dt>
                  <dd className="text-sm font-medium">{project.department}</dd>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <UserRound className="mt-0.5 h-4 w-4 text-muted-foreground" />
                <div>
                  <dt className="text-xs text-muted-foreground">Porteur du projet</dt>
                  <dd className="text-sm font-medium">{project.owner.name} — {project.owner.role}</dd>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Calendar className="mt-0.5 h-4 w-4 text-muted-foreground" />
                <div>
                  <dt className="text-xs text-muted-foreground">Créé le</dt>
                  <dd className="text-sm font-medium">{formatDate(project.createdAt)}</dd>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <FileCheck2 className="mt-0.5 h-4 w-4 text-muted-foreground" />
                <div>
                  <dt className="text-xs text-muted-foreground">Exigences estimées</dt>
                  <dd className="text-sm font-medium">{project.estimatedRequirements} exigences</dd>
                </div>
              </div>
            </dl>
          </motion.div>

          {/* Security score */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35, delay: 0.05 }} className="flex flex-col items-center justify-center rounded-2xl border border-border bg-surface p-6 text-center">
            <h2 className="font-display text-base font-semibold">Aperçu du score de sécurité</h2>
            <div className="mt-4">
              <ScoreRing score={project.securityScore} label="/ 100" />
            </div>
            <p className="mt-4 text-xs text-muted-foreground">
              Basé sur la sensibilité des données déclarées et les contrôles d&apos;accès recommandés.
            </p>
          </motion.div>
        </div>

        {/* Modules */}
        <div className="mt-6">
          <div className="flex items-center justify-between">
            <h2 className="flex items-center gap-2 font-display text-lg font-semibold">
              <Layers className="h-5 w-5 text-primary" />
              Modules détectés
            </h2>
            <Link href="/projects/new" className="text-xs font-medium text-primary hover:underline">Modifier</Link>
          </div>
          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {project.modules.map((m, i) => (
              <motion.div key={m.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3, delay: i * 0.05 }} className="rounded-2xl border border-border bg-surface p-5">
                <p className="font-display text-sm font-semibold">{m.name}</p>
                <p className="mt-1.5 text-xs text-muted-foreground">{m.description}</p>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Roles */}
        <div className="mt-6">
          <div className="flex items-center justify-between">
            <h2 className="flex items-center gap-2 font-display text-lg font-semibold">
              <Users className="h-5 w-5 text-primary" />
              Rôles identifiés
            </h2>
            <Link href="/projects/new" className="text-xs font-medium text-primary hover:underline">Modifier</Link>
          </div>
          <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
            {project.roles.map((r, i) => (
              <motion.div key={r.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3, delay: i * 0.05 }} className="rounded-2xl border border-border bg-surface p-5">
                <div className="flex items-center gap-2.5">
                  <Avatar initials={r.name.slice(0, 2).toUpperCase()} size="sm" />
                  <p className="font-display text-sm font-semibold">{r.name}</p>
                </div>
                <p className="mt-2 text-xs text-muted-foreground">{r.description}</p>
                <ul className="mt-3 flex flex-col gap-1.5">
                  {r.permissions.map((perm) => (
                    <li key={perm} className="flex items-center gap-2 text-xs text-foreground">
                      <ShieldCheck className="h-3.5 w-3.5 text-accent" />
                      {perm}
                    </li>
                  ))}
                </ul>
              </motion.div>
            ))}
          </div>
        </div>

        <div className="mt-8 flex items-center justify-between rounded-2xl border border-dashed border-primary/40 bg-primary-soft/40 p-6">
          <div>
            <p className="font-display text-base font-semibold">Prêt à générer le cahier des charges ?</p>
            <p className="mt-1 text-sm text-muted-foreground">Le document intégrera automatiquement les exigences de cybersécurité recommandées.</p>
          </div>
          <Link href={`/projects/${project.id}/document`}>
            <Button size="lg" className="gap-2 whitespace-nowrap">
              Générer le document
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
