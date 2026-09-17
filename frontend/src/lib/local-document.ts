import type { AnswerValue } from "@/components/wizard/question-card";
import type { GeneratedDocument } from "@/lib/api";

type Section = { title: string; items: string[] };

function asText(value: AnswerValue | undefined): string {
  if (!value) return "";
  const raw = Array.isArray(value) ? value.join(", ") : value;
  return raw
    .replace(/\*\*/g, "")
    .replace(/custom:/g, "")
    .replace(/comment:/g, "Commentaire : ")
    .replace(/\s+/g, " ")
    .trim();
}

function split(value: string): string[] {
  return value
    .split(/[,;\n|]/)
    .map((item) => item.trim().replace(/\.$/, ""))
    .filter(Boolean)
    .filter((item) => !item.toLowerCase().startsWith("autre /"));
}

function sentence(value: string): string {
  const clean = value.trim();
  if (!clean) return "";
  return /[.!?]$/.test(clean) ? clean : `${clean}.`;
}

function join(items: string[]): string {
  if (items.length <= 1) return items[0] ?? "";
  if (items.length === 2) return `${items[0]} et ${items[1]}`;
  return `${items.slice(0, -1).join(", ")} ainsi que ${items[items.length - 1]}`;
}

function add(sections: Section[], title: string, items: string[]) {
  const clean = items.map(sentence).filter(Boolean);
  if (clean.length) sections.push({ title, items: clean });
}

function yes(value: string): boolean {
  const lower = value.toLowerCase();
  return lower.includes("oui") || lower.includes("peut");
}

