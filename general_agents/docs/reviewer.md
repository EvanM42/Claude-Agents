# Reviewer Agent

## What it does
The reviewer audits finished code for quality and security issues before it is shipped. It produces a structured report with Critical Issues, Warnings, and Suggestions. It does not rewrite code — it reports findings only.

## When to use it
- After the developer finishes a feature and tests pass
- Before merging code into a main branch
- When security is a concern and you want a dedicated audit

## Tools it can use
| Tool | Why |
|------|-----|
| Read | Read all code being reviewed |
| Glob | Find all relevant files |
| Grep | Search for known bad patterns (e.g., hardcoded secrets, unsafe calls) |

## Review checklist
- Security vulnerabilities (injection, exposed secrets, unsafe input)
- Correctness (does it do what it claims?)
- Unhandled edge cases
- Performance issues
- Code clarity

## Example task
```
Review the payment processing module in payments.py for security vulnerabilities and correctness issues.
```

## Typical workflow position
**After tester passes.** Final check before the refactorer cleans up or the documenter writes docs.
