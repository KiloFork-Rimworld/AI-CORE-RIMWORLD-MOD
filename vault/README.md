# KiloFork-Rimworld Vault

Status: **active**
Bootstrap date: 2026-09-23
Organization: `KiloFork-Rimworld`
Anchor repository: `KiloFork-Rimworld/AI-CORE-RIMWORLD-MOD`
Role: RimWorld AI-core mod/adaptation authority
Authority effect: **none**

## Purpose

This is the durable organization-local memory surface for KiloFork-Rimworld. It preserves decisions, measurements, handoffs, retrospectives, maps, and context that help a future human or agent resume work without reconstructing the organization from chat history.

The vault is a **projection of evidence and decisions**, not a substitute for source-of-truth product contracts, repository state, CI receipts, or GSV/Kilo_Core governance.

## Organization map

- `KiloFork-Rimworld/AI-CORE-RIMWORLD-MOD`

When repositories are added, moved, archived, or split, update this map with the measured repository identity rather than guessing from names.

## What belongs here

- dated decisions and their rationale;
- handoffs with exact branch/commit/PR identifiers;
- measurements and experiment receipts;
- architecture maps and organizational context;
- retrospectives, lessons learned, and known sharp edges;
- links to canonical contracts rather than copied competing versions.

Create subdirectories only when real material exists, using the conventional names `decisions/`, `handoffs/`, `measurements/`, `projects/`, `services/`, and `archive/`.

## Rules

1. **Observe before interpreting.** Mark inference as inference.
2. **Current repository contracts outrank vault prose.** The vault explains truth; it does not mint it.
3. **Name exact evidence.** Prefer repository, branch, commit, PR, receipt, or dated measurement.
4. **Do not manufacture green.** Missing or unmeasured evidence stays UNKNOWN / DID_NOT_MEASURE.
5. **Preserve history.** Supersede dated notes instead of silently rewriting what an earlier lane observed.
6. **A stranded write lane becomes a read/test/audit lane.** Publish a handoff here or through the cross-org beacon when possible.
7. **No secret store.** This anchor repository is public. The vault is **public-safe only**: never place secrets, credentials, private operational details, personal data, or unpublished sensitive material here.

## Cross-organization coordination

Cross-org findings belong in the personal beacon `KiloMusician/OmniTagProtocol` when the owning organization cannot be reached. The beacon is a rendezvous, not an authority replacement. Bring durable organization-specific knowledge home to this vault once the owning lane is available.

## Initial log

### 2026-09-23 — vault bootstrap

Created the organization vault invariant after the GitHub organization restructuring exposed that organization boundaries are also practical agent/session boundaries. This file establishes a stable memory surface without creating a second control plane.

[Msg⛛{ORG-VAULT:KiloFork-Rimworld:BOOTSTRAP-20260923}]
