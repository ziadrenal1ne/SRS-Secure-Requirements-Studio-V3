"use client";

import * as React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Copy, Download, FileText, Loader2, Pencil, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ProjectSubNav } from "@/components/project/project-subnav";
import { ApiError, documentsApi, type ExportFormat, type GeneratedDocument } from "@/lib/api";

const FORMATS: { format: ExportFormat; label: string }[] = [
  { format: "pdf", label: "PDF" },
  { format: "docx", label: "DOCX" },
  { format: "md", label: "Markdown" },
  { format: "tex", label: "LaTeX" },
];

type CdcSection = { title: string; items: string[] };
type CdcContent = {
  summary?: string;
  completeness_score?: number;
  points_to_confirm?: string[];
  sections?: CdcSection[];
};
type ConceptionContent = { summary?: string; modules?: string[]; diagram?: string };

export default function DocumentsPage() {
  const params = useParams<{ id: string }>();
  const projectId = params.id;

  const [doc, setDoc] = React.useState<GeneratedDocument | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [generating, setGenerating] = React.useState(false);
  const [downloading, setDownloading] = React.useState<ExportFormat | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  const load = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setDoc(await documentsApi.get(projectId));
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) setDoc(null);
      else setError(err instanceof ApiError ? err.message : "Impossible de charger le document.");
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
      setDoc(await documentsApi.generate(projectId));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "La generation a echoue.");
    } finally {
      setGenerating(false);
    }
  }

  async function handleDownload(format: ExportFormat) {
    setDownloading(format);
    setError(null);
    try {
      await documentsApi.download(projectId, format);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "L'export a echoue.");
    } finally {
      setDownloading(null);
    }
  }

  async function handleCopy() {
    if (!cdc) return;
    const text = [
      cdc.summary,
      ...(cdc.sections ?? []).map((section) => `${section.title}\n${section.items.join("\n")}`),
      conception?.summary,
      conception?.diagram,
    ].filter(Boolean).join("\n\n");
    await navigator.clipboard.writeText(text);
  }

  const projectInfo = doc?.content?.project as { name?: string } | undefined;
  const cdc = doc?.content?.cahier_des_charges as CdcContent | undefined;
  const conception = doc?.content?.conception_mvp as ConceptionContent | undefined;

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-20 flex h-16 items-center gap-4 border-b border-border bg-surface/80 px-4 backdrop-blur-md lg:px-8">
        <Link href={`/projects/${projectId}/interview`} className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-surface-2 hover:text-foreground">
          <ArrowLeft className="h-4.5 w-4.5" />
        </Link>
        <p className="text-sm font-semibold">Resultat</p>
        <Button variant="secondary" size="sm" className="ml-auto gap-1.5" onClick={handleGenerate} disabled={generating}>
          {generating ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <RefreshCw className="h-3.5 w-3.5" />}
          {generating ? "Generation du Cahier des Charges..." : doc ? "Regenerer" : "Generer"}
        </Button>
      </header>

      <div className="border-b border-border bg-surface/50 px-4 py-2 lg:px-8">
        <ProjectSubNav projectId={projectId} />
      </div>

      <main className="mx-auto max-w-4xl px-4 py-8 lg:px-0">
        {loading ? (
          <p className="flex items-center gap-2 text-sm text-muted-foreground"><Loader2 className="h-4 w-4 animate-spin" /> Chargement...</p>
        ) : error ? (
          <p className="text-sm text-destructive">{error}</p>
        ) : !doc ? (
          <div className="rounded-2xl border border-dashed border-border p-8 text-center">
            <FileText className="mx-auto h-8 w-8 text-muted-foreground" />
            <p className="mt-3 text-sm text-muted-foreground">Aucun document n&apos;a encore ete genere pour ce projet.</p>
            <Button className="mt-4" onClick={handleGenerate} disabled={generating}>Generer le cahier des charges</Button>
          </div>
        ) : (
          <div className="flex flex-col gap-6">
            <section className="rounded-2xl border border-border bg-surface p-5">
              <p className="font-display text-lg font-semibold">Cahier des Charges genere - {projectInfo?.name}</p>
              <p className="mt-2 text-sm text-muted-foreground">{cdc?.summary}</p>
              <div className="mt-4 flex flex-wrap gap-2 text-xs">
                <span className="rounded-md bg-accent-soft px-2 py-1 text-accent">Completude : {cdc?.completeness_score ?? "N/A"}%</span>
                <span className="rounded-md bg-surface-2 px-2 py-1 text-muted-foreground">{cdc?.points_to_confirm?.length ?? 0} point(s) a confirmer</span>
              </div>
            </section>

            {cdc?.points_to_confirm?.length ? (
              <section className="rounded-2xl border border-border bg-surface p-5">
                <h2 className="font-display text-base font-semibold">Points a confirmer</h2>
                <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-muted-foreground">
                  {cdc.points_to_confirm.map((point) => <li key={point}>{point}</li>)}
                </ul>
              </section>
            ) : null}

            <section className="rounded-2xl border border-border bg-surface p-5">
              <h2 className="font-display text-base font-semibold">Contenu complet</h2>
              <div className="mt-4 space-y-4 text-sm">
                {cdc?.sections?.map((section) => (
                  <section key={section.title}>
                    <h3 className="font-semibold">{section.title}</h3>
                    <ul className="mt-2 list-disc space-y-1 pl-5 text-muted-foreground">
                      {section.items.map((item) => <li key={item}>{item}</li>)}
                    </ul>
                  </section>
                ))}
              </div>
            </section>

            <section className="rounded-2xl border border-border bg-surface p-5">
              <h2 className="font-display text-base font-semibold">Conception MVP</h2>
              <p className="mt-2 text-sm text-muted-foreground">{conception?.summary}</p>
              <h3 className="mt-4 text-sm font-semibold">Modules</h3>
              <div className="mt-2 flex flex-wrap gap-2">
                {conception?.modules?.map((module) => <span key={module} className="rounded-md bg-surface-2 px-2 py-1 text-xs">{module}</span>)}
              </div>
              <pre className="mt-4 overflow-x-auto rounded-xl bg-surface-2 p-4 text-xs text-muted-foreground">{conception?.diagram}</pre>
            </section>

            <section>
              <h2 className="font-display text-base font-semibold">Actions</h2>
              <div className="mt-3 flex flex-wrap gap-2">
                <Button variant="secondary" className="gap-1.5" onClick={handleCopy}><Copy className="h-3.5 w-3.5" /> Copier</Button>
                <Button variant="secondary" className="gap-1.5" disabled><Pencil className="h-3.5 w-3.5" /> Modifier</Button>
                {FORMATS.map(({ format, label }) => (
                  <Button key={format} variant="secondary" className="gap-1.5" onClick={() => handleDownload(format)} disabled={downloading === format}>
                    {downloading === format ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Download className="h-3.5 w-3.5" />}
                    Telecharger {label}
                  </Button>
                ))}
                <Button className="gap-1.5" onClick={handleGenerate} disabled={generating}>
                  <RefreshCw className="h-3.5 w-3.5" />
                  Regenerer
                </Button>
              </div>
            </section>
          </div>
        )}
      </main>
    </div>
  );
}
