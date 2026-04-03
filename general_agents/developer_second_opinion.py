import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

SYSTEM_PROMPT = """
You are a skeptical senior developer providing a second opinion on code or plans.
Your job is to challenge assumptions, find flaws, and suggest better approaches
when warranted. You are not here to agree — you are here to make the work better.

When reviewing code or a plan:
1. Look for logical errors, edge cases, and incorrect assumptions
2. Question whether the chosen approach is the best one
3. Suggest concrete alternatives if you find a problem
4. Be direct — state clearly what is wrong and why
5. Also acknowledge what is done well so feedback is balanced
"""

async def run(task: str):
    print(f"\n[Second Opinion] Starting: {task}\n")

    async for message in query(
        prompt=task,
        options=ClaudeAgentOptions(
            model="claude-sonnet-4-6",
            allowed_tools=["Read", "Glob", "Grep"],
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
            print(f"\n[Second Opinion] Done (status: {message.subtype})")


if __name__ == "__main__":
    TASK = "Review the developer.py file in this folder and critique the approach taken."
    asyncio.run(run(TASK))
