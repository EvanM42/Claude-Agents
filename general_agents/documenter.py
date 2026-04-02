import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

SYSTEM_PROMPT = """
You are a technical writer and documentation specialist. Your job is to write
clear, accurate documentation for code and projects.

When documenting:
1. Read the code thoroughly before writing anything
2. Write a README if one does not exist, or update it if it does
3. Add docstrings to functions and classes that lack them
4. Write usage examples that actually work
5. Document setup steps, dependencies, and environment requirements
6. Keep language simple and direct — avoid jargon where possible
"""

async def run(task: str):
    print(f"\n[Documenter] Starting: {task}\n")

    async for message in query(
        prompt=task,
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"],
            permission_mode="acceptEdits",
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
            print(f"\n[Documenter] Done (status: {message.subtype})")


if __name__ == "__main__":
    TASK = "Read all the agent Python files in this folder and create a README.md that explains what each agent does and how to use them."
    asyncio.run(run(TASK))
