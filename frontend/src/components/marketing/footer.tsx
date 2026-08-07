import Link from "next/link";
import { ShieldHalf } from "lucide-react";

const columns = [
  {
    title: "Produit",
    links: [
      { label: "Fonctionnalités", href: "#fonctionnalites" },
      { label: "Tableau de bord", href: "/dashboard" },
      { label: "Nouveau projet", href: "/projects/new" },
      { label: "Espace administration", href: "/admin" },
    ],
  },
  {
    title: "Sécurité",
    links: [
      { label: "Cybersécurité par conception", href: "#securite" },
      { label: "Comment ça marche", href: "#comment-ca-marche" },
    ],
  },
  {
    title: "Fondation OCP",
    links: [
      { label: "Direction Digital & Innovation", href: "#" },
      { label: "Programme Al Moutmir", href: "#" },
    ],
  },
];

function Footer() {
  return (
    <footer className="bg-surface">
      <div className="mx-auto max-w-6xl px-4 py-16 lg:px-8">
        <div className="grid grid-cols-2 gap-8 sm:grid-cols-4">
          <div className="col-span-2 sm:col-span-1">
            <Link href="/" className="flex items-center gap-2.5">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-accent">
                <ShieldHalf className="h-4.5 w-4.5 text-white" />
              </div>
              <p className="font-display text-sm font-bold">Secure Req. Studio</p>
            </Link>
            <p className="mt-3 text-sm text-muted-foreground">
              Transformez vos besoins métier en cahiers des charges sécurisés.
            </p>
          </div>
          {columns.map((col) => (
            <div key={col.title}>
              <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{col.title}</p>
              <ul className="mt-3 flex flex-col gap-2.5">
                {col.links.map((l) => (
                  <li key={l.label}>
                    <Link href={l.href} className="text-sm text-muted-foreground transition-colors hover:text-foreground">
                      {l.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-border pt-6 sm:flex-row">
          <p className="text-xs text-muted-foreground">© 2026 Fondation OCP — Outil interne, Direction Digital &amp; Innovation.</p>
          <p className="text-xs text-muted-foreground">Prototype frontend — Secure Requirements Studio</p>
        </div>
      </div>
    </footer>
  );
}

export { Footer };
