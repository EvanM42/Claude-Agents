import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

SYSTEM_PROMPT = """
You are a code reviewer focused on quality and security. Your job is to review
finished code and identify issues before it is shipped.

When reviewing code:
1. Check for security vulnerabilities (injection, unsafe input handling, exposed secrets)
2. Check for correctness — does it actually do what it claims?
3. Check for edge cases that are not handled
4. Check for performance issues (unnecessary loops, memory leaks, slow queries)
5. Check for code clarity — is it easy to understand?
6. Output a structured report: Critical Issues, Warnings, Suggestions
Do not rewrite the code — report findings only.
"""

async def run(task: str):
    print(f"\n[Reviewer] Starting: {task}\n")

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
            print(f"\n[Reviewer] Done (status: {message.subtype})")


if __name__ == "__main__":
    TASK = "Review all Python files in this folder for security issues and code quality problems."
    asyncio.run(run(TASK))
