# Developer Agent

## What it does
The developer writes clean, working code based on a given specification or task. It reads existing code before making changes, keeps implementations simple, and verifies its work runs correctly.

## When to use it
- When you need new code written
- When you need an existing feature extended
- After the architect has produced a plan and it's time to implement

## Tools it can use
| Tool | Why |
|------|-----|
| Read | Understand existing code before changing it |
| Write | Create new files |
| Edit | Modify existing files |
| Bash | Run code to verify it works |
| Glob | Find relevant files |
| Grep | Search for patterns in the codebase |

## Example task
```
Implement a user login endpoint using FastAPI that validates credentials against a SQLite database.
```

## Typical workflow position
**Middle.** Comes after the architect/researcher, before the tester and reviewer.
