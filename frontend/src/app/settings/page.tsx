"use client";

import * as React from "react";
import Link from "next/link";
import { ArrowLeft, CheckCircle2, Eye, EyeOff, Loader2, PlugZap, Save, XCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import {
  AIProviderSettings,
  defaultAIProviderSettings,
  fetchAIProviderSettings,
  saveAIProviderSettings,
  testAIProviderConnection,
} from "@/lib/ai-provider-settings";

export default function SettingsPage() {
  const [settings, setSettings] = React.useState<AIProviderSettings>(defaultAIProviderSettings);
  const [status, setStatus] = React.useState("Not tested");
  const [testing, setTesting] = React.useState(false);
  const [saving, setSaving] = React.useState(false);
  const [showKey, setShowKey] = React.useState(false);

  React.useEffect(() => {
    fetchAIProviderSettings().then(setSettings);
  }, []);

  function update<K extends keyof AIProviderSettings>(key: K, value: AIProviderSettings[K]) {
    setSettings((current) => ({ ...current, [key]: value }));
  }

  async function testConnection() {
    setTesting(true);
    const result = await testAIProviderConnection(settings);
    setStatus(result.connected ? "Connected" : `Connection failed: ${result.error ?? "unknown error"}`);
    setTesting(false);
  }

  async function saveSettings() {
    setSaving(true);
    try {
      const saved = await saveAIProviderSettings(settings);
      setSettings(saved);
      setStatus("Configuration saved");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Configuration could not be saved");
    } finally {
      setSaving(false);
    }
  }

  const isGemini = settings.provider === "gemini";

  return (
    <main className="min-h-screen bg-background">
      <header className="flex h-16 items-center gap-4 border-b border-border bg-surface/80 px-4 backdrop-blur-md lg:px-8">
        <Link href="/" className="text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <p className="text-sm font-semibold">AI Providers</p>
          <p className="text-xs text-muted-foreground">Choisir le fournisseur IA et vérifier la connexion.</p>
        </div>
      </header>

      <section className="mx-auto grid max-w-3xl gap-5 px-4 py-10">
        <label className="grid gap-1.5 text-sm font-medium">
          Fournisseur
          <Select
            value={settings.provider}
            onChange={(value) => update("provider", value as AIProviderSettings["provider"])}
            options={[
              { value: "template", label: "Questionnaire guidé" },
              { value: "gemini", label: "Google Gemini" },
            ]}
          />
        </label>


        {isGemini && (
          <>
            <label className="grid gap-1.5 text-sm font-medium">
              Clé API
              <div className="flex gap-2">
                <Input
                  type={showKey ? "text" : "password"}
                  value={settings.gemini_api_key ?? ""}
                  placeholder={settings.gemini_api_key_configured ? "Clé configurée" : "Coller la clé API Gemini"}
                  onChange={(event) => update("gemini_api_key", event.target.value)}
                />
                <Button type="button" variant="outline" size="icon" onClick={() => setShowKey((value) => !value)} aria-label="Show or hide API key">
                  {showKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </Button>
              </div>
            </label>
            <label className="grid gap-1.5 text-sm font-medium">
              Modèle
              <Input value={settings.gemini_model} onChange={(event) => update("gemini_model", event.target.value)} />
            </label>
          </>
        )}

        <div className="flex flex-wrap items-center gap-3 rounded-xl border border-border bg-surface p-4">
          <div className="flex items-center gap-2 text-sm">
            {status.startsWith("Connection failed") ? <XCircle className="h-4 w-4 text-destructive" /> : <CheckCircle2 className="h-4 w-4 text-accent" />}
            Statut : <span className="font-semibold">{status}</span>
          </div>
          <div className="ml-auto flex gap-2">
            <Button type="button" variant="outline" onClick={testConnection} disabled={testing} className="gap-2">
              {testing ? <Loader2 className="h-4 w-4 animate-spin" /> : <PlugZap className="h-4 w-4" />}
              Vérifier la connexion
            </Button>
            <Button type="button" onClick={saveSettings} disabled={saving} className="gap-2">
              {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
              Enregistrer
            </Button>
          </div>
        </div>
      </section>
    </main>
  );
}
