"use client";

import * as React from "react";
import { Sidebar, SidebarContent } from "@/components/layout/sidebar";
import { TopNav } from "@/components/layout/topnav";
import { MobileDrawer } from "@/components/layout/mobile-drawer";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [drawerOpen, setDrawerOpen] = React.useState(false);

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <MobileDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)}>
        <SidebarContent />
      </MobileDrawer>
      <div className="flex min-h-screen w-full flex-1 flex-col">
        <TopNav breadcrumbs={[{ label: "Tableau de bord" }]} onMenuClick={() => setDrawerOpen(true)} />
        <main className="flex-1">{children}</main>
      </div>
    </div>
  );
}
