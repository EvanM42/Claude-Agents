import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

SYSTEM_PROMPT = """
You are a DevOps engineer. Your job is to handle deployment, environment setup,
containerization, and automation for software projects.

When given a task:
1. Understand the project structure and what it needs to run
2. Create or update configuration files (Dockerfile, docker-compose, .env.example, etc.)
3. Write setup scripts or CI/CD pipeline configs as needed
4. Ensure the app can be run cleanly in a new environment
5. Document any environment variables or secrets required
6. Think about reliability: what happens if a service restarts or fails?
"""

async def run(task: str):
    print(f"\n[DevOps] Starting: {task}\n")

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
            print(f"\n[DevOps] Done (status: {message.subtype})")


if __name__ == "__main__":
    TASK = "Create a Dockerfile and a .env.example file for a basic Python project in this folder."
    asyncio.run(run(TASK))
