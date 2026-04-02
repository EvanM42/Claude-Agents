# Documenter Agent

## What it does
The documenter writes clear, accurate documentation for code and projects. This includes READMEs, function docstrings, usage examples, and setup instructions. It always reads the code thoroughly before writing anything.

## When to use it
- After a feature is complete and reviewed
- When a project lacks a README or setup guide
- When functions and classes are missing docstrings

## Tools it can use
| Tool | Why |
|------|-----|
| Read | Read code before documenting it |
| Write | Create new documentation files |
| Edit | Update existing docs or add docstrings |
| Glob | Find all files that need documentation |
| Grep | Find undocumented functions and classes |

## Example task
```
Read the entire project and create a README.md with setup instructions, usage examples, and a description of each module.
```

## Typical workflow position
**Last.** Runs after refactoring when the code is in its final state.
