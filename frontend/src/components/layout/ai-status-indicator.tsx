"use client";

import * as React from "react";
import { AlertTriangle, Bot, CheckCircle2, Cpu, RefreshCw, Server } from "lucide-react";
import { AiHealthStatus, healthApi } from "@/lib/api";

export function AiStatusIndicator() {
  const [health, setHealth] = React.useState<AiHealthStatus | null>(null);
  const [loading, setLoading] = React.useState(true);
  const [open, setOpen] = React.useState(false);
  const popoverRef = React.useRef<HTMLDivElement>(null);

  const checkHealth = React.useCallback(async () => {
    setLoading(true);
    try {
      setHealth(await healthApi.checkAi());
    } catch {
      setHealth({
        status: "error",
        connected: false,
        model_available: false,
        provider: "unknown",
        model: "unknown",
        error: "Backend API is unreachable.",
      });
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    checkHealth();
    const timer = setInterval(checkHealth, 25000);
    return () => clearInterval(timer);
  }, [checkHealth]);

  React.useEffect(() => {
    function close(event: MouseEvent) {
      if (popoverRef.current && !popoverRef.current.contains(event.target as Node)) setOpen(false);
    }
    if (open) document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, [open]);

  const isOk = health?.status === "ok" || health?.status === "fallback";
  const isWarning = health?.status === "model_missing";
  const colorClass = loading
    ? "border-border bg-surface text-muted-foreground"
    : isOk
    ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
    : isWarning
    ? "border-amber-500/30 bg-amber-500/10 text-amber-600 dark:text-amber-400"
    : "border-rose-500/30 bg-rose-500/10 text-rose-600 dark:text-rose-400";

  return (
    <div className="relative inline-block text-left" ref={popoverRef}>
      <button
        onClick={() => setOpen((value) => !value)}
        type="button"
        title="AI provider status"
        className={`flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium shadow-sm transition-all hover:shadow ${colorClass}`}
      >
        <span className={`h-2.5 w-2.5 rounded-full ${loading ? "bg-slate-400" : isOk ? "bg-emerald-500" : isWarning ? "bg-amber-500" : "bg-rose-500"}`} />
        <Bot className="h-3.5 w-3.5" />
        <span className="hidden font-medium sm:inline">
          {loading ? "Checking AI" : isOk ? "AI Connected" : isWarning ? "Model Missing" : "AI Offline"}
        </span>
      </button>

      {open && (
        <div className="absolute right-0 z-50 mt-2 w-80 rounded-xl border border-border bg-surface p-4 shadow-xl">
          <div className="flex items-center justify-between border-b border-border pb-3">
            <div className="flex items-center gap-2">
              {isOk ? <CheckCircle2 className="h-5 w-5 text-emerald-500" /> : <AlertTriangle className="h-5 w-5 text-amber-500" />}
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">AI Engine</h4>
                <p className="text-sm font-semibold text-foreground">{isOk ? "Operational" : "Needs attention"}</p>
              </div>
            </div>
            <button onClick={checkHealth} disabled={loading} title="Refresh status" className="rounded-lg p-1.5 text-muted-foreground transition hover:bg-surface-2 hover:text-foreground">
              <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
            </button>
          </div>

          <div className="mt-3 space-y-2 text-xs">
            <div className="flex justify-between gap-3 border-b border-border/50 py-1">
              <span className="flex items-center gap-1.5 text-muted-foreground"><Cpu className="h-3.5 w-3.5" /> Provider</span>
              <span className="font-mono font-medium capitalize text-foreground">{health?.provider ?? "unknown"}</span>
            </div>
            <div className="flex justify-between gap-3 border-b border-border/50 py-1">
              <span className="flex items-center gap-1.5 text-muted-foreground"><Bot className="h-3.5 w-3.5" /> Model</span>
              <span className="truncate font-mono font-medium text-foreground">{health?.model ?? "unknown"}</span>
            </div>
            {health?.host && (
              <div className="flex justify-between gap-3 border-b border-border/50 py-1">
                <span className="flex items-center gap-1.5 text-muted-foreground"><Server className="h-3.5 w-3.5" /> Host</span>
                <span className="truncate font-mono text-[11px] text-foreground">{health.host}</span>
              </div>
            )}
            {health?.error && (
              <div className="mt-3 rounded-lg border border-amber-500/20 bg-amber-500/10 p-2.5 text-[11px] text-muted-foreground">
                {health.error}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
