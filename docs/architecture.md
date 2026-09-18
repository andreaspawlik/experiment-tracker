# Architecture Decisions

## Consumer Interface Remains Stable

The consumer application preserves its existing public interface unless an
issue explicitly changes it. This keeps each backlog issue independently
testable.

## Dependencies Remain Intentional

New dependencies are not added unless a future issue explicitly requires them.

## Requirements And Feedback Are Separate

GitHub issues and repository instructions define intended behavior. Tests,
coverage CI, pull-request review, and acceptance metrics provide feedback about
whether it was implemented reliably. Metrics do not replace technical review.

## Optimization Is Experiment-Driven

Instruction, test, and workflow changes are recorded in
`metrics/experiments.json` with a baseline, measurable success criteria, and
follow-up observations.
