"use client";

import * as React from "react";
import { Menu } from "lucide-react";
import { Breadcrumbs } from "@/components/ui/breadcrumbs";
import { SearchBar } from "@/components/ui/search-bar";
import { NotificationMenu } from "@/components/ui/notification-menu";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { AiStatusIndicator } from "@/components/layout/ai-status-indicator";
import { Avatar } from "@/components/ui/avatar";
import { notifications, currentUser } from "@/lib/mock-data";

function TopNav({
  breadcrumbs,
  onMenuClick,
}: {
  breadcrumbs: { label: string; href?: string }[];
  onMenuClick?: () => void;
}) {
  const [query, setQuery] = React.useState("");

  return (
    <header className="sticky top-0 z-20 flex h-16 shrink-0 items-center gap-4 border-b border-border bg-surface/80 px-4 backdrop-blur-md lg:px-8">
      <button onClick={onMenuClick} className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground hover:bg-surface-2 lg:hidden">
        <Menu className="h-5 w-5" />
      </button>
      <Breadcrumbs items={breadcrumbs} />
      <div className="ml-auto flex items-center gap-3">
        <SearchBar value={query} onChange={setQuery} placeholder="Rechercher un projet…" className="hidden w-64 md:block" />
        <AiStatusIndicator />
        <NotificationMenu items={notifications} />
        <ThemeToggle />
        <div className="hidden items-center gap-2.5 border-l border-border pl-3 sm:flex">
          <Avatar initials={currentUser.initials} size="sm" />
          <div className="leading-tight">
            <p className="text-xs font-semibold">{currentUser.name}</p>
            <p className="text-[11px] text-muted-foreground">{currentUser.role}</p>
          </div>
        </div>
      </div>
    </header>
  );
}

export { TopNav };
