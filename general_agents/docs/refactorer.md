# Refactorer Agent

## What it does
The refactorer improves the internal quality of working code without changing its behavior. It removes duplication, simplifies complex logic, improves naming, and cleans up structure. It runs tests after changes to confirm nothing broke.

## When to use it
- After a feature is working and tested
- When code has grown messy over time
- When the reviewer flags quality issues that need addressing

## Tools it can use
| Tool | Why |
|------|-----|
| Read | Understand code fully before changing it |
| Edit | Make targeted improvements |
| Bash | Run tests to confirm behavior is unchanged |
| Glob | Find related files |
| Grep | Find all usages of something being renamed or changed |

## Example task
```
Refactor utils.py to remove duplicated logic and improve variable naming. Do not change any behavior.
```

## Typical workflow position
**After reviewer.** The final code quality pass before documentation.
