"use client";

import Link from "next/link";
import * as React from "react";
import { ShieldHalf, Menu, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { cn } from "@/lib/utils";

const links = [
  { href: "#fonctionnalites", label: "Fonctionnalités" },
  { href: "#comment-ca-marche", label: "Comment ça marche" },
  { href: "#securite", label: "Sécurité" },
  { href: "#temoignages", label: "Témoignages" },
];

function Navbar() {
  const [scrolled, setScrolled] = React.useState(false);
  const [mobileOpen, setMobileOpen] = React.useState(false);

  React.useEffect(() => {
    function onScroll() {
      setScrolled(window.scrollY > 12);
    }
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <header
      className={cn(
        "sticky top-0 z-40 transition-all duration-300",
        scrolled ? "border-b border-border bg-surface/80 backdrop-blur-md" : "border-b border-transparent bg-transparent"
      )}
    >
      <div className="mx-auto flex h-16 max-w-7xl items-center gap-6 px-4 lg:px-8">
        <Link href="/" className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-accent">
            <ShieldHalf className="h-4.5 w-4.5 text-white" />
          </div>
          <div className="leading-tight">
            <p className="font-display text-sm font-bold">Secure Requirements Studio</p>
            <p className="text-[10px] text-muted-foreground">Fondation OCP</p>
          </div>
        </Link>

        <nav className="ml-4 hidden items-center gap-1 md:flex">
          {links.map((l) => (
            <a key={l.href} href={l.href} className="rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-surface-2 hover:text-foreground">
              {l.label}
            </a>
          ))}
        </nav>

        <div className="ml-auto hidden items-center gap-3 md:flex">
          <ThemeToggle />
          <Link href="/dashboard"><Button variant="secondary">Se connecter</Button></Link>
          <Link href="/projects/new"><Button>Démarrer un projet</Button></Link>
        </div>

        <button onClick={() => setMobileOpen((o) => !o)} className="ml-auto flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground md:hidden">
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {mobileOpen && (
        <div className="border-t border-border bg-surface px-4 py-4 md:hidden">
          <div className="flex flex-col gap-1">
            {links.map((l) => (
              <a key={l.href} href={l.href} onClick={() => setMobileOpen(false)} className="rounded-lg px-3 py-2.5 text-sm font-medium text-muted-foreground hover:bg-surface-2 hover:text-foreground">
                {l.label}
              </a>
            ))}
          </div>
          <div className="mt-3 flex flex-col gap-2 border-t border-border pt-3">
            <Link href="/dashboard"><Button variant="secondary" className="w-full">Se connecter</Button></Link>
            <Link href="/projects/new"><Button className="w-full">Démarrer un projet</Button></Link>
          </div>
        </div>
      )}
    </header>
  );
}

export { Navbar };
