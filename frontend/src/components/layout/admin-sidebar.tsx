"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { LayoutGrid, Inbox, Bell, BarChart3, ShieldHalf, ArrowLeft } from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/admin", label: "Vue d'ensemble", icon: LayoutGrid, exact: true },
  { href: "/admin#submissions", label: "Soumissions", icon: Inbox, exact: false },
  { href: "/admin#notifications", label: "Notifications", icon: Bell, exact: false },
  { href: "/admin#analytics", label: "Analytique", icon: BarChart3, exact: false },
];

function AdminSidebarContent() {
  const pathname = usePathname();

  return (
    <>
      <div className="flex h-16 items-center gap-2.5 border-b border-border px-6">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-accent">
          <ShieldHalf className="h-4.5 w-4.5 text-white" />
        </div>
        <div className="leading-tight">
          <p className="font-display text-sm font-bold">Espace admin</p>
          <p className="text-[11px] text-muted-foreground">Fondation OCP</p>
        </div>
      </div>

      <nav className="flex flex-col gap-1 p-4">
        {navItems.map((item) => {
          const active = item.exact ? pathname === "/admin" : false;
          return (
            <Link
              key={item.label}
              href={item.href}
              className={cn(
                "group relative flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-medium transition-colors",
                active ? "text-primary" : "text-muted-foreground hover:bg-surface-2 hover:text-foreground"
              )}
            >
              {active && (
                <motion.div
                  layoutId="admin-sidebar-active"
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

      <div className="mt-auto border-t border-border p-4">
        <Link
          href="/dashboard"
          className="flex items-center gap-2 rounded-xl px-3.5 py-2.5 text-sm font-medium text-muted-foreground transition-colors hover:bg-surface-2 hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
          Retour à l&apos;espace projet
        </Link>
      </div>
    </>
  );
}

function AdminSidebar() {
  return (
    <aside className="hidden w-72 shrink-0 flex-col border-r border-border bg-surface lg:flex">
      <AdminSidebarContent />
    </aside>
  );
}

export { AdminSidebar, AdminSidebarContent };
