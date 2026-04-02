# Researcher Agent

## What it does
The researcher investigates topics, compares libraries and frameworks, and produces a clear recommendation. It focuses on up-to-date information and trade-offs — it does not write implementation code.

## When to use it
- Before starting a project, to pick the right tools
- When you're unsure which library or approach to use
- When you need to understand a technology before using it

## Tools it can use
| Tool | Why |
|------|-----|
| WebSearch | Find current information and comparisons |
| WebFetch | Read documentation and articles in detail |
| Read | Review existing project requirements |
| Glob | Check what is already in the project |

## Example task
```
Research the best options for adding a job queue to a Python app. Compare Celery, RQ, and Dramatiq.
```

## Typical workflow position
**First.** Feeds findings to the architect, who then designs the system.
