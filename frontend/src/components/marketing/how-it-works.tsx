"use client";

import { motion } from "framer-motion";
import { NotebookPen, Layers3, ClipboardCheck, FileDown } from "lucide-react";

const steps = [
  { icon: NotebookPen, title: "Décrivez votre besoin", description: "Répondez à un questionnaire clair : objectifs, utilisateurs, données manipulées." },
  { icon: Layers3, title: "Le studio structure vos réponses", description: "Modules, rôles et exigences techniques sont détectés automatiquement à partir de vos réponses." },
  { icon: ClipboardCheck, title: "Validez le résumé", description: "Vérifiez les modules, rôles et le score de sécurité avant la génération finale." },
  { icon: FileDown, title: "Téléchargez le document", description: "Un cahier des charges complet, prêt à être partagé avec vos équipes techniques." },
];

function HowItWorks() {
  return (
    <section id="comment-ca-marche" className="border-y border-border bg-surface-2/40 py-24">
      <div className="mx-auto max-w-6xl px-4 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-xs font-semibold uppercase tracking-wide text-primary">Comment ça marche</p>
          <h2 className="mt-3 font-display text-3xl font-bold tracking-tight sm:text-4xl">Du besoin métier au document final, en 4 étapes</h2>
        </div>

        <div className="relative mt-14 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
          <div className="absolute left-0 right-0 top-6 hidden h-px bg-border lg:block" />
          {steps.map((step, i) => (
            <motion.div
              key={step.title}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.4 }}
              transition={{ duration: 0.45, delay: i * 0.1 }}
              className="relative flex flex-col items-start"
            >
              <div className="relative z-10 flex h-12 w-12 items-center justify-center rounded-2xl border-2 border-primary bg-surface font-display text-sm font-bold text-primary">
                {String(i + 1).padStart(2, "0")}
              </div>
              <step.icon className="mt-4 h-5 w-5 text-accent" />
              <h3 className="mt-2 font-display text-base font-semibold">{step.title}</h3>
              <p className="mt-1.5 text-sm text-muted-foreground">{step.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

export { HowItWorks };
