"use client";

import { motion } from "framer-motion";
import { MessagesSquare, ShieldCheck, Zap, History, type LucideIcon } from "lucide-react";

const features: { icon: LucideIcon; title: string; description: string }[] = [
  {
    icon: MessagesSquare,
    title: "Questionnaire conversationnel",
    description: "Chaque question s'adapte à vos réponses précédentes — pas de formulaire figé, juste les questions qui comptent pour votre projet.",
  },
  {
    icon: ShieldCheck,
    title: "Cybersécurité intégrée",
    description: "RBAC, chiffrement, authentification forte et journalisation sont proposés automatiquement selon la sensibilité de vos données.",
  },
  {
    icon: Zap,
    title: "Généré en quelques minutes",
    description: "Ce qui prenait des semaines d'allers-retours avec les équipes techniques tient désormais dans une session guidée.",
  },
  {
    icon: History,
    title: "Traçabilité complète",
    description: "Historique des versions, commentaires et statut de validation pour chaque cahier des charges produit.",
  },
];

function Features() {
  return (
    <section id="fonctionnalites" className="mx-auto max-w-6xl px-4 py-24 lg:px-8">
      <div className="mx-auto max-w-2xl text-center">
        <p className="text-xs font-semibold uppercase tracking-wide text-primary">Fonctionnalités</p>
        <h2 className="mt-3 font-display text-3xl font-bold tracking-tight sm:text-4xl">
          Un studio pensé pour les porteurs de projet
        </h2>
        <p className="mt-3 text-muted-foreground">
          Aucune expertise technique requise pour produire un cahier des charges exploitable par vos équipes IT.
        </p>
      </div>

      <div className="mt-14 grid grid-cols-1 gap-5 sm:grid-cols-2">
        {features.map((f, i) => (
          <motion.div
            key={f.title}
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.4 }}
            transition={{ duration: 0.45, delay: i * 0.08 }}
            className="group rounded-2xl border border-border bg-surface p-6 transition-colors hover:border-border-strong"
          >
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary-soft text-primary transition-transform group-hover:scale-105">
              <f.icon className="h-5 w-5" />
            </div>
            <h3 className="mt-4 font-display text-base font-semibold">{f.title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{f.description}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}

export { Features };
