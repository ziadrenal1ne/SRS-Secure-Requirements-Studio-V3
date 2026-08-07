"use client";

import { motion } from "framer-motion";
import { Quote } from "lucide-react";
import { Avatar } from "@/components/ui/avatar";

const testimonials = [
  {
    quote: "J'ai pu cadrer le projet Al Moutmir en une matinée, sans attendre un créneau avec l'équipe technique. Le questionnaire pose exactement les bonnes questions.",
    name: "Salma Idrissi",
    role: "Cheffe de Programme Al Moutmir",
    initials: "SI",
  },
  {
    quote: "Ce que j'apprécie le plus, c'est que les exigences de sécurité arrivent déjà rédigées. Je n'ai plus à deviner ce que l'équipe cybersécurité va demander en revue.",
    name: "Nadia Berrada",
    role: "Cheffe de Projet Entrepreneuriat",
    initials: "NB",
  },
  {
    quote: "Le résumé avec les rôles et le score de sécurité m'a permis de valider le périmètre du projet directement avec ma direction, sans document intermédiaire.",
    name: "Yassine Bennani",
    role: "Responsable Programme Bourses",
    initials: "YB",
  },
];

function Testimonials() {
  return (
    <section id="temoignages" className="border-y border-border bg-surface-2/40 py-24">
      <div className="mx-auto max-w-6xl px-4 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-xs font-semibold uppercase tracking-wide text-primary">Témoignages</p>
          <h2 className="mt-3 font-display text-3xl font-bold tracking-tight sm:text-4xl">Adopté par les porteurs de projet de la Fondation</h2>
        </div>

        <div className="mt-14 grid grid-cols-1 gap-5 md:grid-cols-3">
          {testimonials.map((t, i) => (
            <motion.div
              key={t.name}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.4 }}
              transition={{ duration: 0.45, delay: i * 0.1 }}
              className="flex flex-col rounded-2xl border border-border bg-surface p-6"
            >
              <Quote className="h-5 w-5 text-primary/50" />
              <p className="mt-3 flex-1 text-sm leading-relaxed text-foreground">{t.quote}</p>
              <div className="mt-5 flex items-center gap-3 border-t border-border pt-4">
                <Avatar initials={t.initials} size="sm" />
                <div>
                  <p className="text-sm font-semibold">{t.name}</p>
                  <p className="text-xs text-muted-foreground">{t.role}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

export { Testimonials };
