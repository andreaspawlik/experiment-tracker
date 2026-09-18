# Project Adapter Contract

`agentic-project.json` is the consumer-project adapter for the reusable
agentic engineering workflow. It keeps shared instructions and automation
independent of a particular application.

The contract defines:

- project language and install, test, and coverage commands;
- the coverage threshold;
- the backlog label and Project display name; and
- the user-owned GitHub Project owner, number, IDs, and status options.

When adopting this workflow in another repository, copy the shared `.github`,
scripts, and workflow support, then replace this file with that project's
commands, backlog label, and Project identifiers. Application source files,
tests, issue acceptance criteria, and consumer-specific development rules stay
in the adopting repository.

Validate the contract before changing automation:

```bash
python scripts/project_config.py
```

Run configured commands through the adapter rather than embedding consumer
commands in shared workflows:

```bash
python scripts/project_config.py run project.test_command
python scripts/project_config.py run project.coverage_command
```
