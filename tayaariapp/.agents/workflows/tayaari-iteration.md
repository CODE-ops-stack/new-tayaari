# Tayaari Pakki Engineering Iteration

## Objective

Execute one complete, evidence-driven product engineering iteration and, when the roadmap contains another safe high-value task, continue to the next iteration.

## Phase 1 — Repository Inspection

1. Inspect the actual repository before making assumptions.
2. Read the relevant architecture and existing implementations.
3. Search for existing components before creating new ones.
4. Identify duplicate or overlapping engines.
5. Check database schema/version/migrations when persistence is involved.
6. Check existing tests before modifying implementation.

Never trust previous agent completion reports without source verification.

## Phase 2 — Determine Highest-Value Work

Determine the highest-value remaining improvement based on:

1. Correctness
2. Exam integrity
3. Learner benefit
4. Reliability
5. UX
6. Performance
7. Architecture
8. Feature novelty

Do not add features merely because they sound impressive.

Do not optimize feature count.

Prefer solving an actual aspirant pain point.

## Phase 3 — Evidence Verification

If the task depends on current exam rules, verify them from authoritative sources.

Clearly distinguish:

OFFICIAL EVIDENCE
SECONDARY EVIDENCE
INFERENCE
UNKNOWN

Never fabricate missing evidence.

If evidence is insufficient, preserve INSUFFICIENT DATA.

## Phase 4 — Design

Before implementation:

1. Identify affected components.
2. Identify data-model implications.
3. Identify migration implications.
4. Identify scoring implications.
5. Identify learner-model implications.
6. Identify UI/UX implications.
7. Identify regression risks.

Prefer extending existing correct architecture instead of creating duplicate systems.

## Phase 5 — Implementation

Implement the smallest robust architecture that solves the problem.

Maintain:

- deterministic exam rules
- semantic attempt outcomes
- semantic option roles
- exact scoring semantics
- safe database migrations
- offline-first core learning
- evidence-based learner analytics

Never fabricate data simply to make a feature appear intelligent.

Never delete tests just to obtain a green build.

## Phase 6 — Targeted Verification

Immediately test the changed behavior.

Tests should verify real behavior rather than merely checking that code compiles.

When persistence is involved, test actual database behavior.

When migrations change, test the real migration chain.

When scoring changes, test exact mathematical outcomes.

When learner intelligence changes, test evidence thresholds and edge cases.

## Phase 7 — Regression

Run the relevant existing regression suite.

Then run:

- compile checks
- unit tests
- migration tests
- scoring tests
- relevant integration tests
- UI-related tests when applicable

Do not weaken or remove meaningful tests to make the build pass.

## Phase 8 — Adversarial Audit

After tests pass, actively try to break the implementation.

Check for:

- hardcoded exam rules
- duplicate business logic
- incorrect outcome semantics
- incorrect OptionRole handling
- false analytics
- insufficient evidence thresholds
- data loss
- migration failures
- repeated-question contamination
- incorrect scoring
- UI state inconsistencies
- offline failures
- unnecessary network calls
- performance regressions
- unsupported claims

A green build is not sufficient evidence of product correctness.

## Phase 9 — Product Audit

Evaluate the change from three perspectives:

### Learner

Does this actually help an aspirant?

### Teacher

Is the feedback educationally meaningful and evidence-based?

### Engineering

Is the implementation maintainable, deterministic, tested and integrated?

If the feature does not materially improve the product, do not keep adding complexity.

## Phase 10 — Fix

If any defect is found:

1. Fix it.
2. Re-run targeted tests.
3. Re-run regression tests.
4. Re-run the relevant audit.

Do not simply report the defect and stop if it can safely be fixed.

## Phase 11 — Build Verification

Run the appropriate build.

Report exact evidence:

- build result
- tests discovered
- tests executed
- passed
- failed
- skipped
- migration status
- relevant regression status

Never claim READY based only on compilation.

## Phase 12 — Continue

If the requested roadmap contains another clearly defined safe task, continue automatically.

Do not stop after every successful subtask asking for permission.

Stop only when:

1. The current roadmap is exhausted,
2. a genuinely ambiguous product decision requires the user,
3. destructive/high-risk action requires explicit approval,
4. required external information cannot be verified,
5. or a blocking technical issue cannot be safely resolved.

## Final Principle

The goal is not:

"make the code look complete."

The goal is:

"make Tayaari Pakki genuinely better at helping an aspirant prepare and score well, with evidence proving that the system behaves correctly."

Every iteration should move toward:

MISTAKE
-> EVIDENCE
-> UNDERSTANDING
-> REPAIR
-> TRANSFER
-> RETENTION
-> EXAM READINESS
-> NEXT BEST ACTION
