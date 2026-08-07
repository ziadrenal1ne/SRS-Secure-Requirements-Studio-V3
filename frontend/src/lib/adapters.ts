import type { ApiProject } from "@/lib/api";
import type { Project } from "@/lib/types";

export function getInitials(fullName: string): string {
  const parts = fullName.trim().split(/\s+/);
  const initials = parts.slice(0, 2).map((p) => p[0]?.toUpperCase() ?? "");
  return initials.join("") || "?";
}

/**
 * Adapts a backend ApiProject into the richer `Project` shape the
 * existing UI components (ProjectCard, StatCard, etc.) expect.
 *
 * There is no authentication/membership layer in this application (every
 * project belongs to a single internal FOCP owner — see
 * `_internal_context` in `public_projects.py`), so there's no per-user
 * owner identity to resolve here; the display owner is a fixed label.
 *
 * Fields not yet backed by an API (modules, roles, tags, estimated
 * requirements) default to empty/zero until the Knowledge Graph and
 * Requirement Engine phases land — this is intentional, not a bug.
 */
export function toDisplayProject(project: ApiProject): Project {
  const ownerName = "Secure Requirements Studio";

  return {
    id: project.id,
    name: project.name,
    shortName: project.short_name,
    department: project.department,
    owner: {
      name: ownerName,
      role: "Fondation OCP",
      initials: getInitials(ownerName),
    },
    status: project.status,
    progress: project.progress,
    securityScore: project.security_score,
    createdAt: project.created_at,
    updatedAt: project.updated_at,
    description: project.description,
    modules: [],
    roles: [],
    estimatedRequirements: 0,
    tags: [],
  };
}
