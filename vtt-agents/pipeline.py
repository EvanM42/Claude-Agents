"""
pipeline.py — VTT-ALL-RPG (Quest Board) specific agent pipeline.

Project: Universal TTRPG platform — React 19 + TypeScript + Vite + Supabase + Railway
Currently on: Phase 4 (Platform & Social Features)

Usage:
    python pipeline.py

Edit the TASK variable and toggle STEPS at the bottom to control what runs.
"""

import asyncio
import sys
import os
from pathlib import Path

# Force UTF-8 output so Windows terminal doesn't choke on emoji from agents
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

# Load .env from parent claude-agents folder
_env_path = Path(__file__).parent.parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

# ---------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------

PROJECT_ROOT = "C:/Users/Evanm/personal projects/VTT-All/VTT-ALL-RPG"
FRONTEND_DIR = f"{PROJECT_ROOT}/frontend"
BACKEND_SQL_DIR = f"{PROJECT_ROOT}/backend/sql"
AGENTS_DIR = "C:/Users/Evanm/personal projects/claude-agents"

# Add general agents to path so we can reuse their system prompts if needed
sys.path.append(AGENTS_DIR)

# ---------------------------------------------------------------
# PROJECT CONTEXT (injected into every agent's task)
# ---------------------------------------------------------------

PROJECT_CONTEXT = f"""
=== QUEST BOARD — VTT-ALL-RPG PROJECT CONTEXT ===

Project root: {PROJECT_ROOT}
Frontend: {FRONTEND_DIR}
Backend SQL migrations: {BACKEND_SQL_DIR}

Stack:
- Frontend: React 19 + TypeScript 5.9 (strict) + Vite 7 + Tailwind CSS v4
  + shadcn/ui (New York style) + Zustand v5 + React Router v7 + TanStack Query v5
- Backend: Supabase (PostgreSQL + Auth + Realtime)
- Package manager: pnpm — ALL frontend scripts run from {FRONTEND_DIR}
- Deployment: Railway (Nixpacks)

Key commands (run from {FRONTEND_DIR}):
  pnpm dev           — start dev server (localhost:5173)
  pnpm build         — TypeScript check + Vite production build
  pnpm lint          — ESLint
  pnpm test:e2e      — Playwright E2E tests (MUST run pnpm build first)

Important conventions:
- TypeScript strict mode — no unused vars/params (these are ERRORS)
- Use path alias @/ for src/
- Icons: Lucide React only
- Dice: always use crypto.getRandomValues() via src/lib/dice.ts — never Math.random()
- CharacterData type is always Record<string, unknown>
- Tailwind v4 via @tailwindcss/vite plugin — CSS variables in src/index.css
- Forms: React Hook Form + Zod

Key file locations:
  App.tsx / routes     → frontend/src/App.tsx
  Pages                → frontend/src/pages/
  Zustand stores       → frontend/src/stores/
  Types                → frontend/src/types/
  System registry      → frontend/src/lib/systemRegistry.ts
  Game system data     → frontend/src/data/systems/
  Character creation   → frontend/src/components/character/creation-steps/
  Character sheet      → frontend/src/components/character/sheet-sections/
  Supabase client      → frontend/src/lib/supabase.ts
  shadcn/ui components → frontend/src/components/ui/
  SQL migrations       → backend/sql/
  E2E tests            → frontend/tests/e2e/

Architecture:
- Game systems are self-registering: each file calls registerSystem() on import
  and is activated by adding an import to frontend/src/data/systems/index.ts
- State: authStore (Supabase auth), characterStore (CRUD + localStorage + Supabase sync),
  diceStore (roll history), themeStore (light/dark/system)
- Auth flow: App.tsx calls authStore.init() on mount → on login, characterStore.fetchFromSupabase()
- All Zustand persisted stores use localStorage keys prefixed vtt-

Database tables: profiles, characters, campaigns, campaign_members,
                 quests, quest_objectives, sessions, session_events,
                 rules.documents, rules.entities

Current status: Phase 4 in progress
Phase 4 goals (not yet done):
- Public character sheet URLs (shareable via slug)
- Initiative tracker with HP management
- Notification system (your turn, quest updated, session starting)
- Mobile-responsive pass across all pages
- PDF character sheet export (client-side, per system)
- Campaign journals (rich text, image embeds)

Testing: Playwright E2E — auth session is set up in tests/e2e/auth.setup.ts
and reused via tests/.auth/session.json. Always build before running tests.
No mock DB — tests use a real Supabase instance.
=================================================
"""

