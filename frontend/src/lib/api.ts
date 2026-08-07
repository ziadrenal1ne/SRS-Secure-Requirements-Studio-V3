/**
 * Typed client for the FastAPI backend.
 * The FOCP studio is internal-only, so requests do not require auth tokens.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  status: number;
  errorCode: string;

  constructor(status: number, errorCode: string, message: string) {
    super(message);
    this.status = status;
    this.errorCode = errorCode;
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");

  const res = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });

  if (!res.ok) {
    let errorCode = "unknown_error";
    let message = `Request failed with status ${res.status}`;
    try {
      const body = await res.json();
      errorCode = body.error_code ?? errorCode;
      message = body.message ?? message;
    } catch {
      // response wasn't JSON — keep the generic message
    }
    throw new ApiError(res.status, errorCode, message);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

// ---------------------------------------------------------------------------
// Types mirroring the backend Pydantic schemas
// ---------------------------------------------------------------------------

// Removed Auth types

export type ApiProjectStatus = "brouillon" | "en_cours" | "en_revue" | "valide";

export interface ApiProject {
  id: string;
  name: string;
  short_name: string;
  department: string;
  description: string;
  status: ApiProjectStatus;
  progress: number;
  security_score: number;
  organization_id: string;
  owner_id: string;
  created_at: string;
  updated_at: string;
}

export interface CreateProjectInput {
  name: string;
  short_name: string;
  department?: string;
  description?: string;
}

// ---------------------------------------------------------------------------
// Projects
// ---------------------------------------------------------------------------

export const projectsApi = {
  async list(): Promise<ApiProject[]> {
    return request<ApiProject[]>("/projects");
  },

  async create(input: CreateProjectInput): Promise<ApiProject> {
    return request<ApiProject>("/projects", {
      method: "POST",
      body: JSON.stringify(input),
    });
  },

  async get(projectId: string): Promise<ApiProject> {
    return request<ApiProject>(`/projects/${projectId}`);
  },

  async update(
    projectId: string,
    input: Partial<CreateProjectInput> & {
      status?: ApiProjectStatus;
      progress?: number;
      security_score?: number;
    }
  ): Promise<ApiProject> {
    return request<ApiProject>(`/projects/${projectId}`, {
      method: "PATCH",
      body: JSON.stringify(input),
    });
  },

  async remove(projectId: string): Promise<void> {
    await request<void>(`/projects/${projectId}`, {
      method: "DELETE",
    });
  },
};

// ---------------------------------------------------------------------------
// Knowledge Graph
// ---------------------------------------------------------------------------

export interface KnowledgeGraphNode {
  id: string;
  concept_key: string;
  domain: string;
  label: string;
  description: string;
  completion: number;
  confidence: number;
  importance: string;
  business_value: number;
  risk: string;
  status: string;
  validation_rules: string[];
  missing_information: string[];
  captured_data: Record<string, unknown>;
}

export interface ProjectCompletion {
  total_concepts: number;
  completed_concepts: number;
  overall_completion: number;
  overall_confidence: number;
  by_domain: Record<string, { total: number; completed: number }>;
}

export const knowledgeGraphApi = {
  async completion(projectId: string): Promise<ProjectCompletion> {
    return request<ProjectCompletion>(`/projects/${projectId}/knowledge-graph/completion`);
  },
  async gaps(projectId: string): Promise<KnowledgeGraphNode[]> {
    return request<KnowledgeGraphNode[]>(`/projects/${projectId}/knowledge-graph/gaps`);
  },
};

// ---------------------------------------------------------------------------
// Interview
// ---------------------------------------------------------------------------

export interface InterviewTurn {
  sequence: number;
  concept_key: string;
  question: string;
  answer: string;
  completion_delta: number;
  confidence_delta: number;
  consultant_note: string;
  extracted_data: Record<string, unknown>;
  created_at: string;
}

export interface InterviewSession {
  id: string;
  project_id: string;
  status: "active" | "paused" | "completed";
  pending_question: string | null;
  pending_concept_key: string | null;
  pending_question_options: string[];
  pending_section: string | null;
  max_questions: number;
  turns: InterviewTurn[];
  created_at: string;
  updated_at: string;
}

export interface AnswerResponse {
  concept_key: string;
  consultant_note: string;
  next_question: string | null;
  next_concept_key: string | null;
  next_question_options: string[];
  next_section: string | null;
  max_questions: number;
  generated_document_id: string | null;
  interview_status: string;
}

export const interviewApi = {
  async start(projectId: string): Promise<InterviewSession> {
    return request<InterviewSession>(`/projects/${projectId}/interview/start`, {
      method: "POST",
    });
  },
  async answer(projectId: string, answer: string): Promise<AnswerResponse> {
    return request<AnswerResponse>(`/projects/${projectId}/interview/answer`, {
      method: "POST",
      body: JSON.stringify({ answer }),
    });
  },
  async state(projectId: string): Promise<InterviewSession> {
    return request<InterviewSession>(`/projects/${projectId}/interview/state`);
  },
};

// ---------------------------------------------------------------------------
// Requirements
// ---------------------------------------------------------------------------

export interface Requirement {
  id: string;
  requirement_key: string;
  requirement_type: string;
  title: string;
  description: string;
  priority: string;
  business_goal: string;
  risk: string;
  status: string;
  owner: string;
  actors: string[];
  acceptance_criteria: string[];
  dependencies: string[];
  security_controls: string[];
  database_tables: string[];
  api_endpoints: string[];
  ui_screens: string[];
  test_cases: string[];
  source_concept_key: string;
  created_at: string;
  updated_at: string;
}

export const requirementsApi = {
  async list(projectId: string): Promise<Requirement[]> {
    return request<Requirement[]>(`/projects/${projectId}/requirements`);
  },
  async generate(projectId: string): Promise<Requirement[]> {
    return request<Requirement[]>(`/projects/${projectId}/requirements/generate`, {
      method: "POST",
    });
  },
  async update(
    projectId: string,
    requirementId: string,
    input: Partial<Pick<Requirement, "priority" | "status" | "owner" | "title" | "description">>
  ): Promise<Requirement> {
    return request<Requirement>(`/projects/${projectId}/requirements/${requirementId}`, {
      method: "PATCH",
      body: JSON.stringify(input),
    });
  },
};

// ---------------------------------------------------------------------------
// Security
// ---------------------------------------------------------------------------

export interface SecurityAnalysis {
  id: string;
  project_id: string;
  threat_model: Array<Record<string, unknown>>;
  rbac_matrix: Record<string, unknown>;
  risk_register: Array<Record<string, unknown>>;
  security_checklist: Array<{
    control_key: string;
    name: string;
    status: "present" | "partial" | "missing";
    evidence: string;
    recommendation: string;
    framework_references: Record<string, string | null>;
  }>;
  privacy_impact_assessment: Record<string, unknown>;
  data_classification: Array<Record<string, unknown>>;
  security_score: number;
}

export const securityApi = {
  async analyze(projectId: string): Promise<SecurityAnalysis> {
    return request<SecurityAnalysis>(`/projects/${projectId}/security/analyze`, {
      method: "POST",
    });
  },
  async get(projectId: string): Promise<SecurityAnalysis> {
    return request<SecurityAnalysis>(`/projects/${projectId}/security`);
  },
};

// ---------------------------------------------------------------------------
// Documents
// ---------------------------------------------------------------------------

export interface GeneratedDocument {
  id: string;
  project_id: string;
  content: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export type ExportFormat = "json" | "md" | "html" | "docx" | "pdf" | "tex";

export const documentsApi = {
  async generate(projectId: string): Promise<GeneratedDocument> {
    return request<GeneratedDocument>(`/projects/${projectId}/documents/generate`, {
      method: "POST",
    });
  },
  async get(projectId: string): Promise<GeneratedDocument> {
    return request<GeneratedDocument>(`/projects/${projectId}/documents`);
  },
  exportUrl(projectId: string, format: ExportFormat): string {
    return `${API_BASE_URL}/projects/${projectId}/documents/export?format=${format}`;
  },
  async download(projectId: string, format: ExportFormat): Promise<void> {
    const res = await fetch(documentsApi.exportUrl(projectId, format));
    if (!res.ok) throw new ApiError(res.status, "export_failed", "L'export a échoué.");
    const blob = await res.blob();
    const disposition = res.headers.get("Content-Disposition") ?? "";
    const match = disposition.match(/filename="?([^"]+)"?/);
    const filename = match ? match[1] : `document.${format}`;
    const url = window.URL.createObjectURL(blob);
    const a = window.document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
  },
};

// ---------------------------------------------------------------------------
// Review
// ---------------------------------------------------------------------------

export interface ReviewFinding {
  rule_id: string;
  category: string;
  severity: "info" | "warning" | "critical";
  target: string;
  message: string;
  passed: boolean;
}

export interface ReviewRun {
  id: string;
  project_id: string;
  findings: ReviewFinding[];
  rule_count: number;
  failed_count: number;
  completeness_score: number;
  confidence_score: number;
  security_score: number;
  architecture_score: number;
  business_score: number;
  testing_score: number;
  overall_score: number;
  approved_for_export: boolean;
}

export const reviewApi = {
  async run(projectId: string): Promise<ReviewRun> {
    return request<ReviewRun>(`/projects/${projectId}/review/run`, { method: "POST" });
  },
  async get(projectId: string): Promise<ReviewRun> {
    return request<ReviewRun>(`/projects/${projectId}/review`);
  },
};

// ---------------------------------------------------------------------------
// Health & AI Status
// ---------------------------------------------------------------------------

export interface AiHealthStatus {
  status: "ok" | "model_missing" | "error" | "fallback";
  connected: boolean;
  model_available: boolean;
  provider: string;
  model: string;
  host?: string;
  installed_models?: string[];
  error?: string | null;
}

export const healthApi = {
  async checkAi(): Promise<AiHealthStatus> {
    return request<AiHealthStatus>("/health/ai");
  },
};
