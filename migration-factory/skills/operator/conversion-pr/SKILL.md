---
name: Conversion PR
description: Use when composing a Conversion feature PR body — pack_id@version, edit_surface modern/** only, provisional vs golden, WAIVED_PATHFINDER / PARITY=UNVERIFIED, CONTRACT_RISK; no parity claims.
---

# Conversion PR (operator skill)

Write all output in ASD-STE100 only. See skills/operator/asd-ste100/SKILL.md.

Standardise **Conversion PR descriptions** so reviewers see pack law and limits.

## Context hard gate

Field Guide Conversion + BOUND pack + `prompts/conversion-agent-v0.1.md`. Refuse without Field Guide / pack cite.

## When to use

- Feature implementation about to open/update a PR
- Batch summary needs a human-readable PR template
- Reviewer asked “what does this PR claim?”

## Non-goals

- Do not claim `PARITY=GREEN` (Verification only)
- Do not change `*.approved.*` goldens (provisional modern tests ≠ goldens)
- Do not expand `edit_surface` in the PR narrative — that needs re-bind
- Do not invent COMPARE results in the PR body

## Paste-ready PR body

```text
## Summary
Convert Discovery feature(s) under BOUND Architecture PACK.

- SLICE_ID: <id>
- FEATURE_IDS: [<ids>]
- pack_id@version: <pack>@<version>
- Overlay: <path|none>

## Pack law
- Target patterns used: <mapping_rules cites>
- edit_surface: modern/** only (paths touched below)
- Paths touched: <list under modern/**>
- Forbidden / non_goals / legacy/** respected: yes

## Evidence / upstream
- Behaviour cards: discovery/<SLICE_ID>/features/…
- Characterization: REPLAY_GREEN [<ids>] | WAIVED_PATHFINDER (or WAIVED_<CODE>) <path>
- Conversion plan artefact: <path|n/a>
- Plan gate: approved / skipped (reason)

## Modern implementation inventory
- APP_MANIFEST: inventory/<APP_ID>/APP_MANIFEST.yaml
- Per-behaviour classification: <id>: none | partial | full
- Status rule: `converted` only for `full`
- Partial gaps in notes: <id>: <plain-English remaining gaps> | none
- COVERAGE regenerated with migration-factory/inventory/gen_coverage.py: yes
- Operator progress: Done <N> / Partial <N> / Remaining <N>

## Tests
- Pack quality_gates commands run: <list + result>
- Legacy REPLAY safety: OK | SKIPPED (not modern COMPARE)
- Provisional modern / unit tests added: <list>
- Goldens (`*.approved.*`): **untouched** (read-only; provisional ≠ golden)
- **PARITY=UNVERIFIED** — Verification not run in this PR

## CONTRACT_RISK
- Open CONTRACT_RISK items: <ids / one-liners | none>
- (Optional) HTTP status asymmetry notes e.g. legacy 502 vs modern mapping: <note|n/a>
- Leave open for Verification; do not silent-fix goldens

## Residual risks
- known_risks addressed: <…>
- BLOCKED / DEPENDENCY_BLOCKED: <…>
- Follow-ups: <…>

## Checklist
- [ ] Diff inside edit_surface (modern/**) only
- [ ] No golden rewrites; provisional tests clearly labelled
- [ ] pack_id@version cited
- [ ] WAIVED_* or REPLAY_GREEN cited
- [ ] APP_MANIFEST updated for every in-batch behaviour (`impl_in_modern`)
- [ ] Only `full` behaviours use `status: converted`; partial gaps are in `notes`
- [ ] COVERAGE.md regenerated in this change set
- [ ] Done / Partial / Remaining histogram included
- [ ] PARITY=UNVERIFIED stated (no parity claim)
- [ ] CONTRACT_RISK section filled (or explicit none)
- [ ] No net-new product features
- [ ] Handoff ready for Verification agent (skill: verify-parity)
```

## Jira

After the Conversion PR is opened or updated, invoke `jira-cards-mcp` for each affected `FEATURE_ID` (Conversion PR / implementation → Conversion column). If `JIRA_PROJECT_KEY` is unset, warn and continue — do not hard-refuse; only `jira-cards-mcp` hard-refuses missing Jira config.

## Refuse

- PR template that claims parity or modern COMPARE green
- Omitting `pack_id@version`
- Diffs outside `edit_surface` / into `legacy/**` without allow-list
- Treating provisional modern tests as frozen goldens
- Claiming a feature converted without the APP_MANIFEST implementation bump and regenerated COVERAGE
- Treating `legacy_green` or replaying goldens as proof that modern implementation is done