# ---------------------------------------------------------------
# CORE RUNNER
# ---------------------------------------------------------------

async def run_agent(
    label: str,
    task: str,
    system_prompt: str,
    tools: list[str],
    permission_mode: str = "default",
    verbose: bool = True,
) -> str:
    allowed_tools = tools
    print(f"\n{'=' * 60}")
    print(f"  [{label.upper()}]")
    print(f"{'=' * 60}")

    result_text = ""
    full_task = f"{PROJECT_CONTEXT}\n\n{task}"

    async for message in query(
        prompt=full_task,
        options=ClaudeAgentOptions(
            allowed_tools=allowed_tools,
            permission_mode=permission_mode,
            system_prompt=system_prompt,
        ),
    ):
        if isinstance(message, AssistantMessage):
            if verbose:
                for block in message.content:
                    if hasattr(block, "text") and block.text:
                        print(block.text)
                    elif hasattr(block, "name"):
                        print(f"  [Tool: {block.name}]")
        elif isinstance(message, ResultMessage):
            result_text = message.result or ""
            print(f"\n  [{label.upper()}] finished — status: {message.subtype}")

    return result_text

# ---------------------------------------------------------------
# VTT-SPECIFIC AGENT DEFINITIONS
# ---------------------------------------------------------------

AGENTS = {
    "manager": {
        "system_prompt": """You are the engineering manager for Quest Board, a universal TTRPG platform.
You understand the full stack: React/TypeScript frontend, Supabase backend, Railway deployment.
Break down the task into a clear ordered plan. Reference specific files and directories from the project.
Do not write code — produce a structured plan only.""",
        "tools": ["Read", "Glob", "Grep", "Bash"],
        "permission_mode": "default",
    },
    "researcher": {
        "system_prompt": """You are a technical researcher for a React/TypeScript/Supabase app.
Research the best approach for the given task. Consider the existing stack (React 19, Vite 7,
Tailwind v4, shadcn/ui, TanStack Query v5, Zustand v5) before recommending new dependencies.
Prefer solutions that fit the existing architecture. Do not write implementation code.""",
        "tools": ["WebSearch", "WebFetch", "Read", "Glob"],
        "permission_mode": "default",
    },
    "architect": {
        "system_prompt": """You are a software architect for Quest Board, a universal TTRPG platform.
Design solutions that fit the existing patterns: self-registering game systems, Zustand stores,
Supabase RLS, shadcn/ui components. Read the existing code before designing.
Output a written plan — do not write implementation code.""",
        "tools": ["Read", "Glob", "Grep", "WebSearch"],
        "permission_mode": "default",
    },
    "developer": {
        "system_prompt": """You are a senior TypeScript/React developer working on Quest Board.
Follow all project conventions strictly:
- TypeScript strict mode — no unused vars/params (they are errors)
- Use @/ path alias for src/
- Lucide React for icons only
- Dice: crypto.getRandomValues() via src/lib/dice.ts only, never Math.random()
- Tailwind v4 for styling, CSS variables for theming
- Forms: React Hook Form + Zod
- Run pnpm build from the frontend/ directory to verify TypeScript compiles
Read existing files before modifying them. Keep implementations focused.""",
        "tools": ["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
        "permission_mode": "acceptEdits",
    },
    "second_opinion": {
        "system_prompt": """You are a skeptical senior developer reviewing code for Quest Board.
Challenge assumptions. Check that React conventions are followed, TypeScript is strict,
Supabase queries use proper RLS, and new code fits existing patterns (stores, component structure).
Be direct — state what is wrong and why. Also acknowledge what is correct.""",
        "tools": ["Read", "Glob", "Grep"],
        "permission_mode": "default",
    },
    "tester": {
        "system_prompt": """You are a QA engineer for Quest Board. The test suite is Playwright E2E.
You MUST run 'pnpm build' from the frontend/ directory before running tests.
Run tests with 'pnpm test:e2e' from frontend/.
Write tests in frontend/tests/e2e/. Do not mock the database — tests use a real Supabase instance.
Report all failures clearly. Do not fix the underlying code.""",
        "tools": ["Read", "Write", "Bash", "Glob", "Grep"],
        "permission_mode": "acceptEdits",
    },
    "debugger": {
        "system_prompt": """You are an expert debugger for a React/TypeScript/Supabase app.
When debugging TypeScript errors: check strict mode violations, unused vars, type mismatches.
When debugging Supabase issues: check RLS policies, query structure, auth state.
When debugging Playwright failures: check selectors, auth session, build step.
Find root causes methodically. Apply minimal fixes only.""",
        "tools": ["Read", "Edit", "Bash", "Glob", "Grep"],
        "permission_mode": "acceptEdits",
    },
    "reviewer": {
        "system_prompt": """You are a code reviewer for Quest Board. Focus on:
1. Security — Supabase RLS correctness, no exposed secrets, no unsafe input handling
2. TypeScript correctness — strict mode compliance, proper typing
3. React patterns — no unnecessary re-renders, correct hook usage
4. Supabase patterns — proper error handling, RLS assumptions
5. Accessibility — ARIA labels, keyboard navigation, color contrast
Output a structured report: Critical Issues, Warnings, Suggestions. Do not rewrite code.""",
        "tools": ["Read", "Glob", "Grep"],
        "permission_mode": "default",
    },
    "refactorer": {
        "system_prompt": """You are a refactoring specialist for a React/TypeScript codebase.
Improve code quality without changing behavior. Target: duplicated logic across stores or components,
overly complex TypeScript types, components doing too much, inconsistent patterns.
Run pnpm build and pnpm lint from frontend/ after changes to confirm nothing broke.""",
        "tools": ["Read", "Edit", "Bash", "Glob", "Grep"],
        "permission_mode": "acceptEdits",
    },
    "documenter": {
        "system_prompt": """You are a technical writer for Quest Board. Write documentation
that helps developers understand the codebase. Update CLAUDE.md if new patterns are introduced.
Write component-level comments for complex logic. Always read the code before writing anything.""",
        "tools": ["Read", "Write", "Edit", "Glob", "Grep"],
        "permission_mode": "acceptEdits",
    },
    "devops": {
        "system_prompt": """You are a DevOps engineer for Quest Board, deployed on Railway with Nixpacks.
Handle deployment config, environment variables, CI/CD. The project already has railway.json and
nixpacks.toml — read them before making changes. Be careful not to break the existing Railway setup.""",
        "tools": ["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
        "permission_mode": "acceptEdits",
    },
}

# ---------------------------------------------------------------
# PIPELINE
# ---------------------------------------------------------------

async def run_pipeline(task: str, steps: dict, verbose: bool = True):
    context = {}

    def with_context(role: str, base: str) -> str:
        parts = [base]
        if role != "manager" and "manager" in context:
            parts.insert(0, f"Plan from manager:\n{context['manager']}\n")
        if role in ("architect", "developer") and "researcher" in context:
            parts.insert(0, f"Research findings:\n{context['researcher']}\n")
        if role in ("developer", "second_opinion", "tester", "reviewer", "refactorer") and "architect" in context:
            parts.insert(0, f"Architecture design:\n{context['architect']}\n")
        if role in ("second_opinion", "tester", "reviewer", "refactorer", "documenter") and "developer" in context:
            parts.insert(0, f"Developer notes:\n{context['developer']}\n")
        if role == "debugger" and "tester" in context:
            parts.insert(0, f"Test failures:\n{context['tester']}\n")
        return "\n\n".join(parts)

    if steps.get("manager"):
        context["manager"] = await run_agent(
            "Manager",
            with_context("manager", f"Task: {task}\n\nAnalyze this task in the context of Quest Board and produce a detailed, ordered implementation plan."),
            **AGENTS["manager"], verbose=verbose,
        )

    if steps.get("researcher"):
        context["researcher"] = await run_agent(
            "Researcher",
            with_context("researcher", f"Task: {task}\n\nResearch the best approach for this task given the existing Quest Board stack. Recommend solutions that fit existing patterns first."),
            **AGENTS["researcher"], verbose=verbose,
        )

    if steps.get("architect"):
        context["architect"] = await run_agent(
            "Architect",
            with_context("architect", f"Task: {task}\n\nDesign the solution architecture. Read relevant existing files first. Output a written plan with specific file paths and component names."),
            **AGENTS["architect"], verbose=verbose,
        )

    if steps.get("developer"):
        context["developer"] = await run_agent(
            "Developer",
            with_context("developer", f"Task: {task}\n\nImplement the solution in {PROJECT_ROOT}. Follow all project conventions. Run pnpm build from {FRONTEND_DIR} to verify the TypeScript compiles when done."),
            **AGENTS["developer"], verbose=verbose,
        )

    if steps.get("second_opinion"):
        context["second_opinion"] = await run_agent(
            "Second Opinion",
            with_context("second_opinion", f"Task: {task}\n\nReview the implementation critically. Check that it fits Quest Board's patterns and conventions."),
            **AGENTS["second_opinion"], verbose=verbose,
        )

    if steps.get("tester"):
        context["tester"] = await run_agent(
            "Tester",
            with_context("tester", f"Task: {task}\n\nWrite Playwright E2E tests for the changes. Run pnpm build then pnpm test:e2e from {FRONTEND_DIR}. Report all failures."),
            **AGENTS["tester"], verbose=verbose,
        )

    if steps.get("debugger"):
        tester_out = context.get("tester", "").lower()
        if any(w in tester_out for w in ["fail", "error", "exception", "broken", "assert", "timeout"]):
            print("\n  [PIPELINE] Test failures detected — running debugger...")
            context["debugger"] = await run_agent(
                "Debugger",
                with_context("debugger", "Fix all failing tests. Find root causes and apply minimal fixes. Re-run pnpm build and pnpm test:e2e to confirm."),
                **AGENTS["debugger"], verbose=verbose,
            )
        else:
            print("\n  [PIPELINE] No test failures — skipping debugger.")

    if steps.get("reviewer"):
        context["reviewer"] = await run_agent(
            "Reviewer",
            with_context("reviewer", f"Task: {task}\n\nAudit the changes for security (especially Supabase RLS), TypeScript correctness, React patterns, and accessibility."),
            **AGENTS["reviewer"], verbose=verbose,
        )

    if steps.get("refactorer"):
        context["refactorer"] = await run_agent(
            "Refactorer",
            with_context("refactorer", "Address any quality issues from the reviewer. Improve code without changing behavior. Run pnpm build and pnpm lint to confirm."),
            **AGENTS["refactorer"], verbose=verbose,
        )

    if steps.get("documenter"):
        context["documenter"] = await run_agent(
            "Documenter",
            with_context("documenter", f"Task: {task}\n\nUpdate CLAUDE.md if new patterns were introduced. Add comments to any complex logic. Keep it brief and accurate."),
            **AGENTS["documenter"], verbose=verbose,
        )

    if steps.get("devops"):
        context["devops"] = await run_agent(
            "DevOps",
            with_context("devops", f"Task: {task}\n\nUpdate Railway/Nixpacks config if needed. Check for new environment variables that need documenting."),
            **AGENTS["devops"], verbose=verbose,
        )

    print(f"\n{'=' * 60}")
    print("  PIPELINE COMPLETE")
    print(f"{'=' * 60}\n")
    return context


# ---------------------------------------------------------------
# CONFIGURE YOUR TASK HERE
# ---------------------------------------------------------------

if __name__ == "__main__":

    # Describe what you want done on the VTT project
    TASK = """
    Implement ALL of Phase 4 of the Quest Board TTRPG platform. Read the ROADMAP at:
      C:/Users/Evanm/personal projects/VTT-All/VTT-ALL-RPG/MD files/management agent/ROADMAP.md

    Phase 4 — Platform & Social Features (all 6 items are currently unchecked):

    1. PUBLIC CHARACTER SHEET URLs (shareable via slug)
       - Add a `slug` column to the `characters` table (unique, URL-safe, auto-generated from name)
       - Create migration: backend/sql/012_phase4.sql
       - Add a public route /characters/public/:slug that renders the character sheet
         read-only, accessible without login
       - Update Supabase RLS on `characters` to allow anonymous SELECT where is_public=true
       - Add a "Share" button to CharacterSheetPage that copies the public URL
       - Add `is_public` boolean column to characters table (default false)
       - Add toggle on CharacterSheetPage to make a character public/private

    2. INITIATIVE TRACKER with HP management
       - Live initiative tracker for use during campaign sessions
       - Combatants: name, initiative roll, current HP, max HP, status/conditions
       - GM can add/remove combatants, edit HP (damage/heal), reorder by initiative
       - Players can see the tracker (read-only) in real-time via Supabase Realtime
       - Store in a new `initiative_entries` table in migration 012_phase4.sql
       - Add as a new tab on CampaignDetailPage (alongside Quest Board, Session, Party)
       - RLS: GM/co-GM can write; all campaign members can read

    3. NOTIFICATION SYSTEM — your turn, quest updated, session starting
       - New `notifications` table: user_id, type, title, message, read, campaign_id, created_at
       - RLS: users see only their own notifications
       - Notification bell icon in the Header with unread count badge
       - Dropdown panel showing recent notifications, click to mark as read
       - Auto-create notifications via Supabase DB triggers or client-side on relevant actions:
           * "Session started" — when a session begins in a campaign you're in
           * "Quest updated" — when a quest status changes in your campaign
           * "Your turn" — when initiative order advances to your character
       - Real-time subscription to own notifications in a new notificationStore.ts
       - Add to migration 012_phase4.sql

    4. MOBILE-RESPONSIVE PASS across all pages
       - Audit every page and major component for mobile breakpoints
       - Fix: Header nav (hamburger menu on mobile), CharacterListPage card grid,
         CampaignDetailPage tabs (scrollable on small screens),
         QuestBoard Kanban (horizontal scroll on mobile),
         CharacterSheet sections (single column on mobile),
         all modals/dialogs (full-width on mobile)
       - Use Tailwind responsive prefixes (sm:, md:, lg:) — no new dependencies needed
       - Test at 375px (iPhone SE), 390px (iPhone 14), 768px (iPad) widths

    5. PDF CHARACTER SHEET EXPORT (client-side, per system)
       - Export any character sheet as a PDF from the CharacterSheetPage
       - Use @react-pdf/renderer (install via pnpm) — renders React components to PDF
       - Create a PdfCharacterSheet component that renders the character's data cleanly
       - "Export PDF" button on CharacterSheetPage
       - PDF should include: character name, system, all sheet section data
       - Keep it system-agnostic — iterate over the sheet layout sections

    6. CAMPAIGN JOURNALS — rich text, image embeds (GM + player notes)
       - New `journal_entries` table: id, campaign_id, author_id, title, content (rich text JSON),
         is_gm_only, created_at, updated_at
       - RLS: all members can read non-gm_only entries; only GM/co-GM can read gm_only entries;
         authors can create/edit their own entries; GM can edit any entry
       - Use Tiptap (install @tiptap/react @tiptap/starter-kit @tiptap/extension-image via pnpm)
         for rich text editing with image embed support
       - New "Journal" tab on CampaignDetailPage
       - Journal list + entry editor with Tiptap
       - GM entries are marked with a lock icon; gm_only toggle for GMs
       - Add to migration 012_phase4.sql

    ---

    IMPLEMENTATION ORDER (follow this):
    1. Write migration 012_phase4.sql (all DB changes in one file)
    2. Mobile responsive pass (no new deps, quick wins)
    3. Public character URLs (small scoped change)
    4. Initiative tracker (builds on existing campaign patterns)
    5. Notification system (new store + header component)
    6. Campaign journals (Tiptap — install first)
    7. PDF export (@react-pdf/renderer — install last as it's heavyweight)

    CONVENTIONS (must follow):
    - TypeScript strict mode — no unused vars/params
    - Use @/ path alias for src/
    - Lucide React for all icons
    - shadcn/ui components for all UI (Card, Button, Dialog, Badge, Tabs, Input, Label)
    - Tailwind v4 for all styling
    - pnpm for installing new packages (run from frontend/)
    - All new Zustand stores follow existing patterns in src/stores/
    - All new Supabase tables need RLS policies in the migration
    - Run pnpm build from frontend/ and verify zero TypeScript errors when done
    - Run pnpm lint from frontend/ and verify zero lint errors when done
    """

    # Toggle steps — turn off what you don't need for faster runs
    STEPS = {
        "manager":        True,   # Plans implementation order and subtasks
        "researcher":     True,   # Confirms best library choices for PDF + rich text
        "architect":      True,   # Designs DB schema, component structure, store patterns
        "developer":      True,   # Implements all 6 features
        "second_opinion": True,   # Verifies correctness of implementation
        "tester":         True,   # Runs build + lint, writes E2E tests
        "debugger":       True,   # Fixes any build/lint/test failures
        "reviewer":       True,   # Security audit of new RLS policies + new code
        "refactorer":     False,
        "documenter":     True,   # Updates CLAUDE.md with new patterns
        "devops":         False,
    }

    asyncio.run(run_pipeline(TASK, STEPS))
