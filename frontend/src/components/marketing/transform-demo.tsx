"use client";

import { motion } from "framer-motion";
import { Sparkles, ShieldCheck, Users, ListChecks, MessageSquare } from "lucide-react";

const outputChips = [
  { code: "FR-01", label: "Inscription d'un bénéficiaire", icon: ListChecks, tone: "primary" as const },
  { code: "RBAC", label: "4 rôles détectés", icon: Users, tone: "accent" as const },
  { code: "SEC-02", label: "Chiffrement des données", icon: ShieldCheck, tone: "danger" as const },
  { code: "SEC-01", label: "Authentification MFA", icon: ShieldCheck, tone: "warning" as const },
];

const toneClasses = {
  primary: "border-l-primary bg-primary-soft/40",
  accent: "border-l-accent bg-accent-soft/40",
  danger: "border-l-danger bg-danger-soft/50",
  warning: "border-l-warning bg-warning-soft/50",
};

function TransformDemo() {
  return (
    <motion.div
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, amount: 0.4 }}
      variants={{ hidden: {}, show: { transition: { staggerChildren: 0.12, delayChildren: 0.1 } } }}
      className="glass relative mx-auto grid w-full max-w-3xl grid-cols-1 items-center gap-4 rounded-3xl p-5 sm:grid-cols-[1fr_auto_1fr] sm:p-6"
    >
      {/* Input */}
      <motion.div
        variants={{ hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0, transition: { duration: 0.5 } } }}
        className="rounded-2xl border border-border bg-surface p-4"
      >
        <p className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
          <MessageSquare className="h-3 w-3" /> Besoin métier
        </p>
        <p className="mt-2 text-sm leading-relaxed text-foreground">
          « Nous devons recenser les agriculteurs bénéficiaires d&apos;Al Moutmir et suivre leurs campagnes, avec
          import de fichiers CSV terrain. »
        </p>
      </motion.div>

      {/* Arrow / processing */}
      <motion.div
        variants={{ hidden: { opacity: 0, scale: 0.7 }, show: { opacity: 1, scale: 1, transition: { duration: 0.4 } } }}
        className="flex flex-row items-center justify-center gap-2 sm:flex-col"
      >
        <div className="animate-pulse-ring flex h-11 w-11 items-center justify-center rounded-full bg-gradient-to-br from-primary to-accent text-white">
          <Sparkles className="h-5 w-5" />
        </div>
        <span className="text-[10px] font-medium text-muted-foreground">Studio</span>
      </motion.div>

      {/* Output */}
      <div className="flex flex-col gap-2">
        <p className="text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">
          Exigences générées
        </p>
        {outputChips.map((chip) => (
          <motion.div
            key={chip.code}
            variants={{ hidden: { opacity: 0, x: 14 }, show: { opacity: 1, x: 0, transition: { duration: 0.4 } } }}
            className={`flex items-center gap-2.5 rounded-xl border-l-4 bg-surface px-3 py-2 ${toneClasses[chip.tone]}`}
          >
            <chip.icon className="h-3.5 w-3.5 shrink-0 text-foreground" />
            <span className="font-mono text-[10px] font-semibold text-muted-foreground">{chip.code}</span>
            <span className="truncate text-xs font-medium">{chip.label}</span>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}

export { TransformDemo };
