"use client";

import * as React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  ArrowLeft,
  ArrowRight,
  Building2,
  UserRound,
  Calendar,
  Layers,
  Users,
  Send,
  Download,
  FileText,
  FileSpreadsheet,
  Image as ImageIcon,
  GitCommitHorizontal,
  CheckCheck,
  ClipboardCheck,
  FilePlus2,
  Rocket,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { StatusChip } from "@/components/ui/status-chip";
import { Avatar } from "@/components/ui/avatar";
import { ScoreRing } from "@/components/ui/score-ring";
import { Textarea } from "@/components/ui/textarea";
import { EmptyState } from "@/components/ui/empty-state";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { RequirementBlock } from "@/components/document/requirement-block";
import {
  projects,
  documentSections,
  documentVersions,
  generatedFiles,
  projectComments,
} from "@/lib/mock-data";
import { formatDate, formatDateTime } from "@/lib/utils";

const fileIcon: Record<string, React.ReactNode> = {
  PDF: <FileText className="h-4 w-4 text-danger" />,
  Excel: <FileSpreadsheet className="h-4 w-4 text-accent" />,
  Image: <ImageIcon className="h-4 w-4 text-primary" />,
};

const projectTimeline = [
  { label: "Projet créé", icon: FilePlus2 },
  { label: "Questionnaire complété", icon: ClipboardCheck },
  { label: "Soumis pour revue", icon: Send },
  { label: "Cahier des charges généré", icon: Rocket },
  { label: "Validé par l'administration", icon: CheckCheck },
];

