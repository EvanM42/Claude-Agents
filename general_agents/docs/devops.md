# DevOps Agent

## What it does
The DevOps agent handles everything needed to run and deploy an application: Dockerfiles, environment setup, CI/CD pipelines, startup scripts, and configuration files. It ensures the app can run cleanly in any environment.

## When to use it
- When you need to containerize an app with Docker
- When setting up a CI/CD pipeline (GitHub Actions, etc.)
- When configuring environment variables and secrets management
- When writing setup or deployment scripts

## Tools it can use
| Tool | Why |
|------|-----|
| Read | Understand the project before configuring it |
| Write | Create Dockerfiles, configs, pipeline files |
| Edit | Update existing configuration |
| Bash | Run and test commands |
| Glob | Find existing config files |
| Grep | Search for hardcoded values that should be env vars |

## Example task
```
Create a Dockerfile, docker-compose.yml, and GitHub Actions CI workflow for this Python web app.
```

## Typical workflow position
**Parallel to or after developer.** Can set up infrastructure while development is ongoing, or finalize deployment config after the app is built.
