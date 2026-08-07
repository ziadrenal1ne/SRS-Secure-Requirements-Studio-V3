"use client";

import * as React from "react";
import { AdminSidebar, AdminSidebarContent } from "@/components/layout/admin-sidebar";
import { TopNav } from "@/components/layout/topnav";
import { MobileDrawer } from "@/components/layout/mobile-drawer";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const [drawerOpen, setDrawerOpen] = React.useState(false);

  return (
    <div className="flex min-h-screen bg-background">
      <AdminSidebar />
      <MobileDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)}>
        <AdminSidebarContent />
      </MobileDrawer>
      <div className="flex min-h-screen w-full flex-1 flex-col">
        <TopNav breadcrumbs={[{ label: "Espace administration" }]} onMenuClick={() => setDrawerOpen(true)} />
        <main className="flex-1">{children}</main>
      </div>
    </div>
  );
}
