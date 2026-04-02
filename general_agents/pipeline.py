"""
pipeline.py — Full agent pipeline for building software projects.

Usage:
    python pipeline.py

Edit the PROJECT variable at the bottom to describe what you want to build.
Toggle steps on/off using the STEPS dict.
"""

import asyncio
from dataclasses import dataclass, field
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

# ---------------------------------------------------------------
# CORE: Run a single agent and return its final result as a string
# ---------------------------------------------------------------

async def run_agent(
    label: str,
    task: str,
    system_prompt: str,
    allowed_tools: list[str],
    permission_mode: str = "default",
    verbose: bool = True,
) -> str:
    """Run an agent and return its final result text."""
    print(f"\n{'=' * 60}")
    print(f"  [{label.upper()}]")
    print(f"{'=' * 60}")

    result_text = ""

    async for message in query(
        prompt=task,
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
                        print(f"  → Tool: {block.name}")

        elif isinstance(message, ResultMessage):
            result_text = message.result or ""
            status = message.subtype
            print(f"\n  [{label.upper()}] finished — status: {status}")

    return result_text


# ---------------------------------------------------------------
# AGENT DEFINITIONS
# ---------------------------------------------------------------

AGENTS = {
    "manager": {
        "system_prompt": """You are a senior engineering manager. Break down the project task into
a clear, ordered list of subtasks. Identify what needs to be researched, designed, built, and tested.
Output a structured plan only — do not write code.""",
        "tools": ["Read", "Glob", "Grep", "Bash"],
        "permission_mode": "default",
    },
    "researcher": {
        "system_prompt": """You are a technical researcher. Investigate the best tools, libraries,
and patterns for the given task. Compare options and make a clear recommendation with reasoning.
Do not write implementation code.""",
        "tools": ["WebSearch", "WebFetch", "Read", "Glob"],
        "permission_mode": "default",
    },
    "architect": {
        "system_prompt": """You are a software architect. Design the system structure based on the
research and plan provided. Define components, file/folder layout, data flow, and technology choices.
Output a written design — do not write implementation code.""",
        "tools": ["Read", "Glob", "Grep", "WebSearch"],
        "permission_mode": "default",
    },
    "developer": {
        "system_prompt": """You are a senior software developer. Implement the system based on the
architecture and plan provided. Write clean, working code. Read existing files before changing them.
Run code to verify it works.""",
        "tools": ["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
        "permission_mode": "acceptEdits",
    },
    "second_opinion": {
        "system_prompt": """You are a skeptical senior developer providing a second opinion.
Challenge assumptions, find flaws, and suggest better approaches where warranted.
Be direct. Also acknowledge what is done well.""",
        "tools": ["Read", "Glob", "Grep"],
        "permission_mode": "default",
    },
    "tester": {
        "system_prompt": """You are a QA engineer. Write and run pytest tests covering happy paths,
edge cases, and error cases. Report all failures clearly. Do not fix the code yourself.""",
        "tools": ["Read", "Write", "Bash", "Glob", "Grep"],
        "permission_mode": "acceptEdits",
    },
    "debugger": {
        "system_prompt": """You are an expert debugger. Find root causes of failures methodically.
Read errors, trace logic, verify your hypothesis, and apply a minimal fix. Do not rewrite working code.""",
        "tools": ["Read", "Edit", "Bash", "Glob", "Grep"],
        "permission_mode": "acceptEdits",
    },
    "reviewer": {
        "system_prompt": """You are a code reviewer focused on quality and security.
Produce a structured report: Critical Issues, Warnings, Suggestions.
Do not rewrite code — report findings only.""",
        "tools": ["Read", "Glob", "Grep"],
        "permission_mode": "default",
    },
    "refactorer": {
        "system_prompt": """You are a refactoring specialist. Improve code quality without changing behavior.
Remove duplication, simplify logic, improve naming. Run tests after to confirm nothing broke.""",
        "tools": ["Read", "Edit", "Bash", "Glob", "Grep"],
        "permission_mode": "acceptEdits",
    },
    "documenter": {
        "system_prompt": """You are a technical writer. Write clear documentation: README, docstrings,
usage examples, and setup instructions. Always read the code before writing anything.""",
        "tools": ["Read", "Write", "Edit", "Glob", "Grep"],
        "permission_mode": "acceptEdits",
    },
    "devops": {
        "system_prompt": """You are a DevOps engineer. Create everything needed to run and deploy
the app: Dockerfile, docker-compose, .env.example, CI workflow. Think about reliability and portability.""",
        "tools": ["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
        "permission_mode": "acceptEdits",
    },
}


# ---------------------------------------------------------------
# PIPELINE
# ---------------------------------------------------------------

@dataclass
class PipelineConfig:
    project: str                    # High-level description of what to build
    output_dir: str = "."           # Where files should be created
    steps: dict = field(default_factory=lambda: {
        "manager":       True,
        "researcher":    True,
        "architect":     True,
        "developer":     True,
        "second_opinion": True,
        "tester":        True,
        "debugger":      True,   # Runs only if tester reports failures
        "reviewer":      True,
        "refactorer":    True,
        "documenter":    True,
        "devops":        False,  # Off by default — turn on if you need deployment config
    })
    verbose: bool = True


async def run_pipeline(config: PipelineConfig):
    """Run the full agent pipeline for a project."""
    context = {}   # Accumulated outputs passed forward to each agent
    steps = config.steps

    def build_task(role: str, base_task: str) -> str:
        """Prepend relevant prior context to each agent's task."""
        parts = [f"Project goal: {config.project}", f"Working directory: {config.output_dir}", ""]
        if role != "manager" and "manager" in context:
            parts.append(f"Project plan from manager:\n{context['manager']}\n")
        if role in ("architect", "developer", "devops") and "researcher" in context:
            parts.append(f"Research findings:\n{context['researcher']}\n")
        if role in ("developer", "second_opinion", "tester", "debugger", "reviewer", "refactorer") and "architect" in context:
            parts.append(f"Architecture design:\n{context['architect']}\n")
        if role in ("second_opinion", "tester", "reviewer", "refactorer", "documenter") and "developer" in context:
            parts.append(f"Developer notes:\n{context['developer']}\n")
        if role == "debugger" and "tester" in context:
            parts.append(f"Test failures to fix:\n{context['tester']}\n")
        if role in ("reviewer", "refactorer") and "second_opinion" in context:
            parts.append(f"Second opinion feedback:\n{context['second_opinion']}\n")
        parts.append(base_task)
        return "\n".join(parts)

    # ---- 1. MANAGER ----
    if steps.get("manager"):
        context["manager"] = await run_agent(
            label="Manager",
            task=build_task("manager", "Analyze the project goal and produce a detailed, ordered plan."),
            **AGENTS["manager"],
            verbose=config.verbose,
        )

    # ---- 2. RESEARCHER ----
    if steps.get("researcher"):
        context["researcher"] = await run_agent(
            label="Researcher",
            task=build_task("researcher", "Research the best tools, libraries, and patterns for this project. Make clear recommendations."),
            **AGENTS["researcher"],
            verbose=config.verbose,
        )

    # ---- 3. ARCHITECT ----
    if steps.get("architect"):
        context["architect"] = await run_agent(
            label="Architect",
            task=build_task("architect", "Design the system architecture. Define components, file structure, and data flow."),
            **AGENTS["architect"],
            verbose=config.verbose,
        )

    # ---- 4. DEVELOPER ----
    if steps.get("developer"):
        context["developer"] = await run_agent(
            label="Developer",
            task=build_task("developer", f"Implement the project in {config.output_dir}. Follow the architecture. Write clean, working code."),
            **AGENTS["developer"],
            verbose=config.verbose,
        )

    # ---- 5. SECOND OPINION ----
    if steps.get("second_opinion"):
        context["second_opinion"] = await run_agent(
            label="Second Opinion",
            task=build_task("second_opinion", "Review the implementation critically. Challenge any flawed decisions and suggest improvements."),
            **AGENTS["second_opinion"],
            verbose=config.verbose,
        )

    # ---- 6. TESTER ----
    if steps.get("tester"):
        context["tester"] = await run_agent(
            label="Tester",
            task=build_task("tester", "Write and run tests. Cover happy paths, edge cases, and error cases. Report all failures clearly."),
            **AGENTS["tester"],
            verbose=config.verbose,
        )

    # ---- 7. DEBUGGER (only if tester found failures) ----
    if steps.get("debugger"):
        tester_output = context.get("tester", "").lower()
        if any(word in tester_output for word in ["fail", "error", "exception", "broken", "assert"]):
            print("\n  [PIPELINE] Test failures detected — running debugger...")
            context["debugger"] = await run_agent(
                label="Debugger",
                task=build_task("debugger", "Fix all failing tests. Find root causes and apply minimal fixes."),
                **AGENTS["debugger"],
                verbose=config.verbose,
            )
        else:
            print("\n  [PIPELINE] No test failures detected — skipping debugger.")

    # ---- 8. REVIEWER ----
    if steps.get("reviewer"):
        context["reviewer"] = await run_agent(
            label="Reviewer",
            task=build_task("reviewer", "Audit the codebase for security vulnerabilities and quality issues. Produce a structured report."),
            **AGENTS["reviewer"],
            verbose=config.verbose,
        )

    # ---- 9. REFACTORER ----
    if steps.get("refactorer"):
        context["refactorer"] = await run_agent(
            label="Refactorer",
            task=build_task("refactorer", "Improve code quality without changing behavior. Address any issues flagged by the reviewer."),
            **AGENTS["refactorer"],
            verbose=config.verbose,
        )

    # ---- 10. DOCUMENTER ----
    if steps.get("documenter"):
        context["documenter"] = await run_agent(
            label="Documenter",
            task=build_task("documenter", "Write a README, docstrings, and usage examples for the project."),
            **AGENTS["documenter"],
            verbose=config.verbose,
        )

    # ---- 11. DEVOPS ----
    if steps.get("devops"):
        context["devops"] = await run_agent(
            label="DevOps",
            task=build_task("devops", "Create a Dockerfile, docker-compose.yml, .env.example, and a GitHub Actions CI workflow."),
            **AGENTS["devops"],
            verbose=config.verbose,
        )

    print(f"\n{'=' * 60}")
    print("  PIPELINE COMPLETE")
    print(f"{'=' * 60}\n")
    return context


# ---------------------------------------------------------------
# CONFIGURE YOUR PROJECT HERE
# ---------------------------------------------------------------

if __name__ == "__main__":
    config = PipelineConfig(
        # Describe what you want to build
        project="""
        A command-line to-do list app in Python.
        Users can add tasks, list tasks, mark tasks as done, and delete tasks.
        Tasks should persist between runs using a local JSON file.
        """,

        # Where the agent should create files
        output_dir="./output/todo_app",

        # Toggle individual steps on/off
        steps={
            "manager":        True,
            "researcher":     True,
            "architect":      True,
            "developer":      True,
            "second_opinion": True,
            "tester":         True,
            "debugger":       True,
            "reviewer":       True,
            "refactorer":     True,
            "documenter":     True,
            "devops":         False,  # Set to True if you want Docker/CI config
        },
    )

    asyncio.run(run_pipeline(config))
