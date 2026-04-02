# Debugger Agent

## What it does
The debugger finds the root cause of bugs and errors through methodical investigation. It reads error messages, traces code logic, forms a hypothesis, verifies it, and proposes a minimal fix. It does not rewrite working code.

## When to use it
- When there is a specific error or bug to diagnose
- When tests are failing and it's unclear why
- When unexpected behavior occurs at runtime

## Tools it can use
| Tool | Why |
|------|-----|
| Read | Read source code and error logs |
| Bash | Run code to reproduce the error |
| Glob | Find relevant files |
| Grep | Search for where specific variables or functions are used |
| Edit | Apply the minimal fix once the cause is found |

## Example task
```
The app crashes with a KeyError on startup. Here is the stack trace: [paste trace]. Find and fix the root cause.
```

## Typical workflow position
**After tester** when tests fail, or **on demand** when a bug is reported. Hands fixes back to the tester to verify.
