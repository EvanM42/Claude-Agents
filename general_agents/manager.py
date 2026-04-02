import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

SYSTEM_PROMPT = """
You are a senior engineering manager overseeing a software project.
Your job is to break down tasks, delegate to the right specialists, and
ensure the project moves forward coherently. You do not write code yourself —
you plan, coordinate, and verify that work is done correctly.

When given a task:
1. Analyze what needs to be done
2. Break it into clear subtasks
3. Decide which specialist should handle each subtask
4. Summarize results and flag any unresolved issues
"""

async def run(task: str):
    print(f"\n[Manager] Starting: {task}\n")

    async for message in query(
        prompt=task,
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Glob", "Grep", "Bash"],
            system_prompt=SYSTEM_PROMPT,
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text") and block.text:
                    print(block.text)
                elif hasattr(block, "name"):
                    print(f"[Tool: {block.name}]")
        elif isinstance(message, ResultMessage):
            print(f"\n[Manager] Done (status: {message.subtype})")


if __name__ == "__main__":
    TASK = "Review the project structure and create a high-level plan for what needs to be built next."
    asyncio.run(run(TASK))
