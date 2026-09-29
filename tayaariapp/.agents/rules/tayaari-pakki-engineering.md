# TAYAARI PAKKI — ENGINEERING CONSTITUTION

## SOURCE OF TRUTH
The actual repository is the source of truth.

Never trust previous agent READY/COMPLETE reports without inspecting the actual implementation, tests, database schema, and build evidence.

Never assume a feature exists merely because a previous agent claimed it was implemented.

## PRODUCT MISSION
Tayaari Pakki is an evidence-driven exam preparation system.

Its purpose is to help an aspirant improve exam performance by determining the highest-value next learning action from actual evidence.

Prioritize:
exam relevance × learner need × learning value × measurable improvement.

Do not optimize for feature count.

## ANTI-BLUFF
Never fabricate:
- PYQ provenance
- exam rules
- trap metadata
- learner weaknesses
- psychological diagnoses
- mastery
- rank predictions
- selection predictions
- guaranteed score improvement
- unsupported causal explanations

When evidence is insufficient, explicitly use:
INSUFFICIENT DATA.

Truth is more important than feature completeness.

## EXAM BLUEPRINTS
All exam-specific behavior must come from versioned ExamBlueprint configuration.

Never hardcode exam scoring, option count, penalty, timing, or other exam rules inside UI/business logic.

Keep active and historical exam configurations separate.

Before changing an exam rule, verify it from authoritative/current sources when required.

## ATTEMPT SEMANTICS
Never reduce learner outcomes to a boolean.

Preserve:
CORRECT
INCORRECT
ABSTAINED
UNANSWERED

ABSTAINED and UNANSWERED must never silently become INCORRECT.

## OPTION SEMANTICS
Use semantic OptionRole.

Never determine semantic meaning from a literal option label or ID.

Never use option.id == "E" to determine whether an option represents abstention or another semantic role.

The displayed letter and semantic role are separate concepts.

## SCORING
Maintain one authoritative scoring engine.

Represent exam penalties semantically such as:
ONE_THIRD
ONE_FOURTH
NONE

Do not define exam rules using floating-point approximations such as -0.33 or -0.25.

Do not duplicate scoring logic across UI, ViewModel, Repository, and Analytics.

Every scoring change requires regression tests.

## DATABASE SAFETY
Never perform destructive migrations.

Never erase learner history to solve schema problems.

Protect:
- attempts
- revision
- mastery
- bookmarks
- analytics
- confusion evidence
- replay outcomes

Test the real migration chain whenever the schema changes.

## QUESTION FAMILIES
Distinguish:
EXACT_REPETITION
FAMILY_STAGE_REPETITION
FAMILY_PROGRESSION

A failed question must not suppress an entire question family.

Do not fabricate familyId or familyStage metadata.

Prefer conceptual transfer over immediate memorization.

## CONFUSION ENGINE
Confusion evidence must be based on distinct questions.

Evidence ladder:
1 distinct question = POSSIBLE
2-3 distinct questions = EMERGING
4+ distinct questions = CONFIRMED

Repeated attempts of the same question do not create independent evidence.

Never use history.isNotEmpty() as sufficient confirmation logic.

## TRAP ANALYTICS
Only verified trap metadata may create verified trap diagnoses.

Never synthetically inject trap labels simply to increase analytics coverage.

Missing trap metadata means insufficient diagnostic evidence.

## MISTAKE REPLAY
Mistake Replay is a repair system, not a wrong-answer list.

Preferred loop:

MISTAKE
-> EVIDENCE
-> REPAIR
-> ALTERNATE QUESTION
-> TRANSFER
-> OUTCOME
-> LEARNER MODEL
-> REVISION
-> NEXT ACTION

Do not claim mastery from a single successful replay.

## LEARNER MODEL
Maintain one coherent learner model.

Do not create competing intelligence engines.

Use measurable evidence such as:
- accuracy
- recency
- repetition
- confidence
- time
- topic
- concept
- format
- difficulty
- family
- transfer
- revision state

## NEXT-BEST ACTION
Every recommendation must be explainable through:

WHY
WHY NOW
WHAT IT IMPROVES

The best next action may be:
- practice
- revision
- mistake replay
- contrast
- trap training
- prerequisite repair
- transfer
- timed drill
- exam simulation

Do not force question practice when another action has greater evidence-based value.

## GEMINI / AI
Prefer deterministic local Kotlin/Room/SQL logic for:
- scoring
- exam rules
- evidence counting
- revision scheduling
- mastery calculations
- question selection
- analytics

Use Gemini/API only where it provides genuine educational value.

Do not use an LLM where deterministic code is safer, cheaper, faster, or more reliable.

Never let an LLM silently override deterministic exam rules.

## OFFLINE-FIRST
Core learning functionality should remain usable offline.

Network/API failures must not break core practice, scoring, revision, or learner history.

## UI/UX
Keep learner-facing language simple.

Prefer:
Why you missed it
What to fix
Why this question
Try this
Did you improve?
What should you do next?

Avoid unnecessary technical terminology.

The interface should make the next useful action obvious.

## TESTING
Never delete or weaken tests merely to obtain a green build.

If an existing test is obsolete, replace it with an equivalent or stronger meaningful test.

For every substantial change:

INSPECT
-> IMPLEMENT
-> TARGETED TEST
-> BUILD
-> REGRESSION
-> AUDIT

Report exact:
tests executed
passed
failed
skipped

Compilation success alone does not mean the feature is complete.

## ARCHITECTURE
Before creating a new engine, repository, scheduler, analytics pipeline, or learner model, search the existing codebase for equivalent functionality.

Prefer extending a correct existing component over creating duplicate systems.

Keep responsibilities clearly separated.

## PERFORMANCE
Avoid unnecessary database queries.

Do not perform heavy analytics during Compose recomposition.

Keep expensive work off the main thread.

Avoid unnecessary network calls.

Prefer efficient SQL queries and cached/derived analytics where appropriate.

## SECURITY
Never expose API keys, credentials, tokens, or personal data.

Never commit secrets.

Do not modify files outside the project unless explicitly required.

## AUTONOMOUS DEVELOPMENT LOOP
For large tasks:

1. Inspect existing implementation.
2. Identify the highest-value issue or capability.
3. Verify assumptions.
4. Plan the smallest robust change.
5. Implement.
6. Run targeted tests.
7. Run relevant regression tests.
8. Inspect integration points.
9. Fix failures.
10. Build.
11. Perform an adversarial audit.
12. Continue to the next safe roadmap item.

Do not stop simply because compilation succeeds.

Do not stop simply because unit tests pass if important product behavior remains unverified.

## FINAL PRINCIPLE
Build a genuine evidence-driven learning system, not a collection of impressive-looking features.

The central question for every major product decision is:

"What is the highest-value thing this learner should do next, and what evidence proves it?"
