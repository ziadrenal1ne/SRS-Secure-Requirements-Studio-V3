"use client";

import * as React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Clipboard, Download, FileText, Loader2, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ApiError, documentsApi, type GeneratedDocument } from "@/lib/api";

type CdcSection = { title: string; items: string[] };
type CdcContent = {
  generated_at?: string;
  project?: { name?: string; status?: string };
  cahier_des_charges?: {
    summary?: string;
    sections?: CdcSection[];
    points_to_confirm?: string[];
  };
};

export default function GeneratedDocumentPage() {
  const params = useParams<{ id: string }>();
  const projectId = params.id;
  const [document, setDocument] = React.useState<GeneratedDocument | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [downloading, setDownloading] = React.useState<"pdf" | "docx" | null>(null);

  const load = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setDocument(await documentsApi.get(projectId));
    } catch {
      try {
        setDocument(await documentsApi.generate(projectId));
      } catch (err) {
        setError(err instanceof ApiError ? err.message : "Une erreur est survenue lors de la génération. Réessayez.");
      }
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  React.useEffect(() => {
    void load();
  }, [load]);

  async function regenerate() {
    setLoading(true);
    setError(null);
    try {
      setDocument(await documentsApi.generate(projectId));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Une erreur est survenue lors de la génération. Réessayez.");
    } finally {
      setLoading(false);
    }
  }

  async function download(format: "pdf" | "docx") {
    setDownloading(format);
    try {
      await documentsApi.download(projectId, format);
    } catch {
      setError(`Le téléchargement ${format.toUpperCase()} a échoué. Réessayez.`);
    } finally {
      setDownloading(null);
    }
  }

  const content = (document?.content ?? {}) as CdcContent;
  const cdc = content.cahier_des_charges;
  const projectName = content.project?.name ?? "Projet";
  const generatedAt = content.generated_at ? new Date(content.generated_at).toLocaleDateString("fr-FR") : "";

  return (
    <main className="min-h-screen bg-background">
      <header className="sticky top-0 z-20 border-b border-border bg-surface/90 backdrop-blur-md">
        <div className="mx-auto flex max-w-5xl items-center gap-3 px-4 py-4">
          <Link href={`/projects/${projectId}/interview`} className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground hover:bg-surface-2 hover:text-foreground">
            <ArrowLeft className="h-4 w-4" />
          </Link>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-semibold">Cahier des Charges</p>
            <p className="text-xs text-muted-foreground">{projectName} · Version 1.0{generatedAt ? ` · Généré le ${generatedAt}` : ""}</p>
          </div>
          <Button variant="secondary" size="sm" onClick={regenerate} disabled={loading} className="gap-2">
            <RefreshCw className="h-4 w-4" /> Régénérer
          </Button>
          <Button variant="secondary" size="sm" onClick={() => download("pdf")} disabled={!!downloading} className="gap-2">
            {downloading === "pdf" ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />} PDF
          </Button>
          <Button variant="secondary" size="sm" onClick={() => download("docx")} disabled={!!downloading} className="gap-2">
            {downloading === "docx" ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileText className="h-4 w-4" />} Word
          </Button>
        </div>
      </header>

      <section className="mx-auto max-w-5xl px-4 py-8">
        {loading && <p className="flex items-center gap-2 text-sm text-muted-foreground"><Loader2 className="h-4 w-4 animate-spin" /> Génération en cours...</p>}
        {error && <p className="rounded-lg border border-warning/30 bg-warning-soft px-3 py-2 text-sm text-warning">{error}</p>}
        {!loading && cdc && (
          <article className="bg-surface px-8 py-10 shadow-sm ring-1 ring-border sm:px-12">
            <div className="border-b border-border pb-6">
              <p className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">Cahier des Charges</p>
              <h1 className="mt-2 font-display text-3xl font-semibold tracking-tight">{projectName}</h1>
              <p className="mt-2 text-sm text-muted-foreground">Version 1.0 · Généré le {generatedAt}</p>
            </div>
            {cdc.summary && <p className="mt-6 leading-7 text-foreground/85">{cdc.summary}</p>}
            <div className="mt-8 grid gap-7">
              {cdc.sections?.map((section) => (
                <section key={section.title}>
                  <h2 className="font-display text-lg font-semibold">{section.title}</h2>
                  <ul className="mt-3 grid gap-2 text-sm leading-6 text-foreground/85">
                    {section.items.map((item, index) => <li key={`${section.title}-${index}`}>- {item}</li>)}
                  </ul>
                </section>
              ))}
            </div>
            {!!cdc.points_to_confirm?.length && (
              <section className="mt-8 border-t border-border pt-5">
                <h2 className="font-display text-lg font-semibold">Points à valider</h2>
                <ul className="mt-3 grid gap-2 text-sm leading-6 text-foreground/85">
                  {cdc.points_to_confirm.map((point, index) => <li key={index}>- {point}</li>)}
                </ul>
              </section>
            )}
            <div className="mt-8 flex flex-wrap gap-2 border-t border-border pt-5">
              <Link href={`/projects/${projectId}/interview`}><Button variant="secondary">Modifier les réponses</Button></Link>
              <Button variant="secondary" onClick={() => navigator.clipboard.writeText(JSON.stringify(cdc, null, 2))} className="gap-2"><Clipboard className="h-4 w-4" /> Copier</Button>
            </div>
          </article>
        )}
      </section>
    </main>
  );
}
