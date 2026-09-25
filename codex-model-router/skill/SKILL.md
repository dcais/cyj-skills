---
name: codex-model-router
description: Select native Codex subagents by task complexity using configurable fast, standard, and deep model tiers, with evidence-based escalation. Use for coding, investigation, verification, or explicit model-routing requests; simple conversation stays with the parent.
---

# Codex Model Router

Route bounded work through native Codex subagents. No OMX, tmux, gateway, or separate task creation is required. This selects a delegated task's model; the parent model and its usage remain unchanged. Routing is instruction-guided, not a deterministic host-level model switch.

## Select a tier

Read [models.json](models.json) beside this file before selecting a model. It is the installed mapping, not a promise of account access. Do not substitute remembered model IDs. Respect explicit user model choices and workflow constraints.

| Tier | Native role | Suitable work |
| --- | --- | --- |
| fast | `codex-router-fast` | Narrow lookups, extraction, and low-risk mechanical edits with clear acceptance criteria. |
| standard | `codex-router-standard` | Default for bounded implementation, reproducible debugging, and focused tests or reviews. |
| deep | `codex-router-deep` | Architectural tradeoffs, difficult diagnosis, concurrency, or cross-module correctness reasoning. |

Simple conversation, translation, status replies, and work with no useful delegation stay with the parent. File count alone does not establish complexity. Missing requirements or authority require clarification, not a larger model. Apply the existing approval requirements before editing.

## Dispatch

1. Only the parent routes. Delegated agents complete their slice without loading this skill again, spawning descendants, or invoking another orchestrator.
2. Use a concrete independent slice only when the parent can do useful work alongside it, such as acceptance planning or integration. Do not duplicate the child's work or delegate trivial tasks just to claim model savings.
3. State the chosen tier and why. Give the child a self-contained task with an absolute workspace path, file ownership, constraints, evidence, and acceptance checks. Editing agents share the workspace and must preserve others' edits.
4. Inspect the live spawn tool schema. Select the corresponding installed role only if it is exposed. Its configured model and effort must match models.json. If they disagree, report a stale installation and do not override a fixed role. Prefer a fresh context with complete handoff; full-history forks may force parent-model inheritance. Follow the actual tool's fork and override semantics.
5. If custom roles are not exposed, a generic role with explicit model/effort is an option only when the live interface and applicable policy permit it and the role is not model-fixed. Use the selected mapping and these execution constraints, and disclose the fallback. Never invent a role or bypass a hook rejection. If no permitted route exists, report routing unavailable and continue independent safe parent work.
6. Use runtime/tool metadata to confirm the executing model. Distinguish configured model, requested model, and confirmed model. Model self-identification or a cached catalog is not proof of execution or account access. A fresh session may discover installed roles; it does not fix unsupported models or policy restrictions.

## Verify and escalate

Require the result, changed files or cited locations, actual checks and outcomes, unresolved assumptions, and one status: `complete`, `needs_escalation`, or `blocked`.

The parent checks evidence before accepting completion. Escalate a reasoning or implementation limitation along fast -> standard -> deep, at most two upward transitions per slice. Preserve completed work and forward failed checks and remaining questions. Stop the previous writer before another agent takes the same files. The deep tier reports unresolved blockers rather than restarting a cycle.

Credentials, permissions, unavailable models/tools, missing data, and unclear requirements are operational blockers. Do not route around them with another model or disable guards. Do not repeat successful work or automatically demand deep review for every small edit.

## Updating the mapping

The package installer generates the three roles from models.json. To change models, pass a revised mapping to the installer with `--config`; editing only one installed file leaves the skill and roles inconsistent. Model names belong in the mapping, not this skill's name, description, or routing rules. See the package installation instructions for commands and update behavior.
