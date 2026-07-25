# Change Localization Protocol

Use this micro-practice when the team must pinpoint where to edit in a codebase
that is too large to load whole. The goal is to converge from a vague intent to
a precise set of files, line ranges, and call chains — with a bounded and
explicitly growing token budget at each step.

This protocol narrows scope. It does not decide whether to make a change; that
stays with the routing lead and the relevant workflow bundle.

## When To Activate

Activate when any of these appear:

- audit findings that need to map to exact code sites before fixing
- root-cause remediation **when the prompt also carries a localization signal** (locate / pinpoint / call chain / exact files / 定位 / 改动点 / 调用链); a plain root-cause loop without such a signal does not activate this protocol
- a bug whose call chain is not yet traced and a localization signal is present
- edits requested against an unfamiliar or multi-module area
- a fix that keeps recurring because prior attempts patched the wrong site

Do not activate for a one-line change whose location is already named, or for
read-only explanation that needs no edit.

## Goal

Land on a precise change set — files, line ranges, the call chain that justifies
each site, and the reason each site is in scope — without ever feeding the whole
codebase into a single context.

## Relationship To System Map

This protocol runs after, not instead of,
`references/system-map-protocol.md`. The system map answers "what are the
modules and how do they relate"; this protocol answers "given that map, exactly
which lines must change for this task". If no map exists and the area is
unfamiliar, build one first; if a map exists, start from it and converge.

## Token-Budget Convergence

Converge through five steps. Each step widens the budget only as much as the
previous step failed to resolve, so the model is never drowned in code it did
not ask for.

1. **Intent disambiguation** — feed only a compact project overview (target:
   around `2K` tokens) and resolve the technical reading of the request. Output:
   a one-paragraph technical interpretation and the candidate module family.
2. **Module localization** — read the directory tree plus the step-1
   interpretation (no source bodies yet). Output: `2` to `3` candidate file
   paths, with a one-line reason each.
3. **Keyword search (script, not LLM)** — this step does not use the LLM to
   search. Run a script (e.g. `rg` for symbol declarations and call sites) over
   the candidate paths and record the matches. Output: concrete file and line
   locations of the relevant symbols. The LLM consumes the script's landed
   output, never its own browsing of the tree.
4. **Call-chain tracing** — load a single relevant file's relevant fragments
   (target: around `10K` tokens) and trace the call chain through the symbols
   found in step 3. Output: a complete chain from entry to the change site.
5. **Verification** — load the target function's implementation (target: around
   `5K` tokens) and confirm the final change site plus the reason it is the
   right place to edit. Output: the finalized change set with justification.

The budgets are ceilings, not targets. If a step resolves with less, stop early
and advance; never pad a step to its ceiling.

## Rules

1. Step 3 must be a script. Symbol lookup is a data acquisition step, not a
   judgment step — keep it out of the LLM per the
   `references/anti-entropy-governance.md` data-channel constraint.
2. Never collapse two steps into one context. Each step's output gates the next
   step's input; merging them reintroduces the whole-codebase flooding this
   protocol exists to prevent.
3. If step 4 cannot complete a chain from the step-3 candidates, go back to
   step 2 and widen the candidate set — do not browse freely inside step 4.
4. Record the call chain, not just the leaf. A change site without its chain
   cannot be verified and tends to miss upstream callers.
5. If the change set still looks ambiguous after step 5, stop and surface the
   ambiguity rather than picking a site by plausibility.

## Worktree Behavior

When the task runs inside a worktree, localization steps 2 through 5 execute
against the **execution-root** (the worktree being edited) — the directory tree,
keyword search, call chain, and function implementation all live in that
working tree. The L1 overview fed into step 1, however, is read from
**state-root** (the main repository); do not re-derive the project overview
inside each worktree. See
`references/worktree-state-placement-protocol.md` for how to resolve state-root
from inside a worktree.

## Completion Evidence

When this protocol is active, completion must name:

- the finalized change set: files and line ranges
- the call chain that justifies each site
- which step produced each site (so the trace is replayable)
- any ambiguity that forced a return to an earlier step
- whether the result changed the selected workflow bundle's scope
