import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

SYSTEM_PROMPT = """
You are a software tester and QA engineer. Your job is to verify that code
works correctly by writing and running tests.

When given a task:
1. Read the code you are testing thoroughly
2. Identify all cases that need to be tested: happy paths, edge cases, error cases
3. Write tests using pytest (preferred) or unittest
4. Run the tests and report results
5. If tests fail, clearly explain what is broken and why — do not fix the code yourself
"""

async def run(task: str):
    print(f"\n[Tester] Starting: {task}\n")

    async for message in query(
        prompt=task,
        options=ClaudeAgentOptions(
            model="claude-sonnet-4-6",
            allowed_tools=["Read", "Write", "Bash", "Glob", "Grep"],
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
            print(f"\n[Tester] Done (status: {message.subtype})")


if __name__ == "__main__":
    TASK = "Find all Python files in this folder and write basic tests for any functions you find."
    asyncio.run(run(TASK))
