"use client";

import * as React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  Download,
  ChevronDown,
  ShieldCheck,
  ListTree,
  Rows3,
  Rows4,
  FileText,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { Dialog } from "@/components/ui/dialog";
import { Toc } from "@/components/document/toc";
import { DocumentSection } from "@/components/document/document-section";
import { projects, documentSections } from "@/lib/mock-data";
import { formatDate } from "@/lib/utils";

export default function GeneratedDocumentPage() {
  const params = useParams<{ id: string }>();
  const project = projects.find((p) => p.id === params.id);

  const [activeId, setActiveId] = React.useState(documentSections[0].id);
  const [openMap, setOpenMap] = React.useState<Record<string, boolean>>(() =>
    Object.fromEntries(documentSections.map((s) => [s.id, true]))
  );
  const [mobileTocOpen, setMobileTocOpen] = React.useState(false);
  const [downloadOpen, setDownloadOpen] = React.useState(false);
  const sectionRefs = React.useRef<Record<string, HTMLDivElement | null>>({});

  React.useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) setActiveId(entry.target.id);
        });
      },
      { rootMargin: "-15% 0px -70% 0px", threshold: 0 }
    );
    Object.values(sectionRefs.current).forEach((el) => el && observer.observe(el));
    return () => observer.disconnect();
  }, []);

  function selectSection(id: string) {
    setOpenMap((prev) => ({ ...prev, [id]: true }));
    setMobileTocOpen(false);
    requestAnimationFrame(() => {
      sectionRefs.current[id]?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }

  function toggleAll(expand: boolean) {
    setOpenMap(Object.fromEntries(documentSections.map((s) => [s.id, expand])));
  }

  if (!project) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16">
        <EmptyState title="Projet introuvable" description="Ce projet n'existe pas ou a été supprimé." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-20 border-b border-border bg-surface/85 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center gap-3 px-4 py-4 lg:px-8">
          <Link href={`/projects/${project.id}/summary`} className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-muted-foreground hover:bg-surface-2 hover:text-foreground">
            <ArrowLeft className="h-4.5 w-4.5" />
          </Link>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-semibold">{project.shortName} — Cahier des Charges</p>
            <p className="text-xs text-muted-foreground">Généré le {formatDate(project.updatedAt)} · Version 1.3</p>
          </div>
          <button
            onClick={() => setMobileTocOpen(true)}
            className="flex h-9 w-9 items-center justify-center rounded-lg border border-border text-muted-foreground hover:bg-surface-2 lg:hidden"
          >
            <ListTree className="h-4 w-4" />
          </button>
          <div className="relative hidden sm:block">
            <Button variant="secondary" size="sm" className="gap-1.5" onClick={() => setDownloadOpen((o) => !o)}>
              <Download className="h-3.5 w-3.5" />
              Télécharger
              <ChevronDown className="h-3.5 w-3.5" />
            </Button>
            {downloadOpen && (
              <div className="absolute right-0 z-30 mt-2 w-44 overflow-hidden rounded-xl border border-border bg-surface shadow-lg">
                <button onClick={() => setDownloadOpen(false)} className="flex w-full items-center gap-2 px-3.5 py-2.5 text-left text-sm hover:bg-surface-2">
                  <FileText className="h-3.5 w-3.5 text-muted-foreground" /> Format PDF
                </button>
                <button onClick={() => setDownloadOpen(false)} className="flex w-full items-center gap-2 px-3.5 py-2.5 text-left text-sm hover:bg-surface-2">
                  <FileText className="h-3.5 w-3.5 text-muted-foreground" /> Format Word
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="mx-auto flex max-w-7xl gap-8 px-4 py-8 lg:px-8">
        {/* Desktop TOC */}
        <aside className="sticky top-24 hidden h-fit w-64 shrink-0 rounded-2xl border border-border bg-surface p-3 lg:block">
          <Toc sections={documentSections} activeId={activeId} onSelect={selectSection} />
        </aside>

        {/* Mobile TOC dialog */}
        <Dialog open={mobileTocOpen} onClose={() => setMobileTocOpen(false)} title="Sommaire">
          <Toc sections={documentSections} activeId={activeId} onSelect={selectSection} />
        </Dialog>

        {/* Document content */}
        <div className="min-w-0 flex-1">
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }} className="rounded-2xl border border-border bg-gradient-to-br from-primary-soft/60 to-accent-soft/40 p-6 sm:p-8">
            <Badge variant="primary">Cahier des Charges — Généré automatiquement</Badge>
            <h1 className="mt-3 font-display text-2xl font-bold tracking-tight sm:text-3xl">{project.name}</h1>
            <p className="mt-2 max-w-2xl text-sm text-muted-foreground">{project.description}</p>
            <div className="mt-4 flex flex-wrap items-center gap-4 text-xs text-muted-foreground">
              <span>Porteur : <strong className="text-foreground">{project.owner.name}</strong></span>
              <span>Département : <strong className="text-foreground">{project.department}</strong></span>
              <span className="flex items-center gap-1.5 font-medium text-accent">
                <ShieldCheck className="h-3.5 w-3.5" /> Score sécurité {project.securityScore}/100
              </span>
            </div>
          </motion.div>

          <div className="mt-5 flex items-center justify-between">
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              <span className="flex items-center gap-1.5"><Badge variant="danger">Critique</Badge></span>
              <span className="flex items-center gap-1.5"><Badge variant="warning">Haute</Badge></span>
              <span className="flex items-center gap-1.5"><Badge variant="default">Moyenne</Badge></span>
            </div>
            <div className="flex items-center gap-1.5">
              <Button variant="ghost" size="sm" className="gap-1.5" onClick={() => toggleAll(true)}>
                <Rows4 className="h-3.5 w-3.5" /> Tout développer
              </Button>
              <Button variant="ghost" size="sm" className="gap-1.5" onClick={() => toggleAll(false)}>
                <Rows3 className="h-3.5 w-3.5" /> Tout réduire
              </Button>
            </div>
          </div>

          <div className="mt-4 flex flex-col gap-4">
            {documentSections.map((section) => (
              <DocumentSection
                key={section.id}
                section={section}
                open={!!openMap[section.id]}
                onToggle={() => setOpenMap((prev) => ({ ...prev, [section.id]: !prev[section.id] }))}
                sectionRef={(el) => { sectionRefs.current[section.id] = el; }}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
