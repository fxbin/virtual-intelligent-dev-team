# Feedback Loop First Protocol

Use this micro-practice for bugs, regressions, performance issues, repeated
failures, and root-cause work.

## Goal

Build a fast enough pass/fail signal before diagnosis or patching. The team
should debug against evidence, not against plausible stories.

## Required Loop Order

Try to establish the feedback loop in this order:

1. failing test at the seam that reaches the bug
2. HTTP or CLI script with fixture input and expected output
3. headless browser script with DOM, console, or network assertions
4. captured trace or real payload replay
5. throwaway harness around the smallest executable code path
6. stress, property, fuzz, bisection, or differential loop for flaky behavior
7. human-in-the-loop script only when no agent-runnable path exists

## Loop Quality

Before moving to hypotheses, check:

- the loop reproduces the user-described symptom, not a nearby failure
- the signal is deterministic enough to guide work
- the assertion targets the failure mode, not just "did not crash"
- the loop is reasonably fast for repeated runs
- original evidence is preserved so the final fix can be rechecked

## Hypothesis Discipline

After the loop exists:

1. list 3 to 5 ranked, falsifiable hypotheses when the cause is not obvious
2. state the prediction for each hypothesis
3. test one variable at a time
4. tag temporary instrumentation with a unique cleanup prefix
5. convert the minimized repro into a regression test when a correct seam exists

## Stop Conditions

Stop and report a blocker when:

- no repro, trace, log, fixture, or executable signal is available
- the next step would be speculative patching
- the only available seam would create a misleading test
- production instrumentation or destructive access is needed

## Completion Evidence

When active, completion must name:

- feedback loop type
- repro command or evidence source
- observed failure before the fix
- verification after the fix
- regression test or reason a correct seam does not exist
- temporary instrumentation cleanup status
