import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

SYSTEM_PROMPT = """
You are a refactoring specialist. Your job is to improve the internal quality of
working code without changing its behavior.

When refactoring code:
1. Read and fully understand the code before changing anything
2. Identify duplication, overly complex logic, poor naming, or structural issues
3. Make targeted improvements — one concern at a time
4. Do NOT add new features or change behavior
5. After changes, verify the code still works by running tests if available
6. Explain each change you made and why
"""

async def run(task: str):
    print(f"\n[Refactorer] Starting: {task}\n")

    async for message in query(
        prompt=task,
        options=ClaudeAgentOptions(
            model="claude-sonnet-4-6",
            allowed_tools=["Read", "Edit", "Bash", "Glob", "Grep"],
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
            print(f"\n[Refactorer] Done (status: {message.subtype})")


if __name__ == "__main__":
    TASK = "Refactor the starter_agent.py file to improve its structure and readability without changing its behavior."
    asyncio.run(run(TASK))
