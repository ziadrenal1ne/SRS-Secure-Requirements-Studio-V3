"use client";

import * as React from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, ShieldCheck, RefreshCw, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { securityApi, ApiError, type SecurityAnalysis } from "@/lib/api";
import { ProjectSubNav } from "@/components/project/project-subnav";

const STATUS_VARIANT: Record<string, "danger" | "warning" | "accent"> = {
  missing: "danger",
  partial: "warning",
  present: "accent",
};

export default function SecurityPage() {
  const params = useParams<{ id: string }>();
  const projectId = params.id;

  const [analysis, setAnalysis] = React.useState<SecurityAnalysis | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [analyzing, setAnalyzing] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  const load = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setAnalysis(await securityApi.get(projectId));
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setAnalysis(null);
      } else {
        setError(err instanceof ApiError ? err.message : "Impossible de charger l'analyse.");
      }
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  React.useEffect(() => {
    load();
  }, [load]);

  async function handleAnalyze() {
    setAnalyzing(true);
    setError(null);
    try {
      setAnalysis(await securityApi.analyze(projectId));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "L'analyse a échoué.");
    } finally {
      setAnalyzing(false);
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-20 flex h-16 items-center gap-4 border-b border-border bg-surface/80 px-4 backdrop-blur-md lg:px-8">
        <Link
          href={`/projects/${projectId}/interview`}
          className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-surface-2 hover:text-foreground"
        >
          <ArrowLeft className="h-4.5 w-4.5" />
        </Link>
        <p className="text-sm font-semibold">Sécurité</p>
        <Button
          variant="secondary"
          size="sm"
          className="ml-auto gap-1.5"
          onClick={handleAnalyze}
          disabled={analyzing}
        >
          {analyzing ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <RefreshCw className="h-3.5 w-3.5" />}
          {analysis ? "Ré-analyser" : "Analyser"}
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
        ) : !analysis ? (
          <div className="rounded-2xl border border-dashed border-border p-8 text-center">
            <ShieldCheck className="mx-auto h-8 w-8 text-muted-foreground" />
            <p className="mt-3 text-sm text-muted-foreground">
              Aucune analyse de sécurité n&apos;a encore été exécutée pour ce projet.
            </p>
            <Button className="mt-4" onClick={handleAnalyze} disabled={analyzing}>
              Lancer l&apos;analyse
            </Button>
          </div>
        ) : (
          <div className="flex flex-col gap-8">
            <div className="flex items-center gap-4 rounded-2xl border border-border bg-surface p-5">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-accent-soft text-2xl font-bold text-accent">
                {analysis.security_score}
              </div>
              <div>
                <p className="font-medium">Score de sécurité global</p>
                <p className="text-sm text-muted-foreground">sur 100, recalculé à chaque analyse</p>
              </div>
            </div>

            <div>
              <h2 className="font-display text-lg font-semibold">Checklist des contrôles</h2>
              <div className="mt-3 flex flex-col gap-2">
                {analysis.security_checklist.map((c) => (
                  <div
                    key={c.control_key}
                    className="flex flex-col gap-1 rounded-xl border border-border bg-surface p-3.5 sm:flex-row sm:items-center sm:justify-between"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="font-medium">{c.name}</p>
                        <Badge variant={STATUS_VARIANT[c.status]}>{c.status}</Badge>
                      </div>
                      <p className="mt-1 text-sm text-muted-foreground">{c.recommendation}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h2 className="font-display text-lg font-semibold">
                Modèle de menaces (STRIDE / DREAD)
              </h2>
              <div className="mt-3 flex flex-col gap-2">
                {analysis.threat_model.map((t) => {
                  const threat = t as {
                    threat_id: string;
                    stride_category: string;
                    description: string;
                    status: string;
                    dread: { score: number };
                  };
                  return (
                    <div key={threat.threat_id} className="rounded-xl border border-border bg-surface p-3.5">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs text-muted-foreground">
                          {threat.threat_id}
                        </span>
                        <Badge variant="outline">{threat.stride_category}</Badge>
                        <Badge variant={threat.status === "gap" ? "danger" : "accent"}>
                          {threat.status === "gap" ? "non traité" : "documenté"}
                        </Badge>
                        <span className="ml-auto text-xs text-muted-foreground">
                          DREAD : {threat.dread.score}/10
                        </span>
                      </div>
                      <p className="mt-1.5 text-sm text-muted-foreground">{threat.description}</p>
                    </div>
                  );
                })}
              </div>
            </div>

            <div>
              <h2 className="font-display text-lg font-semibold">Registre des risques</h2>
              <div className="mt-3 flex flex-col gap-2">
                {analysis.risk_register.map((r) => {
                  const risk = r as {
                    risk_id: string;
                    title: string;
                    impact: string;
                    status: string;
                    mitigation: string;
                  };
                  return (
                    <div key={risk.risk_id} className="rounded-xl border border-border bg-surface p-3.5">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs text-muted-foreground">{risk.risk_id}</span>
                        <p className="font-medium">{risk.title}</p>
                        <Badge variant={risk.impact === "critical" ? "danger" : "warning"}>
                          {risk.impact}
                        </Badge>
                      </div>
                      <p className="mt-1.5 text-sm text-muted-foreground">{risk.mitigation}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
