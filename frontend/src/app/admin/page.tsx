"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  Inbox,
  FileCheck2,
  Percent,
  FileClock,
  Download,
  Sparkles,
  Eye,
  CheckCircle2,
  AlertTriangle,
  Info,
} from "lucide-react";
import { StatCard } from "@/components/dashboard/stat-card";
import { StatusChip } from "@/components/ui/status-chip";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table";
import {
  GeneratedDocumentsChart,
  DepartmentDistributionChart,
  SecurityScoreTrendChart,
  pieColors,
} from "@/components/admin/analytics-charts";
import { adminSubmissions, notifications, departmentDistribution, dashboardStats } from "@/lib/mock-data";
import { formatDateTime } from "@/lib/utils";

const notifIcon = {
  success: <CheckCircle2 className="h-4 w-4 text-accent" />,
  warning: <AlertTriangle className="h-4 w-4 text-warning" />,
  info: <Info className="h-4 w-4 text-primary" />,
};

export default function AdminDashboardPage() {
  const avgCompleteness = Math.round(
    adminSubmissions.reduce((sum, s) => sum + s.completeness, 0) / adminSubmissions.length
  );

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 lg:px-8">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="font-display text-2xl font-bold tracking-tight">Vue d&apos;ensemble</h1>
          <p className="mt-1 text-sm text-muted-foreground">Pilotage des projets soumis par les départements de la Fondation.</p>
        </div>
        <Button variant="secondary" className="gap-2">
          <Download className="h-4 w-4" />
          Exporter le rapport
        </Button>
      </div>

      <div className="mt-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Projets au total" value={dashboardStats.totalProjects} icon={Inbox} accent="primary" />
        <StatCard label="Soumissions en revue" value={adminSubmissions.filter((s) => s.status === "en_revue").length} icon={FileClock} accent="warning" delay={0.05} />
        <StatCard label="Complétude moyenne" value={avgCompleteness} suffix="%" icon={Percent} accent="accent" delay={0.1} />
        <StatCard label="Documents générés" value={dashboardStats.requirementsGenerated} icon={FileCheck2} accent="primary" delay={0.15} />
      </div>

      {/* Submissions */}
      <div id="submissions" className="mt-10 scroll-mt-24">
        <h2 className="font-display text-lg font-semibold">Soumissions récentes</h2>
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.35 }} className="mt-4">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Projet</TableHead>
                <TableHead>Soumis par</TableHead>
                <TableHead>Département</TableHead>
                <TableHead>Date</TableHead>
                <TableHead>Complétude</TableHead>
                <TableHead>Statut</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {adminSubmissions.map((s) => (
                <TableRow key={s.id}>
                  <TableCell className="font-medium">{s.projectName}</TableCell>
                  <TableCell className="text-muted-foreground">{s.submittedBy}</TableCell>
                  <TableCell className="text-muted-foreground">{s.department}</TableCell>
                  <TableCell className="text-muted-foreground">{formatDateTime(s.submittedAt)}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Progress value={s.completeness} className="w-20" />
                      <span className="text-xs text-muted-foreground">{s.completeness}%</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <StatusChip status={s.status} />
                  </TableCell>
                  <TableCell>
                    <div className="flex justify-end gap-1.5">
                      <Link href={`/admin/projects/${s.projectId}`}>
                        <Button variant="ghost" size="icon" aria-label="Voir le projet">
                          <Eye className="h-4 w-4" />
                        </Button>
                      </Link>
                      <Button variant="ghost" size="icon" aria-label="Générer la documentation">
                        <Sparkles className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" aria-label="Télécharger">
                        <Download className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </motion.div>
      </div>

      <div className="mt-10 grid grid-cols-1 gap-8 xl:grid-cols-3">
        {/* Notifications */}
        <div id="notifications" className="scroll-mt-24">
          <h2 className="font-display text-lg font-semibold">Notifications</h2>
          <div className="mt-4 rounded-2xl border border-border bg-surface">
            {notifications.map((n, i) => (
              <div key={n.id} className={`flex gap-3 px-5 py-4 ${i !== notifications.length - 1 ? "border-b border-border" : ""}`}>
                <div className="mt-0.5">{notifIcon[n.type]}</div>
                <div className="min-w-0">
                  <p className="text-sm font-medium">{n.title}</p>
                  <p className="mt-0.5 text-xs text-muted-foreground">{n.description}</p>
                  <p className="mt-1 text-[11px] text-muted-foreground">{n.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Analytics */}
        <div id="analytics" className="scroll-mt-24 xl:col-span-2">
          <h2 className="font-display text-lg font-semibold">Analytique</h2>
          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-border bg-surface p-5">
              <p className="text-sm font-semibold">Documents générés / mois</p>
              <GeneratedDocumentsChart />
            </div>
            <div className="rounded-2xl border border-border bg-surface p-5">
              <p className="text-sm font-semibold">Score de sécurité moyen</p>
              <SecurityScoreTrendChart />
            </div>
            <div className="rounded-2xl border border-border bg-surface p-5 sm:col-span-2">
              <p className="text-sm font-semibold">Répartition des projets par département</p>
              <div className="flex flex-col items-center gap-4 sm:flex-row">
                <div className="w-full sm:w-1/2">
                  <DepartmentDistributionChart />
                </div>
                <div className="flex w-full flex-col gap-2 sm:w-1/2">
                  {departmentDistribution.map((d, i) => (
                    <div key={d.name} className="flex items-center justify-between text-sm">
                      <span className="flex items-center gap-2">
                        <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: pieColors[i % pieColors.length] }} />
                        {d.name}
                      </span>
                      <span className="font-medium text-muted-foreground">{d.value} projet{d.value > 1 ? "s" : ""}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
