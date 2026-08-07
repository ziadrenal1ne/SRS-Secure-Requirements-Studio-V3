"use client";

import * as React from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, RefreshCw, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { requirementsApi, ApiError, type Requirement } from "@/lib/api";
import { ProjectSubNav } from "@/components/project/project-subnav";

const PRIORITY_VARIANT: Record<string, "danger" | "warning" | "outline" | "default"> = {
  critical: "danger",
  high: "danger",
  medium: "warning",
  low: "outline",
};

const TYPE_LABELS: Record<string, string> = {
  business: "Exigences métier",
  functional: "Exigences fonctionnelles",
  non_functional: "Exigences non fonctionnelles",
  security: "Exigences de sécurité",
  technical: "Exigences techniques",
  infrastructure: "Exigences d'infrastructure",
  deployment: "Exigences de déploiement",
  maintenance: "Exigences de maintenance",
  training: "Exigences de formation",
  performance: "Exigences de performance",
  accessibility: "Exigences d'accessibilité",
};

export default function RequirementsPage() {
  const params = useParams<{ id: string }>();
  const projectId = params.id;

  const [requirements, setRequirements] = React.useState<Requirement[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [generating, setGenerating] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const load = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setRequirements(await requirementsApi.list(projectId));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Impossible de charger les exigences.");
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  React.useEffect(() => {
    load();
  }, [load]);

  async function handleGenerate() {
    setGenerating(true);
    setError(null);
    try {
      await requirementsApi.generate(projectId);
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "La génération a échoué.");
    } finally {
      setGenerating(false);
    }
  }

  const grouped = requirements.reduce<Record<string, Requirement[]>>((acc, r) => {
    (acc[r.requirement_type] ??= []).push(r);
    return acc;
  }, {});

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-20 flex h-16 items-center gap-4 border-b border-border bg-surface/80 px-4 backdrop-blur-md lg:px-8">
        <Link
          href={`/projects/${projectId}/interview`}
          className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-surface-2 hover:text-foreground"
        >
          <ArrowLeft className="h-4.5 w-4.5" />
        </Link>
        <p className="text-sm font-semibold">Exigences</p>
        <Button
          variant="secondary"
          size="sm"
          className="ml-auto gap-1.5"
          onClick={handleGenerate}
          disabled={generating}
        >
          {generating ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <RefreshCw className="h-3.5 w-3.5" />}
          Régénérer
        </Button>
      </header>

      <div className="border-b border-border bg-surface/50 px-4 py-2 lg:px-8">
        <ProjectSubNav projectId={projectId} />
      </div>

      <div className="mx-auto max-w-4xl px-4 py-8 lg:px-0">
        {loading ? (
          <p className="text-sm text-muted-foreground">Chargement...</p>
        ) : error ? (
          <p className="text-sm text-destructive">{error}</p>
        ) : requirements.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-border p-8 text-center">
            <p className="text-sm text-muted-foreground">
              Aucune exigence n&apos;a encore été générée. Les exigences apparaissent
              automatiquement au fil de l&apos;entretien, ou peuvent être régénérées ici.
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-8">
            {Object.entries(grouped).map(([type, reqs]) => (
              <div key={type}>
                <h2 className="font-display text-lg font-semibold">
                  {TYPE_LABELS[type] ?? type}
                </h2>
                <div className="mt-3 flex flex-col gap-3">
                  {reqs.map((r) => (
                    <div key={r.id} className="rounded-2xl border border-border bg-surface p-4">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-mono text-xs text-muted-foreground">
                          {r.requirement_key}
                        </span>
                        <h3 className="font-medium">{r.title}</h3>
                        <Badge variant={PRIORITY_VARIANT[r.priority] ?? "outline"}>
                          {r.priority}
                        </Badge>
                        <Badge variant="outline">{r.status}</Badge>
                      </div>
                      <p className="mt-2 text-sm text-muted-foreground">{r.description}</p>
                      {r.acceptance_criteria.length > 0 && (
                        <ul className="mt-2 list-disc pl-5 text-sm text-muted-foreground">
                          {r.acceptance_criteria.map((c, i) => (
                            <li key={i}>{c}</li>
                          ))}
                        </ul>
                      )}
                      {r.dependencies.length > 0 && (
                        <p className="mt-2 text-xs text-muted-foreground">
                          Dépendances : {r.dependencies.join(", ")}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
