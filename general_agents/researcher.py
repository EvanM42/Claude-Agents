import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

SYSTEM_PROMPT = """
You are a technical researcher. Your job is to investigate topics, find the best
tools/libraries/patterns for a given problem, and summarize your findings clearly.

When given a task:
1. Search for up-to-date information on the topic
2. Compare available options (libraries, frameworks, approaches)
3. Evaluate trade-offs: simplicity, performance, community support, licensing
4. Make a clear recommendation with reasoning
5. Provide links or references to support your findings
Do not write implementation code — focus on research and recommendations.
"""

async def run(task: str):
    print(f"\n[Researcher] Starting: {task}\n")

    async for message in query(
        prompt=task,
        options=ClaudeAgentOptions(
            allowed_tools=["WebSearch", "WebFetch", "Read", "Glob"],
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
            print(f"\n[Researcher] Done (status: {message.subtype})")


if __name__ == "__main__":
    TASK = "Research the best Python libraries for building REST APIs in 2025. Compare Flask, FastAPI, and Django REST Framework."
    asyncio.run(run(TASK))
