# Development Guide

These conventions keep consumer changes small, testable, and reviewable.

## Change Shape

One pull request implements one GitHub issue. Start from the issue, inspect the
nearest consumer implementation and tests, and make the smallest change that
satisfies the acceptance criteria.

For a new application behavior:

1. Implement the smallest behavior that satisfies the issue.
2. Preserve the consumer application's existing interface unless the issue
   specifies a change.
3. Add focused automated tests for the behavior.
4. Add tests for issue-specific edge cases and errors.

## Compatibility

Preserve the consumer application's existing argument formats, output style,
command names, and successful exit status unless an issue explicitly changes
them. Error behavior must be clear and must not expose a traceback when the
issue requires user-facing error handling.

For workflow and agent inputs, validate values at the boundary that parses them.
Normalize equivalent documented forms, reject malformed values clearly, and test
accepted forms plus invalid-input behavior.

## Categories

Assign exactly one primary category to every issue and pull request. Use the
consumer project's documented taxonomy. The issue body category and GitHub
label must agree.

## Verification

Run the configured test and coverage commands from `agentic-project.json`.
Coverage must meet the configured threshold. Passing tests do not replace
checking every acceptance criterion.
