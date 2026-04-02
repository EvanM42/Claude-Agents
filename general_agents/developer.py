import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

SYSTEM_PROMPT = """
You are a senior software developer. Your job is to write clean, correct,
and maintainable code based on the requirements given to you.

When given a task:
1. Read any relevant existing code first
2. Plan your implementation briefly before writing
3. Write the code — keep it simple and focused
4. Run it to verify it works if possible
5. Do not over-engineer; solve exactly what is asked
"""

async def run(task: str):
    print(f"\n[Developer] Starting: {task}\n")

    async for message in query(
        prompt=task,
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
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
            print(f"\n[Developer] Done (status: {message.subtype})")


if __name__ == "__main__":
    TASK = "Create a Python utility function that reads a JSON file and returns its contents as a dictionary."
    asyncio.run(run(TASK))
