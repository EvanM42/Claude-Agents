import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

SYSTEM_PROMPT = """
You are an expert debugger. Your job is to find the root cause of bugs and errors.
You do not guess — you investigate methodically.

When given a bug or error:
1. Read the full error message and stack trace carefully
2. Read the relevant source code
3. Form a hypothesis about the root cause
4. Verify the hypothesis by tracing the code logic
5. Identify the exact line or lines responsible
6. Explain the root cause clearly
7. Propose a minimal fix — do not rewrite working code
"""

async def run(task: str):
    print(f"\n[Debugger] Starting: {task}\n")

    async for message in query(
        prompt=task,
        options=ClaudeAgentOptions(
            model="claude-opus-4-6",
            allowed_tools=["Read", "Bash", "Glob", "Grep", "Edit"],
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
            print(f"\n[Debugger] Done (status: {message.subtype})")


if __name__ == "__main__":
    TASK = "Run the starter_agent.py file and debug any errors that occur."
    asyncio.run(run(TASK))
