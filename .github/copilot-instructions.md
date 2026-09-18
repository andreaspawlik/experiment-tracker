# Repository Instructions

## Scope

These instructions apply to every change in this repository. Follow the
role-specific guidance in `.github/agents/` as well.

Before editing, read `docs/development-guide.md` and
`docs/architecture.md`. Treat those documents as the repository's detailed
development and design guidance.

Project-specific commands, coverage settings, backlog identity, and GitHub
Project identifiers are defined in `agentic-project.json`. Read that contract
before changing workflows or repository-usage guidance; do not hardcode values
from one consumer project into shared automation.

## Engineering conventions

- Implement exactly one GitHub issue per pull request.
- Treat the issue's acceptance criteria as the source of truth; do not invent
  adjacent product scope.
- Preserve the consumer project's existing command names, argument formats,
  output, and exit behavior unless the issue explicitly changes them.
- Prefer small, direct functions over new abstractions for single operations.
- Use type annotations and clear names; avoid one-letter variables outside
  conventional mathematical parameters such as `a` and `b`.
- Validate external inputs at their owning boundary. Normalize documented
  equivalent forms, reject malformed values with clear errors, and add tests
  for each accepted form and the invalid-input path.

## Required verification

- Add or update focused unit and CLI tests for each new behavior.
- Add edge-case tests for behavior called out by the issue.
- For numeric operations, explicitly handle and test non-finite inputs such as
  `nan` and positive or negative infinity when the CLI accepts floats.
- For workflow, agent, or repository-usage changes, update the README with the
  user-facing workflow and link any detailed guide that was added or changed.
- Run the narrowest relevant check first, then the full test suite.
- Run the configured test and coverage commands from `agentic-project.json`
  before opening a pull request; coverage must meet the configured threshold.
- Do not treat passing tests as a substitute for checking every acceptance
  criterion.
- When changing instructions or workflow guidance, link the change to an entry
  in `metrics/experiments.json` and define how a future result will be compared.

## Pull requests and commits

- Use a feature branch named after the issue, such as
  `issue-12-modulo-command`.
- Reference the issue in the pull request and use `Closes #N` when the issue
  should close on merge.
- Keep commits and pull requests focused; do not mix unrelated cleanup with
  feature work.
- Complete the pull request checklist and report files changed, tests run,
  branch name, and pull request URL.

## Review expectations

Reviewers should report blocking correctness, regression, test, and
acceptance-criteria gaps before minor suggestions. Passing CI is evidence, not
proof that the issue is complete.
