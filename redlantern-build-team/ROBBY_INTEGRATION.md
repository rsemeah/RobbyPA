# RobbyPA — RedLantern Build Team Integration
*How RobbyPA fits into the 9-layer Build Team OS.*

---

## Robby's Place

```
QBos = doctrine (the law)
RobbyPA = conductor (enforces the law)
SwarmClaw agents = workers (do the work)
```

Robby does not build. Robby conducts.
Robby enforces phases, generates receipts, detects blockers, and maintains audit trails.

## Lifecycle Robby Enforces

```
INTAKE → SCOPE_LOCK → PLAN → EXECUTE → PROVE → HANDOFF → SHIP → OBSERVE → IMPROVE
```

## Robby's Adapters (implement or reference)

```python
# robby/adapters/swarmclaw_adapter.py
# Dispatch tasks to SwarmClaw agents, receive receipts

# robby/adapters/github_adapter.py  
# Check PR status, CI status, open PRs, branch state

# robby/adapters/vercel_adapter.py
# Check deployment status, preview URLs

# robby/adapters/supabase_adapter.py
# Verify schema, check table state, confirm RLS
```

## Phase Preconditions Robby Checks

| Phase | Preconditions |
|-------|--------------|
| SCOPE_LOCK | Problem statement exists, repo identified |
| PLAN | Scope lock receipt approved by Rory |
| EXECUTE | Plan receipt exists, data contracts written |
| PROVE | Execution receipt exists, CI has run |
| HANDOFF | REVIEW: PASS, QA: PASS, Security: CLEAN |
| SHIP | Proof receipt complete, Rory approved |
| OBSERVE | Ship receipt written, production confirmed |
| IMPROVE | Observe receipt written |

## Blocker Types Robby Detects

```
SCOPE_UNCLEAR      — work cannot start without clearer boundaries
MISSING_CONTRACT   — data or AI contract missing for this feature
CI_FAILING         — typecheck/lint/build failing
REVIEW_REJECT      — REVIEW agent returned REJECT
QA_FAIL            — QA agent returned FAIL
SECRET_DETECTED    — TruffleHog or Semgrep found a credential
RLS_MISSING        — new user table has no RLS policy
RORY_APPROVAL      — phase requires Rory to approve before continuing
PREVIEW_UNTESTED   — ship requires a preview that hasn't been confirmed
ROLLBACK_MISSING   — risky deploy has no rollback plan
```

## Receipt Format

Every phase exit produces a receipt in `/receipts/[SOLUTION]/[PHASE]_[DATE].md`.
Receipt templates are in `QBos---Master-Founder-Repo/redlantern-build-team/receipts/`.

## Post-Ship Phases (Extend Robby)

The current RobbyPA lifecycle ends at SHIP.
These are the RedLantern extensions — do not break existing code, add these as new phases:

```python
# Add to lifecycle after SHIP:
# Phase 8: OBSERVE — watch PostHog, Sentry, AI runs for 24h
# Phase 9: IMPROVE — feed lessons back to QBos templates
```

## Robby ↔ SwarmClaw Protocol

Robby dispatches tasks to SwarmClaw agents via the SwarmClaw API:
- `POST /api/missions` — start a mission
- `GET /api/missions/:id` — check status
- Agent receipts are parsed from mission output

Robby reads REVIEW agent output as: PASS / FLAG / REJECT
Robby reads QA agent output as: PASS / FAIL
Any other verdict is treated as BLOCKED until resolved.
