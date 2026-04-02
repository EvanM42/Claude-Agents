import asyncio
import os
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

# ---------------------------------------------------------------
# SETUP
# Make sure your API key is set before running:
#   Windows terminal: set ANTHROPIC_API_KEY=sk-ant-...
#   Or hardcode it below (not recommended for shared projects):
#   os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."
# ---------------------------------------------------------------

async def run_agent(task: str):
    """Run a single agent with a given task."""
    print(f"\n--- Agent starting ---")
    print(f"Task: {task}\n")

    async for message in query(
        prompt=task,
        options=ClaudeAgentOptions(
            # Limit which tools the agent can use
            allowed_tools=["Read", "Write", "Edit", "Glob", "Grep", "Bash"],

            # Auto-approve file edits so the agent doesn't pause to ask
            permission_mode="acceptEdits",

            # Give the agent a role/personality
            system_prompt="You are a helpful Python developer assistant. Write clean, simple code.",
        ),
    ):
        # AssistantMessage = Claude thinking/acting
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text") and block.text:
                    print(block.text)
                elif hasattr(block, "name"):
                    print(f"[Tool used: {block.name}]")

        # ResultMessage = agent finished
        elif isinstance(message, ResultMessage):
            print(f"\n--- Agent finished (status: {message.subtype}) ---")


# ---------------------------------------------------------------
# EXAMPLE TASKS — change these to whatever you want the agent to do
# ---------------------------------------------------------------

TASK = """
Create a Python file called hello_agent.py in the current directory.
It should print 'Hello from my first Claude agent!' when run.
Then run it with Python to confirm it works.
"""

if __name__ == "__main__":
    asyncio.run(run_agent(TASK))
