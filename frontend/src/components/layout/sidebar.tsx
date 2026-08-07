"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { LayoutDashboard, FilePlus2, Settings, ShieldCheck, ShieldHalf, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { projects } from "@/lib/mock-data";

const navItems = [
  { href: "/dashboard", label: "Tableau de bord", icon: LayoutDashboard },
  { href: "/projects/new", label: "Nouveau projet", icon: FilePlus2 },
  { href: "/settings", label: "Parametres AI", icon: Settings },
];

function SidebarContent() {
  const pathname = usePathname();

  return (
    <>
      <div className="flex h-16 items-center gap-2.5 border-b border-border px-6">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-accent">
          <ShieldHalf className="h-4.5 w-4.5 text-white" />
        </div>
        <div className="leading-tight">
          <p className="font-display text-sm font-bold">Secure Req. Studio</p>
          <p className="text-[11px] text-muted-foreground">Fondation OCP</p>
        </div>
      </div>

      <nav className="flex flex-col gap-1 p-4">
        {navItems.map((item) => {
          const active = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "group relative flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-medium transition-colors",
                active ? "text-primary" : "text-muted-foreground hover:bg-surface-2 hover:text-foreground"
              )}
            >
              {active && (
                <motion.div
                  layoutId="sidebar-active"
                  className="absolute inset-0 rounded-xl bg-primary-soft"
                  transition={{ type: "spring", bounce: 0.2, duration: 0.5 }}
                />
              )}
              <item.icon className="relative z-10 h-4.5 w-4.5" />
              <span className="relative z-10">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="px-6 pb-3 pt-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
        Projets récents
      </div>
      <div className="flex flex-col gap-1 px-4 pb-4">
        {projects.slice(0, 4).map((p) => (
          <Link
            key={p.id}
            href={`/projects/${p.id}/summary`}
            className="group flex items-center justify-between gap-2 rounded-xl px-3.5 py-2.5 text-sm transition-colors hover:bg-surface-2"
          >
            <div className="min-w-0">
              <p className="truncate font-medium text-foreground">{p.shortName}</p>
              <p className="truncate text-xs text-muted-foreground">{p.department}</p>
            </div>
            <ChevronRight className="h-4 w-4 shrink-0 text-muted-foreground opacity-0 transition-opacity group-hover:opacity-100" />
          </Link>
        ))}
      </div>

      <div className="mt-auto border-t border-border p-4">
        <div className="flex items-center gap-2 rounded-xl bg-surface-2 px-3.5 py-3">
          <ShieldCheck className="h-4 w-4 text-accent" />
          <div className="text-xs">
            <p className="font-medium">Score sécurité moyen</p>
            <p className="text-muted-foreground">Portefeuille de projets</p>
          </div>
        </div>
      </div>
    </>
  );
}

function Sidebar() {
  return (
    <aside className="hidden w-72 shrink-0 flex-col border-r border-border bg-surface lg:flex">
      <SidebarContent />
    </aside>
  );
}

export { Sidebar, SidebarContent };
