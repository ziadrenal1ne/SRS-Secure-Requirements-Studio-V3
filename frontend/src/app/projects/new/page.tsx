"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowRight, Bot, ClipboardList, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { projectsApi, ApiError } from "@/lib/api";
import { cn } from "@/lib/utils";

type CreationMode = "classic" | "ai";

export default function NewProjectPage() {
  const router = useRouter();
  const [name, setName] = React.useState("Plateforme de Gestion des Beneficiaires Eco-Social");
  const [shortName, setShortName] = React.useState("PGB Eco-Social");
  const [department, setDepartment] = React.useState("Axe Eco-Social - Fondation OCP");
  const [description, setDescription] = React.useState(
    "Conception d'une plateforme de gestion des beneficiaires, cooperatives, conventions, reporting ESG/ODD et tableaux de bord."
  );
  const [mode, setMode] = React.useState<CreationMode>("classic");
  const [error, setError] = React.useState<string | null>(null);
  const [submitting, setSubmitting] = React.useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const project = await projectsApi.create({
        name,
        short_name: shortName || name.slice(0, 40),
        department,
        description,
      });
      router.push(`/projects/${project.id}/interview?mode=${mode}`);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(`${err.message}. Demarrage en mode local.`);
      }
      router.push(`/projects/focp-eco-social/interview?mode=${mode}`);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <header className="sticky top-0 z-20 flex h-16 shrink-0 items-center gap-4 border-b border-border bg-surface/80 px-4 backdrop-blur-md lg:px-8">
        <Link
          href="/"
          className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-surface-2 hover:text-foreground"
        >
          <X className="h-4.5 w-4.5" />
        </Link>
        <div>
          <p className="text-sm font-semibold">Nouveau projet FOCP</p>
          <p className="text-xs text-muted-foreground">Selectionnez le mode de collecte et lancez la conception.</p>
        </div>
      </header>

      <div className="mx-auto w-full max-w-2xl flex-1 px-4 py-10 lg:px-0">
        <form onSubmit={handleSubmit} className="flex flex-col gap-5">
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {[
              { id: "classic" as const, label: "Questionnaire guide", icon: ClipboardList },
              { id: "ai" as const, label: "AI Interview Qwen", icon: Bot },
            ].map((item) => {
              const active = mode === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setMode(item.id)}
                  className={cn(
                    "flex items-center gap-3 rounded-xl border px-4 py-3 text-left transition-colors",
                    active ? "border-primary bg-primary-soft text-primary" : "border-border bg-surface hover:bg-surface-2"
                  )}
                >
                  <item.icon className="h-5 w-5" />
                  <span className="text-sm font-semibold">{item.label}</span>
                </button>
              );
            })}
          </div>

          <label className="flex flex-col gap-1.5 text-sm font-medium">
            Nom du projet
            <Input required value={name} onChange={(event) => setName(event.target.value)} />
          </label>
          <label className="flex flex-col gap-1.5 text-sm font-medium">
            Nom court
            <Input value={shortName} onChange={(event) => setShortName(event.target.value)} />
          </label>
          <label className="flex flex-col gap-1.5 text-sm font-medium">
            Direction / departement
            <Input value={department} onChange={(event) => setDepartment(event.target.value)} />
          </label>
          <label className="flex flex-col gap-1.5 text-sm font-medium">
            Description initiale
            <Textarea value={description} onChange={(event) => setDescription(event.target.value)} rows={4} />
          </label>
          {error && <p className="text-sm text-warning">{error}</p>}
          <Button type="submit" className="gap-2 self-start" disabled={submitting}>
            {submitting ? "Creation..." : "Demarrer"}
            <ArrowRight className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </div>
  );
}
