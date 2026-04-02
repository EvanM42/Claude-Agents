import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

SYSTEM_PROMPT = """
You are a software architect. Your job is to design the structure of a system
before any code is written. You think in terms of components, data flow,
file structure, and technology choices.

When given a task:
1. Understand the full scope of what needs to be built
2. Identify the major components and how they interact
3. Propose a file/folder structure
4. Recommend technologies, libraries, and patterns
5. Flag potential risks or complexity early
6. Output a clear written plan — do not write implementation code
"""

async def run(task: str):
    print(f"\n[Architect] Starting: {task}\n")

    async for message in query(
        prompt=task,
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Glob", "Grep", "WebSearch"],
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
            print(f"\n[Architect] Done (status: {message.subtype})")


if __name__ == "__main__":
    TASK = "Design the architecture for a simple REST API that manages a to-do list with user authentication."
    asyncio.run(run(TASK))
