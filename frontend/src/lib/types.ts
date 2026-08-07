export type ProjectStatus = "brouillon" | "en_cours" | "en_revue" | "valide";

export interface ProjectModule {
  id: string;
  name: string;
  description: string;
}

export interface ProjectRole {
  id: string;
  name: string;
  description: string;
  permissions: string[];
}

export interface Project {
  id: string;
  name: string;
  shortName: string;
  department: string;
  owner: {
    name: string;
    role: string;
    initials: string;
  };
  status: ProjectStatus;
  progress: number;
  securityScore: number;
  createdAt: string;
  updatedAt: string;
  description: string;
  modules: ProjectModule[];
  roles: ProjectRole[];
  estimatedRequirements: number;
  tags: string[];
}

export interface ActivityItem {
  id: string;
  actor: string;
  initials: string;
  action: string;
  target: string;
  time: string;
  type: "create" | "update" | "comment" | "generate" | "submit";
}

export interface NotificationItem {
  id: string;
  title: string;
  description: string;
  time: string;
  read: boolean;
  type: "info" | "success" | "warning";
}

export type QuestionType =
  | "text"
  | "textarea"
  | "radio"
  | "checkbox"
  | "tags"
  | "select"
  | "cards"
  | "upload"
  | "date";

export interface QuestionOption {
  id: string;
  label: string;
  description?: string;
  icon?: string;
}

export interface FollowUpQuestion {
  id: string;
  triggerOptionId: string;
  question: WizardQuestion;
}

export interface WizardQuestion {
  id: string;
  title: string;
  helper: string;
  description?: string;
  example?: string;
  recommendedAnswer?: string;
  tooltip?: string;
  importance?: "critique" | "haute" | "moyenne" | "faible";
  dependencies?: string[];
  type: QuestionType;
  options?: QuestionOption[];
  placeholder?: string;
  required?: boolean;
  customPrompt?: string;
  followUps?: FollowUpQuestion[];
}

export interface WizardStep {
  id: string;
  title: string;
  shortTitle: string;
  description: string;
  questions: WizardQuestion[];
}

export type RequirementPriority = "critique" | "haute" | "moyenne";

export interface DocumentRequirement {
  id: string;
  code: string;
  label: string;
  detail: string;
  priority: RequirementPriority;
}

export interface DocumentSectionTable {
  headers: string[];
  rows: string[][];
}

export interface DocumentSection {
  id: string;
  title: string;
  icon: string;
  summary: string;
  paragraphs?: string[];
  requirements?: DocumentRequirement[];
  table?: DocumentSectionTable;
}

export interface AdminSubmission {
  id: string;
  projectId: string;
  projectName: string;
  submittedBy: string;
  department: string;
  submittedAt: string;
  status: ProjectStatus;
  completeness: number;
}
