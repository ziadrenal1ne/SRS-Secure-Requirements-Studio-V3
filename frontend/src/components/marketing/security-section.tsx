"use client";

import { motion } from "framer-motion";
import { KeyRound, Lock, ShieldCheck, ScrollText } from "lucide-react";
import { ScoreRing } from "@/components/ui/score-ring";

const pillars = [
  { icon: KeyRound, title: "Authentification forte", description: "MFA recommandé automatiquement pour les profils sensibles, selon le niveau de confidentialité déclaré." },
  { icon: Lock, title: "Chiffrement de bout en bout", description: "Chiffrement au repos et en transit exigé dès qu'une donnée personnelle est manipulée." },
  { icon: ShieldCheck, title: "Contrôle d'accès par rôles", description: "Chaque rôle détecté reçoit un périmètre de permissions selon le principe du moindre privilège." },
  { icon: ScrollText, title: "Journalisation & audit", description: "Traçabilité des accès aux données confidentielles, conservée selon la politique de la Fondation." },
];

const floatingBadges = [
  { label: "AES-256", className: "left-[6%] top-[10%]", delay: "0s" },
  { label: "MFA", className: "right-[4%] top-[22%]", delay: "1.2s" },
  { label: "RBAC", className: "left-[2%] bottom-[16%]", delay: "0.6s" },
  { label: "Audit 12 mois", className: "right-[8%] bottom-[6%]", delay: "1.8s" },
];

function SecuritySection() {
  return (
    <section id="securite" className="mx-auto max-w-6xl px-4 py-24 lg:px-8">
      <div className="grid grid-cols-1 items-center gap-14 lg:grid-cols-2">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-accent">Cybersécurité par conception</p>
          <h2 className="mt-3 font-display text-3xl font-bold tracking-tight sm:text-4xl">
            La sécurité n&apos;est pas une option ajoutée après coup
          </h2>
          <p className="mt-3 text-muted-foreground">
            Chaque cahier des charges généré intègre nativement les contrôles recommandés par la politique de
            sécurité de la Fondation OCP.
          </p>

          <div className="mt-8 flex flex-col gap-6">
            {pillars.map((p, i) => (
              <motion.div
                key={p.title}
                initial={{ opacity: 0, x: -12 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true, amount: 0.5 }}
                transition={{ duration: 0.4, delay: i * 0.08 }}
                className="flex gap-4 border-l-2 border-accent/30 pl-4"
              >
                <p.icon className="mt-0.5 h-5 w-5 shrink-0 text-accent" />
                <div>
                  <h3 className="font-display text-sm font-semibold">{p.title}</h3>
                  <p className="mt-1 text-sm text-muted-foreground">{p.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        <motion.div
          initial={{ opacity: 0, scale: 0.92 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true, amount: 0.4 }}
          transition={{ duration: 0.5 }}
          className="relative mx-auto flex h-80 w-80 items-center justify-center rounded-full bg-radial-fade sm:h-96 sm:w-96"
        >
          <div className="rounded-full border border-border bg-surface p-10 shadow-xl">
            <ScoreRing score={88} size={180} strokeWidth={14} label="score sécurité moyen" />
          </div>
          {floatingBadges.map((b) => (
            <span
              key={b.label}
              style={{ animationDelay: b.delay }}
              className={`animate-float absolute rounded-full border border-border bg-surface px-3 py-1.5 text-xs font-medium shadow-sm ${b.className}`}
            >
              {b.label}
            </span>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

export { SecuritySection };
