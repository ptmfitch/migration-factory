---
name: Record bind
description: Use when Discovery Phase A has candidates and a human must accept/reject/defer — writes durable bind decisions into MANIFEST, not only chat.
---

# Record bind (operator skill)

Write all output in ASD-STE100 only. See skills/operator/asd-ste100/SKILL.md.

Capture **human bind** decisions so Phase B and downstream stages have a git SoT.

## Context hard gate

Read Field Guide (App Discovery mid-gate) + `OPERATOR-RUNBOOK.md`. Refuse without Field Guide.

## When to use

- `CANDIDATES.md` + `SME_BRIEF.md` ready; human reviewing accepts
- Need a structured bind record for MANIFEST / checklist PR comment
- Re-bind after scope change (document prior decisions)

## Non-goals

- Do not deepen behaviour cards here (`deepen-phase-b`)
- Do not approve Test gen matrices (`matrix-gate-reply`)
- Do not BIND Architecture packs (`architecture-pack-bind`)
- Agent must **not** self-flip candidates to accepted

## Recipe

1. Load `discovery/<SLICE_ID>/CANDIDATES.md` + `SME_BRIEF.md`.
2. For each candidate, record: `accept` | `reject` | `defer` (+ one-line reason).
3. Update / instruct update of `MANIFEST.yaml` statuses to match.
4. List `needs-SME` / blocked items explicitly — do not drop silently.
5. Emit sign-off line: who bound, when (operator timezone label OK), ticket link if any.
6. Hand off to `deepen-phase-b` for accepted-only deepen prompt.
7. After the bind record is written, invoke `jira-cards-mcp` for each affected `FEATURE_ID` (`bind-accept` / `bind-reject` / `bind-defer`). If `JIRA_PROJECT_KEY` is unset, warn and continue — do not hard-refuse; only `jira-cards-mcp` hard-refuses missing Jira config.

## Paste-ready bind record

```text
## Bind record — discovery/<SLICE_ID>/

| Candidate ID | Decision | Reason |
| --- | --- | --- |
| <id> | accept | <why> |
| <id> | reject | <why> |
| <id> | defer | <why> |

needs-SME / blocked:
- <id>: <question>

Bound by: <name>
Bound at: <YYYY-MM-DD HH:MM TZ>
Next: deepen Phase B for accepted only (skill: deepen-phase-b)
```

## Refuse

- Bind from vibes with no `CANDIDATES.md`
- Accepting `inferred` items into Test gen without SME note / waiver