export default function AdminProjectDetailsPage() {
  const params = useParams<{ id: string }>();
  const project = projects.find((p) => p.id === params.id);
  const [comments, setComments] = React.useState(projectComments);
  const [draft, setDraft] = React.useState("");

  if (!project) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16">
        <EmptyState title="Projet introuvable" description="Ce projet n'existe pas ou a été supprimé." />
      </div>
    );
  }

  const requirementSections = documentSections.filter((s) => s.requirements);
  const timelineProgress =
    project.status === "valide" ? 5 : project.status === "en_revue" ? 3 : project.progress >= 60 ? 2 : 1;

  function postComment() {
    if (!draft.trim()) return;
    setComments((prev) => [...prev, { id: `c${prev.length + 1}`, author: "Karim El Amrani", initials: "KA", text: draft.trim(), time: "à l'instant" }]);
    setDraft("");
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-8 lg:px-8">
      <Link href="/admin" className="flex w-fit items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeft className="h-3.5 w-3.5" />
        Retour aux soumissions
      </Link>

      <div className="mt-4 flex flex-col justify-between gap-4 sm:flex-row sm:items-start">
        <div>
          <div className="flex flex-wrap items-center gap-2.5">
            <h1 className="font-display text-2xl font-bold tracking-tight">{project.name}</h1>
            <StatusChip status={project.status} />
          </div>
          <p className="mt-2 max-w-2xl text-sm text-muted-foreground">{project.description}</p>
        </div>
        <div className="flex shrink-0 gap-2.5">
          <Button variant="secondary">Demander une révision</Button>
          <Link href={`/projects/${project.id}/document`}>
            <Button className="gap-2">
              Voir le document
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </div>

      <Tabs defaultValue="overview" className="mt-8">
        <TabsList className="flex-wrap">
          <TabsTrigger value="overview">Aperçu</TabsTrigger>
          <TabsTrigger value="requirements">Exigences</TabsTrigger>
          <TabsTrigger value="timeline">Chronologie</TabsTrigger>
          <TabsTrigger value="versions">Versions</TabsTrigger>
          <TabsTrigger value="notes">Notes & commentaires</TabsTrigger>
          <TabsTrigger value="files">Fichiers générés</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-6">
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <div className="rounded-2xl border border-border bg-surface p-6 lg:col-span-2">
              <h2 className="font-display text-base font-semibold">Informations</h2>
              <dl className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div className="flex items-start gap-3">
                  <Building2 className="mt-0.5 h-4 w-4 text-muted-foreground" />
                  <div><dt className="text-xs text-muted-foreground">Département</dt><dd className="text-sm font-medium">{project.department}</dd></div>
                </div>
                <div className="flex items-start gap-3">
                  <UserRound className="mt-0.5 h-4 w-4 text-muted-foreground" />
                  <div><dt className="text-xs text-muted-foreground">Porteur</dt><dd className="text-sm font-medium">{project.owner.name}</dd></div>
                </div>
                <div className="flex items-start gap-3">
                  <Calendar className="mt-0.5 h-4 w-4 text-muted-foreground" />
                  <div><dt className="text-xs text-muted-foreground">Dernière mise à jour</dt><dd className="text-sm font-medium">{formatDate(project.updatedAt)}</dd></div>
                </div>
                <div className="flex items-start gap-3">
                  <Layers className="mt-0.5 h-4 w-4 text-muted-foreground" />
                  <div><dt className="text-xs text-muted-foreground">Modules</dt><dd className="text-sm font-medium">{project.modules.length} modules détectés</dd></div>
                </div>
              </dl>

              <h3 className="mt-6 flex items-center gap-2 font-display text-sm font-semibold">
                <Users className="h-4 w-4 text-primary" /> Rôles
              </h3>
              <div className="mt-3 flex flex-wrap gap-2">
                {project.roles.map((r) => <Badge key={r.id} variant="outline">{r.name}</Badge>)}
              </div>
            </div>

            <div className="flex flex-col items-center justify-center rounded-2xl border border-border bg-surface p-6 text-center">
              <p className="font-display text-sm font-semibold">Score de sécurité</p>
              <div className="mt-3"><ScoreRing score={project.securityScore} label="/ 100" size={110} /></div>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="requirements" className="mt-6">
          <div className="flex flex-col gap-6">
            {requirementSections.map((section) => (
              <div key={section.id}>
                <h3 className="font-display text-sm font-semibold text-muted-foreground">{section.title}</h3>
                <div className="mt-3 flex flex-col gap-2.5">
                  {section.requirements?.map((req) => <RequirementBlock key={req.id} requirement={req} />)}
                </div>
              </div>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="timeline" className="mt-6">
          <div className="rounded-2xl border border-border bg-surface p-6">
            <ol className="relative flex flex-col gap-6 before:absolute before:left-[15px] before:top-2 before:h-[calc(100%-2rem)] before:w-px before:bg-border">
              {projectTimeline.map((step, i) => {
                const active = i < timelineProgress;
                return (
                  <li key={step.label} className="relative flex items-center gap-3.5">
                    <div className={`z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${active ? "bg-accent text-white" : "bg-surface-2 text-muted-foreground"}`}>
                      <step.icon className="h-4 w-4" />
                    </div>
                    <span className={`text-sm ${active ? "font-medium text-foreground" : "text-muted-foreground"}`}>{step.label}</span>
                  </li>
                );
              })}
            </ol>
          </div>
        </TabsContent>

        <TabsContent value="versions" className="mt-6">
          <div className="flex flex-col gap-3">
            {documentVersions.map((v) => (
              <div key={v.id} className="flex items-start gap-3.5 rounded-2xl border border-border bg-surface p-4">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-surface-2 text-muted-foreground">
                  <GitCommitHorizontal className="h-4.5 w-4.5" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge variant="primary">v{v.version}</Badge>
                    <span className="text-xs text-muted-foreground">{formatDateTime(v.date)} · {v.author}</span>
                  </div>
                  <p className="mt-1.5 text-sm">{v.change}</p>
                </div>
              </div>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="notes" className="mt-6">
          <div className="rounded-2xl border border-border bg-surface p-5">
            <div className="flex flex-col gap-4">
              {comments.map((c) => (
                <div key={c.id} className="flex gap-3">
                  <Avatar initials={c.initials} size="sm" />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm"><span className="font-medium">{c.author}</span> <span className="text-xs text-muted-foreground">{c.time}</span></p>
                    <p className="mt-0.5 text-sm text-muted-foreground">{c.text}</p>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-5 border-t border-border pt-4">
              <Textarea value={draft} onChange={(e) => setDraft(e.target.value)} placeholder="Ajouter une note ou un commentaire pour l'équipe projet…" rows={3} />
              <div className="mt-2.5 flex justify-end">
                <Button size="sm" className="gap-1.5" onClick={postComment}>
                  <Send className="h-3.5 w-3.5" /> Publier
                </Button>
              </div>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="files" className="mt-6">
          <div className="flex flex-col gap-2.5">
            {generatedFiles.map((f) => (
              <div key={f.id} className="flex items-center justify-between rounded-xl border border-border bg-surface px-4 py-3.5">
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-surface-2">{fileIcon[f.type]}</div>
                  <div>
                    <p className="text-sm font-medium">{f.name}</p>
                    <p className="text-xs text-muted-foreground">{f.size} · Généré le {formatDate(f.date)}</p>
                  </div>
                </div>
                <Button variant="ghost" size="icon" aria-label="Télécharger">
                  <Download className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
