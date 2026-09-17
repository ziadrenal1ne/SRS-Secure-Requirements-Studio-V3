"use client";

import * as React from "react";
import { motion } from "framer-motion";
import { Lightbulb, Check, CalendarDays, Info } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Radio } from "@/components/ui/radio";
import { TagInput } from "@/components/wizard/tag-input";
import { UploadZone } from "@/components/wizard/upload-zone";
import { cn } from "@/lib/utils";
import type { WizardQuestion } from "@/lib/types";

export type AnswerValue = string | string[] | null;

function QuestionCard({
  question,
  value,
  onChange,
}: {
  question: WizardQuestion;
  value: AnswerValue;
  onChange: (v: AnswerValue) => void;
}) {
  const checkboxValues = Array.isArray(value) ? value : [];
  const stringValue = typeof value === "string" ? value : "";
  const customValue = React.useMemo(() => {
    const source = Array.isArray(value) ? value.find((item) => item.startsWith("custom:")) ?? "" : stringValue.startsWith("custom:") ? stringValue : "";
    return source.replace(/^custom:/, "");
  }, [stringValue, value]);
  const commentValue = React.useMemo(() => {
    const source = Array.isArray(value) ? value.find((item) => item.startsWith("comment:")) ?? "" : "";
    return source.replace(/^comment:/, "");
  }, [value]);

  function toggleMulti(optionId: string) {
    if (checkboxValues.includes(optionId)) {
      onChange(checkboxValues.filter((v) => v !== optionId));
    } else {
      onChange([...checkboxValues, optionId]);
    }
  }

  function updateMeta(prefix: "custom:" | "comment:", next: string) {
    if (Array.isArray(value)) {
      const withoutPrevious = value.filter((item) => !item.startsWith(prefix));
      onChange(next.trim() ? [...withoutPrevious, `${prefix}${next}`] : withoutPrevious);
      return;
    }
    onChange(next.trim() ? `${prefix}${next}` : null);
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -16 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className="rounded-3xl border border-border bg-surface p-6 shadow-sm sm:p-8"
    >
      <h2 className="font-display text-xl font-semibold leading-snug tracking-tight sm:text-2xl flex items-center gap-2">
        {question.title}
        {question.required && <span className="text-primary">*</span>}
        {question.tooltip && (
          <span title={question.tooltip} className="cursor-help text-muted-foreground hover:text-foreground transition-colors">
            <Info className="h-4 w-4" />
          </span>
        )}
      </h2>
      {question.helper && <p className="mt-2 text-sm text-muted-foreground">{question.helper}</p>}
      {question.description && <p className="mt-2 text-sm leading-6 text-foreground/80">{question.description}</p>}

      {question.example && (
        <div className="mt-3 flex items-start gap-2 rounded-xl bg-primary-soft/60 px-3.5 py-2.5 text-xs text-primary">
          <Lightbulb className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          <p><span className="font-semibold">Exemple : </span>{question.example}</p>
        </div>
      )}
      {(question.recommendedAnswer || question.importance || question.dependencies?.length) && (
        <div className="mt-3 grid gap-2 rounded-xl border border-border bg-surface-2/60 px-3.5 py-3 text-xs">
          {question.recommendedAnswer && (
            <p><span className="font-semibold">Recommandation : </span>{question.recommendedAnswer}</p>
          )}
          {question.importance && (
            <p><span className="font-semibold">Importance : </span>{question.importance}</p>
          )}
          {question.dependencies?.length ? (
            <p><span className="font-semibold">Dependances : </span>{question.dependencies.join(", ")}</p>
          ) : null}
        </div>
      )}

      <div className="mt-6">
        {question.type === "text" && (
          <Input
            value={stringValue}
            onChange={(e) => onChange(e.target.value)}
            placeholder={question.placeholder}
            autoFocus
          />
        )}

        {question.type === "textarea" && (
          <Textarea
            value={stringValue}
            onChange={(e) => onChange(e.target.value)}
            placeholder={question.placeholder}
            rows={4}
            autoFocus
          />
        )}

        {question.type === "date" && (
          <div className="relative max-w-xs">
            <CalendarDays className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              type="date"
              value={stringValue}
              onChange={(e) => onChange(e.target.value)}
              className="h-11 w-full rounded-xl border border-border bg-surface pl-10 pr-3.5 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            />
          </div>
        )}

        {question.type === "select" && question.options && (
          <Select
            options={question.options.map((o) => ({ value: o.id, label: o.label }))}
            value={stringValue}
            onChange={onChange}
            className="max-w-sm"
          />
        )}

        {question.type === "upload" && (
          <UploadZone fileName={stringValue || null} onChange={(f) => onChange(f)} />
        )}

        {question.type === "radio" && question.options && (
          <div className="flex flex-col gap-2.5">
            {question.options.map((opt) => {
              const active = stringValue === opt.id;
              return (
                <label
                  key={opt.id}
                  className={cn(
                    "flex cursor-pointer items-start gap-3 rounded-xl border px-4 py-3.5 transition-colors",
                    active ? "border-primary bg-primary-soft/50" : "border-border hover:border-border-strong hover:bg-surface-2"
                  )}
                >
                  <Radio checked={active} onSelect={() => onChange(opt.id)} className="mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">{opt.label}</p>
                    {opt.description && <p className="text-xs text-muted-foreground">{opt.description}</p>}
                  </div>
                </label>
              );
            })}
          </div>
        )}

        {question.type === "checkbox" && question.options && (
          <div className="flex flex-col gap-2.5">
            {question.options.map((opt) => {
              const active = checkboxValues.includes(opt.id);
              return (
                <label
                  key={opt.id}
                  className={cn(
                    "flex cursor-pointer items-start gap-3 rounded-xl border px-4 py-3.5 transition-colors",
                    active ? "border-primary bg-primary-soft/50" : "border-border hover:border-border-strong hover:bg-surface-2"
                  )}
                >
                  <Checkbox checked={active} onCheckedChange={() => toggleMulti(opt.id)} className="mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">{opt.label}</p>
                    {opt.description && <p className="text-xs text-muted-foreground">{opt.description}</p>}
                  </div>
                </label>
              );
            })}
          </div>
        )}

        {question.type === "cards" && question.options && (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {question.options.map((opt) => {
              const active = checkboxValues.includes(opt.id);
              return (
                <button
                  type="button"
                  key={opt.id}
                  onClick={() => toggleMulti(opt.id)}
                  className={cn(
                    "relative flex flex-col items-start gap-1 rounded-2xl border p-4 text-left transition-all",
                    active ? "border-primary bg-primary-soft/50 shadow-sm" : "border-border hover:border-border-strong hover:bg-surface-2"
                  )}
                >
                  {active && (
                    <span className="absolute right-3 top-3 flex h-5 w-5 items-center justify-center rounded-full bg-primary text-white">
                      <Check className="h-3 w-3" strokeWidth={3} />
                    </span>
                  )}
                  <p className="pr-6 text-sm font-semibold">{opt.label}</p>
                  {opt.description && <p className="text-xs text-muted-foreground">{opt.description}</p>}
                </button>
              );
            })}
          </div>
        )}

        {question.type === "tags" && (
          <TagInput value={checkboxValues} onChange={onChange} />
        )}

        {question.options && question.type !== "text" && question.type !== "textarea" && (
          <div className="mt-5 grid gap-3 border-t border-border pt-4">
            <label className="grid gap-1.5 text-sm font-medium">
              Réponse personnalisée
              <Textarea
                value={customValue}
                onChange={(event) => updateMeta("custom:", event.target.value)}
                placeholder={question.customPrompt ?? "Écrivez votre propre réponse si les choix ne couvrent pas le besoin."}
                rows={3}
              />
            </label>
            <label className="grid gap-1.5 text-sm font-medium">
              Commentaires optionnels
              <Textarea
                value={commentValue}
                onChange={(event) => updateMeta("comment:", event.target.value)}
                placeholder="Précisions, contraintes, exceptions, règles internes..."
                rows={2}
              />
            </label>
          </div>
        )}
      </div>
    </motion.div>
  );
}

export { QuestionCard };
