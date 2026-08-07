"use client";

import * as React from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, ClipboardCheck, RefreshCw, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { reviewApi, ApiError, type ReviewRun } from "@/lib/api";
import { ProjectSubNav } from "@/components/project/project-subnav";

const SCORE_LABELS: { key: keyof ReviewRun; label: string }[] = [
  { key: "completeness_score", label: "Complétude" },
  { key: "confidence_score", label: "Confiance" },
  { key: "security_score", label: "Sécurité" },
  { key: "architecture_score", label: "Architecture" },
  { key: "business_score", label: "Métier" },
  { key: "testing_score", label: "Tests" },
];

export default function ReviewPage() {
  const params = useParams<{ id: string }>();
  const projectId = params.id;

  const [review, setReview] = React.useState<ReviewRun | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [running, setRunning] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [showOnlyFailed, setShowOnlyFailed] = React.useState(true);

  const load = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setReview(await reviewApi.get(projectId));
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setReview(null);
      } else {
        setError(err instanceof ApiError ? err.message : "Impossible de charger la revue.");
      }
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  React.useEffect(() => {
    load();
  }, [load]);

  async function handleRun() {
    setRunning(true);
    setError(null);
    try {
      setReview(await reviewApi.run(projectId));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "L'exécution de la revue a échoué.");
    } finally {
      setRunning(false);
    }
  }

  const findings = review
    ? showOnlyFailed
      ? review.findings.filter((f) => !f.passed)
      : review.findings
    : [];

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-20 flex h-16 items-center gap-4 border-b border-border bg-surface/80 px-4 backdrop-blur-md lg:px-8">
        <Link
          href={`/projects/${projectId}/interview`}
          className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-surface-2 hover:text-foreground"
        >
          <ArrowLeft className="h-4.5 w-4.5" />
        </Link>
        <p className="text-sm font-semibold">Revue qualité</p>
        <Button
          variant="secondary"
          size="sm"
          className="ml-auto gap-1.5"
          onClick={handleRun}
          disabled={running}
        >
          {running ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <RefreshCw className="h-3.5 w-3.5" />}
          {review ? "Relancer" : "Lancer la revue"}
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
        ) : !review ? (
          <div className="rounded-2xl border border-dashed border-border p-8 text-center">
            <ClipboardCheck className="mx-auto h-8 w-8 text-muted-foreground" />
            <p className="mt-3 text-sm text-muted-foreground">
              Aucune revue n&apos;a encore été exécutée pour ce projet.
            </p>
            <Button className="mt-4" onClick={handleRun} disabled={running}>
              Lancer la revue
            </Button>
          </div>
        ) : (
          <div className="flex flex-col gap-6">
            <div className="flex items-center gap-4 rounded-2xl border border-border bg-surface p-5">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-accent-soft text-2xl font-bold text-accent">
                {review.overall_score}
              </div>
              <div>
                <p className="font-medium">Score global</p>
                <p className="text-sm text-muted-foreground">
                  {review.failed_count} / {review.rule_count} règles en échec ·{" "}
                  {review.approved_for_export ? (
                    <span className="text-accent">Approuvé pour export (≥95%)</span>
                  ) : (
                    <span>Non approuvé pour export (seuil : 95%)</span>
                  )}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              {SCORE_LABELS.map(({ key, label }) => (
                <div key={key} className="rounded-xl border border-border bg-surface p-3.5 text-center">
                  <p className="text-xl font-semibold">{review[key] as number}</p>
                  <p className="text-xs text-muted-foreground">{label}</p>
                </div>
              ))}
            </div>

            <div>
              <div className="flex items-center justify-between">
                <h2 className="font-display text-lg font-semibold">Constats</h2>
                <button
                  onClick={() => setShowOnlyFailed((v) => !v)}
                  className="text-xs font-medium text-accent hover:underline"
                >
                  {showOnlyFailed ? "Afficher tout" : "Afficher uniquement les échecs"}
                </button>
              </div>
              <div className="mt-3 flex flex-col gap-1.5">
                {findings.map((f) => (
                  <div
                    key={f.rule_id}
                    className="flex items-center gap-2 rounded-lg border border-border bg-surface px-3 py-2 text-sm"
                  >
                    <Badge
                      variant={f.passed ? "accent" : f.severity === "critical" ? "danger" : "warning"}
                    >
                      {f.passed ? "OK" : f.severity}
                    </Badge>
                    <span className="text-muted-foreground">{f.message}</span>
                  </div>
                ))}
                {findings.length === 0 && (
                  <p className="text-sm text-muted-foreground">Aucun constat à afficher.</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
