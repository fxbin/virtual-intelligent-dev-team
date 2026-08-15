# Release Train Protocol

Use this protocol when one coherent release is too large or risky for a single PR, but several bounded feature PRs must integrate before the final default-branch release.

This protocol is optional. Do not introduce a release branch for a small, independently shippable slice.

## Goal

Preserve small reviewable PRs while keeping one explicit integration surface and one final production gate.

Target shape:

```text
main / default branch
        ↑ final release PR
release/<release-name>
        ↑
feature/A   feature/B   feature/C
```

## When to activate

Use a release train when at least one is true:

- multiple bounded PRs must ship atomically or under one release gate;
- localization/migration/content work spans many independent surfaces but needs a single launch;
- parallel workers need isolation while integration semantics must be checked before default-branch merge;
- a production backend rollout must happen after feature integration but before final release;
- rollback or release notes need one identifiable release candidate.

Do not use it merely because there are multiple Issues.

## 1. Release contract

Before child work begins, record:

```yaml
release_branch: release/<name>
default_branch: <main/master/etc>
parent_issue: <release/epic issue>
child_issues:
  - <issue>
final_release_pr_owner: <lead>
required_release_gates:
  - <CI/QA/etc>
required_production_gates:
  - <migration/deploy/smoke if applicable>
release_invariants:
  - <stable semantic behavior>
  - <route/API/schema contracts>
rollback_anchor: <known-good branch/tag/deployment>
```

The release branch is an integration candidate, not automatically production-ready.

## 2. Child PR rule

Each child PR should:

- target the release branch;
- stay bounded to one semantic slice;
- preserve release-level invariants;
- carry its own targeted verification;
- state what it does **not** verify at release level;
- avoid claiming the parent release complete.

### Issue-closing semantics

Do not assume `Closes #123` will close an Issue when a PR merges into a non-default branch. Hosting platforms commonly apply automatic closure only when the closing commit reaches the default branch.

Therefore choose deliberately:

- child Issue can stay open until final release; or
- child Issue can be manually closed after verified integration; or
- final release reconciliation closes completed children.

The workflow must record which policy is being used. Never infer Issue state from PR merge state alone.

## 3. Integration branch rule

The release branch owns cross-slice verification:

- semantic parity across child changes;
- shared schema/API/route compatibility;
- integrated build/test/QA;
- release-specific regressions;
- external production readiness when required.

A child PR being green does not prove the release branch is green.

## 4. Final release PR

The final PR from release branch to default branch is the **release owner**.

Its checklist should distinguish:

```text
[x] integrated code gates
[x] release-specific QA
[ ] required production control-plane rollout
[ ] required production data-plane smoke
```

Keep the PR Draft/hold while any required external gate is unverified.

Only the final release PR should carry automatic closure language for the parent release Issue when the project wants default-branch merge to close it.

## 5. External production gate

If the release changes a remote production system, combine this protocol with `production-bound-delivery-protocol.md`.

Typical order:

```text
release branch integrated
→ code/release QA green
→ production control-plane rollout
→ production persistence/behavior verification
→ mark final PR Ready
→ merge to default
→ deployment
→ post-merge production smoke
```

Some systems deploy only after default-branch merge. In that case, split the evidence honestly:

```text
pre-merge required control-plane gates
post-merge required production smoke
```

Do not label the release complete until the post-merge required smoke passes.

## 6. Hotfix after release

A production bug found after a successfully closed release should normally use a bounded hotfix:

```text
Issue
→ fix/<issue-or-bug>
→ targeted verification
→ relevant release/regression QA
→ PR to default branch
→ production verification
```

Do not reopen the entire release train unless the release itself was never actually complete or the bug invalidates the release-level contract broadly.

Preserve the original release closure and link the hotfix back to it.

## 7. Release-train evidence

Before closing the train, preserve:

- final release PR/merge commit;
- child PR list;
- child Issue reconciliation state;
- release QA results;
- required remote rollout evidence;
- production smoke evidence;
- rollback anchor;
- residual known issues/hotfix links;
- next-phase truth-sync result.

## 8. Parallel development rule

Release train does not automatically mean worktree/subagent parallelism.

Parallelize only when child slices are actually independent enough to avoid shared-state contention. If they share a hot file/schema/contract, sequence or establish the contract first.

The release branch must remain the single integration truth source regardless of worker count.

## Non-goals

- Replacing trunk-based development for small changes.
- Hiding integration debt behind a long-lived release branch.
- Letting feature PRs bypass their own verification because final QA exists.
- Treating release branch merge as proof of production deployment.
