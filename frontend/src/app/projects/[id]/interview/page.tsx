"use client";

import * as React from "react";
import Link from "next/link";
import { useParams, useSearchParams } from "next/navigation";
import { ArrowRight, FileText, Loader2, Sparkles, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ProjectSubNav } from "@/components/project/project-subnav";
import { QuestionCard, type AnswerValue } from "@/components/wizard/question-card";
import { Stepper } from "@/components/wizard/stepper";
import { wizardSteps } from "@/lib/questionnaire";
import { ApiError, documentsApi, healthApi, interviewApi, knowledgeGraphApi, type ProjectCompletion } from "@/lib/api";
import { buildLocalDocument, saveLocalAnswers, saveLocalDocument } from "@/lib/local-document";
import type { WizardQuestion } from "@/lib/types";

export default function ProjectInterviewPage() {
  const params = useParams<{ id: string }>();
  const searchParams = useSearchParams();
  const projectId = params.id;
  const requestedMode = searchParams.get("mode") === "ai" ? "ai" : "classic";

  const [mode, setMode] = React.useState<"classic" | "ai">(requestedMode);
  const [loading, setLoading] = React.useState(requestedMode === "ai");
  const [error, setError] = React.useState<string | null>(null);
  const [status, setStatus] = React.useState<"active" | "completed">("active");
  const [submitting, setSubmitting] = React.useState(false);
  const [conceptKey, setConceptKey] = React.useState<string | null>(null);
  const [question, setQuestion] = React.useState<string | null>(null);
  const [questionOptions, setQuestionOptions] = React.useState<string[]>([]);
  const [section, setSection] = React.useState<string | null>(null);
  const [answer, setAnswer] = React.useState("");
  const [note, setNote] = React.useState<string | null>(null);
  const [completion, setCompletion] = React.useState<ProjectCompletion | null>(null);
  const [turnsAnswered, setTurnsAnswered] = React.useState(0);
  const [stepIndex, setStepIndex] = React.useState(0);
  const [questionIndex, setQuestionIndex] = React.useState(0);
  const [classicAnswer, setClassicAnswer] = React.useState<AnswerValue>(null);
  const [classicAnswers, setClassicAnswers] = React.useState<Record<string, AnswerValue>>({});
  const [aiConnection, setAiConnection] = React.useState<"checking" | "connected" | "failed" | null>(requestedMode === "ai" ? "checking" : null);
  const [backendAvailable, setBackendAvailable] = React.useState(true);

  const refreshCompletion = React.useCallback(async () => {
    try {
      setCompletion(await knowledgeGraphApi.completion(projectId));
    } catch {
      setCompletion(null);
    }
  }, [projectId]);

  React.useEffect(() => {
    (async () => {
      setLoading(requestedMode === "ai");
      try {
        if (requestedMode === "ai") {
          const ai = await healthApi.checkAi();
          if (!ai.connected || ai.status === "error" || ai.status === "model_missing") {
            setAiConnection("failed");
            setError(`Assistant IA indisponible. Cause : ${ai.error ?? "fournisseur ou modèle inaccessible"}. Vous pouvez continuer avec le questionnaire guidé.`);
            setMode("classic");
          } else {
            setAiConnection("connected");
          }
        }
        const session = await interviewApi.start(projectId);
        setTurnsAnswered(session.turns.length);
        setConceptKey(session.pending_concept_key);
        setQuestion(session.pending_question);
        setQuestionOptions(session.pending_question_options ?? []);
        setSection(session.pending_section);
        if (session.status === "completed") setStatus("completed");
        await refreshCompletion();
      } catch (err) {
        setAiConnection("failed");
        setBackendAvailable(false);
        setError(requestedMode === "ai" ? (err instanceof ApiError ? err.message : "Impossible de contacter le fournisseur sélectionné. Vérifiez la clé API, la connexion réseau ou la configuration.") : null);
        setMode("classic");
      } finally {
        setLoading(false);
      }
    })();
  }, [projectId, refreshCompletion, requestedMode]);

  async function handleClassicNext() {
    const currentStep = wizardSteps[stepIndex];
    const lastQuestion = questionIndex >= currentStep.questions.length - 1;
    const lastStep = stepIndex >= wizardSteps.length - 1;
    
    if (classicAnswer) {
      const answerStr = Array.isArray(classicAnswer) ? classicAnswer.join(", ") : classicAnswer;
      try {
        await interviewApi.answer(projectId, answerStr);
      } catch (e) {
        setBackendAvailable(false);
        if (!(e instanceof ApiError && e.status === 409)) {
          console.error("Failed to save answer to graph", e);
        }
      }
    }

    const nextAnswers = { ...classicAnswers, [currentStep.questions[questionIndex].id]: classicAnswer };
    setClassicAnswers(nextAnswers);
    saveLocalAnswers(projectId, nextAnswers);
    if (!lastQuestion) {
      const nextQuestion = currentStep.questions[questionIndex + 1];
      setClassicAnswer(nextAnswers[nextQuestion.id] ?? null);
      setQuestionIndex((current) => current + 1);
    } else if (!lastStep) {
      const nextStep = wizardSteps[stepIndex + 1];
      setClassicAnswer(nextAnswers[nextStep.questions[0].id] ?? null);
      setStepIndex((current) => current + 1);
      setQuestionIndex(0);
    } else {
      const localDocument = buildLocalDocument(projectId, nextAnswers);
      saveLocalDocument(projectId, localDocument);
      if (backendAvailable) {
        try {
          await documentsApi.generate(projectId);
        } catch {
          setBackendAvailable(false);
        }
      }
      setStatus("completed");
    }
  }

  async function handleAiSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!answer.trim() || submitting) return;
    setSubmitting(true);
    setError(null);
    try {
      const result = await interviewApi.answer(projectId, answer.trim());
      setNote(result.consultant_note);
      setAnswer("");
      setTurnsAnswered((current) => current + 1);
      await refreshCompletion();
      if (result.interview_status === "completed" || !result.next_question) setStatus("completed");
      else {
        setConceptKey(result.next_concept_key);
        setQuestion(result.next_question);
        setQuestionOptions(result.next_question_options ?? []);
        setSection(result.next_section);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Answer was not saved.");
      setMode("classic");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-5 w-5 animate-spin" />
          Preparation de la prochaine question...
        </div>
      </div>
    );
  }

  if (status === "completed") {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background px-4">
        <div className="w-full max-w-md rounded-xl border border-border bg-surface p-8 text-center shadow-lg">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-lg bg-accent-soft text-accent">
            <FileText className="h-7 w-7" />
          </div>
          <h1 className="mt-5 font-display text-xl font-semibold">Cahier des Charges genere</h1>
          <p className="mt-2 text-sm text-muted-foreground">
            Votre entretien est termine. Nous avons prepare votre Cahier des Charges.
          </p>
          <div className="mt-6 flex flex-col gap-2.5">
            <Link href={`/projects/${projectId}/documents`}>
              <Button className="w-full gap-2">Voir le resultat <ArrowRight className="h-4 w-4" /></Button>
            </Link>
            <Link href="/dashboard">
              <Button variant="secondary" className="w-full">Retour au tableau de bord</Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const headerTitle = mode === "ai" ? "Entretien IA metier" : "Questionnaire guide";

  if (mode === "classic") {
    const currentStep = wizardSteps[stepIndex];
    const currentQuestion = currentStep.questions[questionIndex];
    const answered = wizardSteps.slice(0, stepIndex).reduce((sum, step) => sum + step.questions.length, 0) + questionIndex;
    const total = wizardSteps.reduce((sum, step) => sum + step.questions.length, 0);
    const progress = Math.round(((answered + 1) / total) * 100);

    return (
      <Shell projectId={projectId} title={headerTitle} subtitle={currentStep.title}>
        <Stepper steps={wizardSteps} currentStepIndex={stepIndex} progress={progress} />
      {requestedMode === "ai" && error && <p className="mt-4 rounded-lg border border-warning/30 bg-warning-soft px-3 py-2 text-sm text-warning">{error}</p>}
        <div className="mt-6">
          <QuestionCard question={currentQuestion} value={classicAnswer} onChange={setClassicAnswer} />
        </div>
        <div className="mt-6 flex justify-between">
          <Button
            type="button"
            variant="secondary"
            disabled={stepIndex === 0 && questionIndex === 0}
            onClick={() => {
              const saved = { ...classicAnswers, [currentQuestion.id]: classicAnswer };
              setClassicAnswers(saved);
              if (questionIndex > 0) {
                const previousQuestion = currentStep.questions[questionIndex - 1];
                setClassicAnswer(saved[previousQuestion.id] ?? null);
                setQuestionIndex((current) => current - 1);
              } else {
                const previousStep = wizardSteps[stepIndex - 1];
                const previousQuestion = previousStep.questions[previousStep.questions.length - 1];
                setClassicAnswer(saved[previousQuestion.id] ?? null);
                setStepIndex((current) => current - 1);
                setQuestionIndex(previousStep.questions.length - 1);
              }
            }}
          >
            Retour
          </Button>
          <Button type="button" onClick={handleClassicNext} className="gap-2">Continuer <ArrowRight className="h-4 w-4" /></Button>
        </div>
      </Shell>
    );
  }

  const syntheticQuestion: WizardQuestion = {
    id: conceptKey ?? "ai-question",
    title: question ?? "Décrivez le besoin principal pour cette application.",
    helper: "Sélectionnez les suggestions qui conviennent, puis complétez avec votre réponse libre si besoin.",
    type: questionOptions.length ? "checkbox" : "textarea",
    options: questionOptions.map((option) => ({ id: option, label: option })),
    customPrompt: "Autre réponse",
    placeholder: "Votre réponse...",
    required: true,
  };


  return (
    <Shell projectId={projectId} title={headerTitle} subtitle={`${Math.min(turnsAnswered + 1, 30)}/30 - ${section ?? "Question metier"}`}>
      {aiConnection === "checking" && <p className="mb-4 rounded-lg border border-border bg-surface px-3 py-2 text-sm">Assistant IA - Connexion à votre fournisseur IA... Vérification de la connexion et du modèle.</p>}
      {aiConnection === "connected" && <p className="mb-4 rounded-lg border border-accent/30 bg-accent-soft px-3 py-2 text-sm text-accent">IA connectée. L&apos;entretien peut commencer.</p>}
      {completion && (
        <div className="h-1.5 w-full overflow-hidden rounded-full bg-surface-2">
          <div className="h-full rounded-full bg-accent transition-all duration-500" style={{ width: `${completion.overall_completion}%` }} />
        </div>
      )}
      {note && <p className="mt-4 flex gap-2 rounded-xl border border-accent/30 bg-accent-soft px-3 py-2 text-sm"><Sparkles className="h-4 w-4" />{note}</p>}
      <form onSubmit={handleAiSubmit} className="mt-6">
        <QuestionCard
          question={syntheticQuestion}
          value={questionOptions.length ? (answer ? answer.split(" | ") : []) : answer}
          onChange={(value) => setAnswer(Array.isArray(value) ? value.join(" | ") : typeof value === "string" ? value : "")}
        />
        {error && <p className="mt-3 text-sm text-warning">{error}</p>}
        <div className="mt-6 flex justify-end">
          <Button type="submit" disabled={!answer.trim() || submitting} className="gap-2">
            {submitting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                L&apos;IA réfléchit...
              </>
            ) : (
              <>
                Continuer
                <ArrowRight className="h-4 w-4" />
              </>
            )}
          </Button>
        </div>
      </form>
    </Shell>
  );
}

function Shell({ projectId, title, subtitle, children }: { projectId: string; title: string; subtitle: string; children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <header className="sticky top-0 z-20 flex h-16 shrink-0 items-center gap-4 border-b border-border bg-surface/80 px-4 backdrop-blur-md lg:px-8">
        <Link href="/dashboard" className="flex h-9 w-9 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-surface-2 hover:text-foreground">
          <X className="h-4.5 w-4.5" />
        </Link>
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold">{title}</p>
          <p className="text-xs text-muted-foreground">{subtitle}</p>
        </div>
      </header>
      <div className="border-b border-border bg-surface/50 px-4 py-2 lg:px-8">
        <ProjectSubNav projectId={projectId} />
      </div>
      <div className="mx-auto w-full max-w-4xl flex-1 px-4 py-8 lg:px-0">{children}</div>
    </div>
  );
}
