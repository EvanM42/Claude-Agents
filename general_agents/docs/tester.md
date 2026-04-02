# Tester Agent

## What it does
The tester writes and runs tests to verify that code works correctly. It covers happy paths, edge cases, and error cases. When tests fail, it reports what is broken clearly — it does not fix the underlying code.

## When to use it
- After a developer has finished writing a feature
- When you want to verify existing code still works after changes
- When test coverage is missing or incomplete

## Tools it can use
| Tool | Why |
|------|-----|
| Read | Read the code being tested |
| Write | Create test files |
| Bash | Run pytest or other test runners |
| Glob | Find files to test |
| Grep | Search for functions and classes to cover |

## Example task
```
Write and run pytest tests for the authentication module in auth.py, covering login success, wrong password, and missing user cases.
```

## Typical workflow position
**After developer and second opinion.** Reports failures back so the debugger or developer can fix them.