export function buildLocalDocument(projectId: string, answers: Record<string, AnswerValue>): GeneratedDocument {
  const text = Object.fromEntries(Object.entries(answers).map(([key, value]) => [key, asText(value)]));
  const projectName = text.project_name || "Projet";
  const features = split(text.main_features);
  const users = split(text.users);
  const search = split(text.search);
  const exports = split(text.exports);
  const sensitive = split(text.sensitive_information);
  const devices = split(text.devices);
  const languages = split(text.languages);

  const sections: Section[] = [];
  add(sections, "1. Contexte et problématique", [
    text.current_situation ? `Aujourd'hui, le besoin est géré de la manière suivante : ${text.current_situation}` : "",
    text.problem ? `La principale difficulté à résoudre est la suivante : ${text.problem}` : "",
    text.expected_result ? `La nouvelle application doit permettre de ${text.expected_result.charAt(0).toLowerCase()}${text.expected_result.slice(1)}` : "",
  ]);
  add(sections, "2. Objectifs de la plateforme", [
    text.objective,
    features.length ? `La plateforme vise également à couvrir les fonctions clés suivantes : ${join(features)}.` : "",
  ]);
  add(sections, "3. Utilisateurs et permissions", [
    users.length ? `Les profils utilisateurs identifiés sont : ${join(users)}.` : "",
    text.user_actions ? `Les actions attendues par profil sont les suivantes : ${text.user_actions}` : "",
    text.restricted_information && !text.restricted_information.toLowerCase().includes("non")
      ? `Les informations sensibles ou financières doivent être accessibles uniquement aux profils autorisés : ${text.restricted_information}`
      : "",
  ]);
  add(sections, "4. Données gérées", [
    text.view_information ? `Les utilisateurs doivent consulter : ${text.view_information}` : "",
    text.edit_information ? `Les utilisateurs autorisés doivent ajouter ou modifier : ${text.edit_information}` : "",
  ]);
  add(sections, "5. Fonctionnalités principales", [
    features.length ? `Le périmètre fonctionnel comprend : ${join(features)}.` : "",
    text.documents && yes(text.documents) ? "La gestion documentaire doit couvrir le dépôt, la consultation et l'export des pièces utiles." : text.documents,
  ]);
  add(sections, "6. Workflow métier", [
    text.main_workflow,
    yes(text.validation) ? "Certaines informations doivent être vérifiées ou validées avant confirmation." : "",
    text.rejection ? `En cas d'information incorrecte ou rejetée, le processus doit prévoir : ${join(split(text.rejection))}.` : "",
    text.history && !text.history.toLowerCase().includes("non") ? "L'historique des modifications doit être conservé pour les informations concernées." : "",
  ]);
  add(sections, "7. Recherche, filtres et tableaux de bord", [
    search.length ? `La recherche doit permettre de filtrer les informations par ${join(search)}.` : "",
    text.dashboards ? `Les tableaux de bord doivent présenter : ${text.dashboards}` : "",
    yes(text.maps) ? `Une vue cartographique ou de localisation est à prévoir : ${text.maps}` : "",
  ]);
  add(sections, "8. Documents et rapports", [
    text.documents && !yes(text.documents) ? `Documents attendus : ${text.documents}` : "",
    yes(text.reports) ? `Des rapports métier doivent être générés selon les besoins exprimés : ${text.reports}` : "",
    exports.length ? `Les formats d'export attendus sont : ${join(exports)}.` : "",
  ]);
  add(sections, "9. Notifications", [
    yes(text.notifications) ? `Des notifications doivent accompagner les événements importants du processus : ${text.notifications}` : "",
  ]);
  add(sections, "10. Exigences de cybersécurité", [
    sensitive.length ? `Les informations à protéger particulièrement sont : ${join(sensitive)}.` : "",
    text.restricted_information && !text.restricted_information.toLowerCase().includes("non") ? "Les accès doivent être différenciés selon les rôles métier." : "",
    text.special_constraints ? `Contraintes confirmées par l'utilisateur : ${text.special_constraints}` : "",
  ]);
  add(sections, "11. Exigences non fonctionnelles et contraintes", [
    text.availability ? `Mode de fonctionnement attendu : ${text.availability}` : "",
    devices.length ? `L'application doit être utilisable sur ${join(devices)}.` : "",
    languages.length ? `Les langues attendues sont : ${join(languages)}.` : "",
    text.final_notes,
  ]);
  add(sections, "12. MVP et évolutions futures", [
    text.mvp ? `MVP : ${text.mvp}` : "",
    text.future_features ? `Évolutions futures : ${text.future_features}` : "",
  ]);
  add(sections, "13. Critères d'acceptation", [
    users.length ? "Chaque profil utilisateur accède uniquement aux fonctions prévues pour son rôle." : "",
    text.mvp ? "Les fonctionnalités indispensables de la première version sont utilisables de bout en bout." : "",
    sensitive.length ? "Les informations déclarées sensibles ne sont accessibles qu'aux profils autorisés." : "",
    exports.length ? "Les exports demandés sont générés correctement à partir des données réellement saisies." : "",
    yes(text.notifications) ? "Les notifications prévues sont déclenchées aux étapes clés du workflow." : "",
  ]);

  return {
    id: `local-${projectId}`,
    project_id: projectId,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    content: {
      generated_at: new Date().toISOString(),
      project: { name: projectName, status: "brouillon" },
      cahier_des_charges: {
        title: `Cahier des Charges - ${projectName}`,
        summary: sentence(text.objective || `Cadrage fonctionnel du projet ${projectName}`),
        completeness_score: 100,
        points_to_confirm: [],
        sections,
      },
    },
  };
}

export function saveLocalDocument(projectId: string, document: GeneratedDocument) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(`srs_local_document_${projectId}`, JSON.stringify(document));
}

export function saveLocalAnswers(projectId: string, answers: Record<string, AnswerValue>) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(`srs_local_answers_${projectId}`, JSON.stringify(answers));
}

export function loadLocalAnswers(projectId: string): Record<string, AnswerValue> | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(`srs_local_answers_${projectId}`);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as Record<string, AnswerValue>;
  } catch {
    return null;
  }
}

export function loadLocalDocument(projectId: string): GeneratedDocument | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem(`srs_local_document_${projectId}`);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as GeneratedDocument;
  } catch {
    return null;
  }
}
