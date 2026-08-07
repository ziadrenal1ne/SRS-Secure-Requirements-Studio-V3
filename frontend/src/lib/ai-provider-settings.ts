"use client";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";
const STORAGE_KEY = "srs_ai_provider_settings";

export type AIProvider = "template" | "gemini";

export interface AIProviderSettings {
  provider: AIProvider;
  gemini_api_key?: string;
  gemini_api_key_configured?: boolean;
  gemini_model: string;
  gemini_temperature: number;
  gemini_top_p: number;
  gemini_max_output_tokens: number;
  gemini_timeout_seconds: number;
  gemini_enable_streaming: boolean;
}

export interface AIConnectionStatus {
  status: "ok" | "model_missing" | "error" | "fallback";
  connected: boolean;
  model_available: boolean;
  provider: string;
  model: string;
  host?: string;
  installed_models?: string[];
  error?: string | null;
}

export const defaultAIProviderSettings: AIProviderSettings = {
  provider: "template",
  gemini_api_key: "",
  gemini_api_key_configured: false,
  gemini_model: "gemini-2.5-flash",
  gemini_temperature: 0.2,
  gemini_top_p: 0.95,
  gemini_max_output_tokens: 2048,
  gemini_timeout_seconds: 60,
  gemini_enable_streaming: false,
};

function withDefaults(value: Partial<AIProviderSettings>): AIProviderSettings {
  return { ...defaultAIProviderSettings, ...value };
}

export function loadLocalAIProviderSettings(): AIProviderSettings {
  if (typeof window === "undefined") return defaultAIProviderSettings;
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) return defaultAIProviderSettings;
  try {
    return withDefaults(JSON.parse(raw));
  } catch {
    return defaultAIProviderSettings;
  }
}

export function saveLocalAIProviderSettings(settings: AIProviderSettings) {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
}

export async function fetchAIProviderSettings(): Promise<AIProviderSettings> {
  const response = await fetch(`${API_BASE_URL}/ai/settings`);
  if (!response.ok) return loadLocalAIProviderSettings();
  return withDefaults(await response.json());
}

export async function saveAIProviderSettings(settings: AIProviderSettings): Promise<AIProviderSettings> {
  saveLocalAIProviderSettings(settings);
  const response = await fetch(`${API_BASE_URL}/ai/settings`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(settings),
  });
  if (!response.ok) throw new Error("Unable to save AI provider settings.");
  const saved = withDefaults(await response.json());
  saveLocalAIProviderSettings(saved);
  return saved;
}

export async function testAIProviderConnection(settings: AIProviderSettings): Promise<AIConnectionStatus> {
  const response = await fetch(`${API_BASE_URL}/ai/test`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(settings),
  });
  if (!response.ok) {
    return {
      status: "error",
      connected: false,
      model_available: false,
      provider: settings.provider,
      model: settings.provider === "gemini" ? settings.gemini_model : "template-heuristic",
      error: `Connection test failed (${response.status}).`,
    };
  }
  return response.json();
}
