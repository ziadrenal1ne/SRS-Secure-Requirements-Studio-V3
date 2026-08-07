import Link from "next/link";
import { Bot, ClipboardList, Gauge, Settings, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ui/theme-toggle";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-background">
      <header className="flex h-16 items-center justify-between border-b border-border bg-surface/80 px-4 backdrop-blur-md lg:px-8">
        <div>
          <p className="font-display text-sm font-bold">FOCP Secure Requirements Studio</p>
          <p className="text-xs text-muted-foreground">Axe Eco-Social - Fondation OCP</p>
        </div>
        <div className="flex items-center gap-2">
          <Link href="/settings">
            <Button variant="secondary" size="icon" aria-label="Parametres AI">
              <Settings className="h-4 w-4" />
            </Button>
          </Link>
          <ThemeToggle />
        </div>
      </header>

      <section className="mx-auto grid min-h-[calc(100vh-4rem)] max-w-6xl grid-cols-1 gap-8 px-4 py-10 lg:grid-cols-[0.95fr_1.05fr] lg:px-8">
        <div className="flex flex-col justify-center">
          <div className="mb-5 flex w-fit items-center gap-2 rounded-full border border-border bg-surface px-3 py-1 text-xs font-medium text-muted-foreground">
            <ShieldCheck className="h-3.5 w-3.5 text-accent" />
            Cahier des charges, conception et cybersecurite
          </div>
          <h1 className="font-display text-4xl font-bold tracking-tight text-balance lg:text-5xl">
            Comment souhaitez-vous creer votre projet ?
          </h1>
          <p className="mt-4 max-w-xl text-sm leading-6 text-muted-foreground">
            Les deux modes alimentent les memes livrables: exigences fonctionnelles,
            architecture, base de donnees, API, risques, tests, plans de deploiement et
            documents exportables.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link href="/projects/new">
              <Button size="lg" className="gap-2">
                Demarrer
                <Gauge className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/dashboard">
              <Button size="lg" variant="secondary">
                Ouvrir le studio
              </Button>
            </Link>
          </div>
        </div>

        <div className="grid content-center gap-4">
          <Link href="/projects/new" className="group rounded-xl border border-border bg-surface p-5 transition-colors hover:border-primary">
            <div className="flex items-start gap-4">
              <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-primary-soft text-primary">
                <ClipboardList className="h-5 w-5" />
              </div>
              <div>
                <h2 className="font-display text-lg font-semibold">Mode 1 - Classic Guided Questionnaire</h2>
                <p className="mt-1 text-sm text-muted-foreground">
                  Questionnaire d&apos;analyse d&apos;entreprise avec choix, reponse libre, commentaires,
                  importance et dependances.
                </p>
              </div>
            </div>
          </Link>

          <Link href="/projects/new" className="group rounded-xl border border-border bg-surface p-5 transition-colors hover:border-accent">
            <div className="flex items-start gap-4">
              <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-accent-soft text-accent">
                <Bot className="h-5 w-5" />
              </div>
              <div>
                <h2 className="font-display text-lg font-semibold">Mode 2 - AI Interview Gemini Assistant</h2>
                <p className="mt-1 text-sm text-muted-foreground">
                  Entretien adaptatif avec Google Gemini. Si Gemini est indisponible, le mode
                  questionnaire reste disponible automatiquement.
                </p>
              </div>
            </div>
          </Link>
        </div>
      </section>
    </main>
  );
}
