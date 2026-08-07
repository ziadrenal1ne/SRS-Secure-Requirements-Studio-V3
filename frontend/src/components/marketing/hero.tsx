"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, PlayCircle, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { TransformDemo } from "./transform-demo";

function Hero() {
  return (
    <section className="relative overflow-hidden bg-grid bg-radial-fade">
      <div className="mx-auto max-w-6xl px-4 pb-20 pt-16 text-center sm:pt-24 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mx-auto inline-flex items-center gap-2 rounded-full border border-border bg-surface px-3.5 py-1.5 text-xs font-medium text-muted-foreground"
        >
          <Sparkles className="h-3.5 w-3.5 text-primary" />
          Direction Digital &amp; Innovation — Fondation OCP
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.05 }}
          className="text-balance mx-auto mt-6 max-w-3xl font-display text-4xl font-bold leading-[1.1] tracking-tight sm:text-5xl lg:text-6xl"
        >
          Transformez vos besoins métier en{" "}
          <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            cahiers des charges sécurisés
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.1 }}
          className="text-balance mx-auto mt-5 max-w-xl text-base text-muted-foreground sm:text-lg"
        >
          Décrivez votre projet en répondant à un questionnaire guidé. Secure Requirements Studio structure vos
          réponses en un cahier des charges complet, avec les exigences de cybersécurité déjà intégrées.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.15 }}
          className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row"
        >
          <Link href="/projects/new">
            <Button size="lg" className="gap-2">
              Démarrer un nouveau projet
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <Link href="/dashboard">
            <Button size="lg" variant="secondary" className="gap-2">
              <PlayCircle className="h-4 w-4" />
              Explorer le tableau de bord
            </Button>
          </Link>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.25 }}
          className="mt-16"
        >
          <TransformDemo />
        </motion.div>
      </div>
    </section>
  );
}

export { Hero };
