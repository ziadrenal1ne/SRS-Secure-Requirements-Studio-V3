"use client";

import * as React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Copy, Download, FileText, Loader2, Pencil, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ProjectSubNav } from "@/components/project/project-subnav";
import { ApiError, documentsApi, type ExportFormat, type GeneratedDocument } from "@/lib/api";
import { buildLocalDocument, loadLocalAnswers, loadLocalDocument, saveLocalDocument } from "@/lib/local-document";

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
      const localDocument = loadLocalDocument(projectId);
      if (localDocument) {
        setDoc(localDocument);
      } else if (err instanceof ApiError && err.status === 404) {
        setDoc(null);
      } else {
        setDoc(null);
        setError(err instanceof ApiError ? err.message : "Impossible de charger le document.");
      }
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
      const localAnswers = loadLocalAnswers(projectId);
      if (localAnswers) {
        const rebuilt = buildLocalDocument(projectId, localAnswers);
        saveLocalDocument(projectId, rebuilt);
        setDoc(rebuilt);
        return;
      }
      const localDocument = loadLocalDocument(projectId);
      if (localDocument) {
        setDoc(localDocument);
      } else {
        setError(err instanceof ApiError ? err.message : "La génération a échoué. Répondez au questionnaire guidé pour créer un document local.");
      }
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
    const text = [cdc.summary, ...(cdc.sections ?? []).map((section) => `${section.title}\n${section.items.join("\n")}`)].filter(Boolean).join("\n\n");
    await navigator.clipboard.writeText(text);
  }

  const projectInfo = doc?.content?.project as { name?: string } | undefined;
  const cdc = doc?.content?.cahier_des_charges as CdcContent | undefined;

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
        ) : !doc ? (
          <div className="rounded-2xl border border-dashed border-border p-8 text-center">
            <FileText className="mx-auto h-8 w-8 text-muted-foreground" />
            {error && <p className="mb-3 text-sm text-destructive">{error}</p>}
            <p className="mt-3 text-sm text-muted-foreground">Aucun document n&apos;a encore été généré pour ce projet.</p>
            <Button className="mt-4" onClick={handleGenerate} disabled={generating}>Generer le cahier des charges</Button>
          </div>
        ) : (
          <div className="flex flex-col gap-6">
            <section className="border-b border-border bg-surface px-6 py-7">
              <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Cahier des Charges</p>
              <h1 className="mt-2 font-display text-2xl font-semibold tracking-tight">Cahier des Charges - {projectInfo?.name}</h1>
              <p className="mt-1 text-xs text-muted-foreground">Version 1.0 · Document de cadrage fonctionnel</p>
              <p className="mt-5 max-w-3xl text-sm leading-7 text-foreground/85">{cdc?.summary}</p>
            </section>

            {cdc?.points_to_confirm?.length ? (
              <section className="border border-border bg-surface p-5">
                <h2 className="font-display text-base font-semibold">Points a confirmer</h2>
                <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-muted-foreground">
                  {cdc.points_to_confirm.map((point) => <li key={point}>{point}</li>)}
                </ul>
              </section>
            ) : null}

            <article className="border border-border bg-surface px-6 py-7">
              <div className="space-y-6 text-sm">
                {cdc?.sections?.map((section) => (
                  <section key={section.title}>
                    <h2 className="font-display text-base font-semibold text-foreground">{section.title}</h2>
                    <div className="mt-2 space-y-2 leading-7 text-foreground/85">
                      {section.items.map((item) => <p key={item}>{item}</p>)}
                    </div>
                  </section>
                ))}
              </div>
            </article>

            <section>
              <h2 className="font-display text-base font-semibold">Actions</h2>
              <div className="mt-3 flex flex-wrap gap-2">
                <Button variant="secondary" className="gap-1.5" onClick={handleCopy}><Copy className="h-3.5 w-3.5" /> Copier</Button>
                <Link href={`/projects/${projectId}/interview`}>
                  <Button variant="secondary" className="gap-1.5"><Pencil className="h-3.5 w-3.5" /> Modifier les reponses</Button>
                </Link>
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
