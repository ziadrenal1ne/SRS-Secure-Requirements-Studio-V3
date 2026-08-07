# Secure Requirements Studio — Fondation OCP

> « Transform Business Needs into Secure Software Requirements. »

Frontend prototype only — no auth, no API, no database. Everything runs on
mock data in `src/lib/mock-data.ts`, styled around a realistic scenario:
the **Plateforme de Gestion des Bénéficiaires** for Fondation OCP's
*Al Moutmir* agricultural program.

## Stack

- **Next.js 15** (App Router) + **TypeScript**
- **Tailwind CSS v4** (CSS-based theme, see `src/app/globals.css`)
- **Framer Motion** for transitions & micro-interactions
- **Lucide** icons
- **Recharts** for the admin analytics charts
- UI primitives hand-built in the **shadcn/ui** visual language (no Radix
  runtime) — see `src/components/ui/`
- Fonts self-hosted via `@fontsource` (Sora / Inter / JetBrains Mono) — no
  runtime dependency on Google Fonts

## Getting started

```bash
npm install
npm run dev
```

Open http://localhost:3000. Run `npm run build && npm run start` for a
production build (verified to build clean with `npm run build` and pass
`npx eslint .`).

## Pages

| Route | Description |
| --- | --- |
| `/` | Landing page — hero, features, how it works, cybersecurity section, testimonials |
| `/dashboard` | Project list, stats, search/filter, recent activity |
| `/projects/new` | Multi-step conversational questionnaire wizard (dynamic follow-up questions, autosave indicator) |
| `/projects/[id]/summary` | Reviewable project summary — modules, roles, security score |
| `/projects/[id]/document` | Generated Cahier des Charges — Notion-style TOC + collapsible sections, requirement blocks, tables |
| `/admin` | Admin overview — submissions table, notifications, analytics charts |
| `/admin/projects/[id]` | Admin project detail — tabs for overview, requirements, timeline, versions, notes/comments, generated files |

Every project card / table row links to a real route — the whole thing is
navigable end to end. The wizard's "Terminer" step routes into the
`pgb-almoutmir` project's summary/document, since that's the fully fleshed
out demo project.

## Structure

```
src/
  app/                 # routes (App Router)
  components/
    ui/                # shadcn-style primitives (Button, Card, Table, ...)
    layout/             # Sidebar, AdminSidebar, TopNav, MobileDrawer
    dashboard/          # StatCard, ProjectCard
    wizard/             # Stepper, QuestionCard, TagInput, UploadZone
    document/           # Toc, DocumentSection, RequirementBlock
    marketing/          # Landing page sections
    admin/              # Recharts wrappers
  lib/
    mock-data.ts        # all mock content (projects, wizard questions, document sections...)
    types.ts
    utils.ts
```

## Notes for whoever picks this up next

- Dark/light mode via `next-themes`, toggle lives in the top nav.
- The wizard's dynamic follow-up (CSV upload -> volume question) is driven by
  `WizardQuestion.followUps` in `types.ts` — the flattened question list is
  recomputed from current answers on every render, so add more triggers the
  same way.
- Swap `src/lib/mock-data.ts` for real data fetching whenever the backend
  lands; the components don't otherwise know it's mocked.
# Secure-Requirements-Studio
