# Operator runbook (App modernisation) — routing table

One-page map for humans running the factory. **Not** a Discovery tutorial — stage how-tos live in the [Field Guide](./FIELD-GUIDE.md).

**Context hard gate:** before any agent or operator skill runs, attach `docs/FIELD-GUIDE.md` + that stage’s schemas/prompts. Agents refuse without them.

**Writing rule:** All agent output and all skill output is ASD-STE100 Simplified Technical English only. See [`skills/operator/asd-ste100/SKILL.md`](../skills/operator/asd-ste100/SKILL.md). Apply this rule to generated factory and stakeholder text (Jira cards, behaviour cards, SME briefs, comments, paste blocks).

**New application repository:** copy [`skills/factory-quick-start/`](../skills/factory-quick-start/SKILL.md) to the application repository at `.cursor/skills/factory-quick-start/` and run that skill. It vendors this pack and writes an incomplete inventory. It does not start Discovery.

**EXPERIMENTAL estate discovery:** optional overnight inventory radar (`prompts/estate-discovery-loop-v0.1.md`). Phase A candidates only; never auto-bind; never claim completeness. Separate from the overnight Conversion conductor.

**Portfolio inventory:** SoT is `inventory/<APP_ID>/APP_MANIFEST.yaml` (schema: `schemas/app-manifest.schema.json`). Generate `inventory/<APP_ID>/COVERAGE.md` with `python3 migration-factory/inventory/gen_coverage.py <APP_ID> --repo-root <REPO_ROOT>`. Operators open COVERAGE first for **Done / Partial / Remaining** modern implementation progress; seed counts and `legacy_green` are not migration progress. Never hand-edit `COVERAGE.md`.

**Conversion inventory gate:** every Conversion or engine-rewrite change set that lands modern behaviour must update `APP_MANIFEST.yaml` (`impl_in_modern`, with `status: converted` only for `full`) and regenerate COVERAGE in the same change set. Shipping modern code without that bump is a process defect.

---

## Where artefacts land

| Stage / artefact | Path |
| --- | --- |
| Slice inputs (seeds) | Operator brief / ticket; echoed in Discovery prompt |
| Discovery Phase A | `discovery/<SLICE_ID>/CANDIDATES.md`, `MANIFEST.yaml` (stub), `SME_BRIEF.md` |
| Discovery Phase B | `discovery/<SLICE_ID>/features/<FEATURE_ID>.md` (+ bound MANIFEST) |
| Test gen | `testgen/<SLICE_ID>/` — scenarios, stubs, `TRACEABILITY.yaml`, `SME_BRIEF.md` |
| Test exec | `tests/characterization/<SLICE_ID>/…`, goldens `*.approved.*`, `results.json`, `REPORT.md` |
| Waiver (no legacy run) | `testexec/<SLICE_ID>/WAIVED_*.md` + ADR under `architecture/` or `discovery/` (see skill) |
| Architecture | `architecture/<MIGRATION_ID>/PACK.yaml`, `ADR/`, `slice-overlays/<SLICE_ID>.yaml` |
| Conversion | Feature PRs citing `pack_id@version`; APP_MANIFEST progress bump; generated COVERAGE; Done / Partial / Remaining batch summary |
| Verification | `verification/<SLICE_ID>/<RUN_ID>/` — `PARITY.yaml`, narrative, evidence |
| Portfolio inventory | `inventory/<APP_ID>/APP_MANIFEST.yaml` (SoT); generated `inventory/<APP_ID>/COVERAGE.md` (**read-only**) |

---

## Routing table

| Gate / stuck moment | Skill | Human says (one line) | Next artefact |
| --- | --- | --- | --- |
| New application repository; factory pack not in the workspace | `factory-quick-start` | “Bootstrap the factory for `APP_ID`.” | Vendored `migration-factory/`, incomplete APP_MANIFEST, generated COVERAGE. No Discovery. |
| Starting a pathfinder; fuzzy “whole module” | `slice-scoping` | “Scope slice `SLICE_ID` with these seeds / out-of-scope.” | Bound slice inputs ready for Discovery Phase A |
| Discovery Phase A done; candidates waiting | `record-bind` | “Bind: accept / reject / defer per candidate.” | Updated `MANIFEST.yaml` + bind record; unlock deepen |
| Bind done; need Phase B deepen prompt | `deepen-phase-b` | “Deepen accepted only for `SLICE_ID`.” | Paste-ready Phase B prompt → behaviour cards PR |
| Test gen Phase A matrix waiting | `matrix-gate-reply` | “Approve / drop / defer these case rows.” | Paste-ready matrix reply → Phase B specs/stubs |
| Any mid-gate (golden approve, Conversion plan, SME sign-off) | `compose-gate-reply` | “Approve / waive / block with reason.” | Durable gate reply (chat or PR comment) |
| Unsure which stage prompt to paste next | `compose-stage-prompt` | “Compose next-stage run for `STAGE` + `SLICE_ID`.” | Paste-ready agent prompt + required attachments |
| No legacy runtime/license; cannot RECORD | `waive-characterization` | “Waive Test Exec under `WAIVED_PATHFINDER`.” | `WAIVED_*` + ADR; Conversion may proceed; **no PARITY claim** |
| Need to-be target before Conversion | `architecture-pack-author` | “Author DRAFT PACK for `MIGRATION_ID`.” | `PACK.yaml` `status: DRAFT` (+ ADR) |
| DRAFT pack ready; architect will BIND | `architecture-pack-bind` | “BIND checklist for pack@version (human only).” | Git commit: `status: BOUND` + `bound_by` / `bound_at` |
| Conversion feature about to PR | `conversion-pr` | “Compose PR body for feature(s).” | PR description: pack@version, edit surface, risks, inventory bump + COVERAGE regeneration |
| Modern built; need parity proof | `verify-parity` | “Run Verification COMPARE for `SLICE_ID`.” | `PARITY.yaml` + evidence pack (not chat greening) |
| **EXPERIMENTAL:** overnight estate candidate hunt | `prompts/estate-discovery-loop-v0.1.md` | "Run estate discovery under allowlist; Phase A only." | APP_MANIFEST + COVERAGE delta; MORNING_BRIEF; nothing bound |
| Unsure what is done or left in modern | _(read)_ `COVERAGE.md` | “Show modern progress for `APP_ID`.” | Done / Partial / Remaining first; residual completeness is still a **human** gate on APP_MANIFEST |
| Want the station output or human bind on the feature ticket | `jira-cards-mcp` | “Post this output / bind to the feature ticket.” | Jira comment + column move; git remains SoT (no MCP server) |

---

## Refuse / don’t-proceed rows

| Situation | Do **not** | Instead |
| --- | --- | --- |
| Bootstrap asked inside the factory pack repository | Create `inventory/<APP_ID>/` here | Copy `factory-quick-start` into the application repository and run it there |
| No Field Guide / schemas in context | Launch agent anyway | Attach Field Guide + stage schemas; hard-refuse is correct |
| Discovery candidates unbound | Deepen Phase B / invent accepts | `record-bind` first |
| Cards `inferred` / `needs-SME` without waiver | Test gen Phase B or RECORD | SME resolve, waive explicitly, or drop from batch |
| No `REPLAY_GREEN` and no `WAIVED_*` | BIND Architecture pack; start Conversion | Run Test Exec **or** `waive-characterization` |
| Chat “looks good” on architecture | Treat as BOUND | `architecture-pack-bind` → git `status: BOUND` (+ CODEOWNERS) |
| Claim overnight found all slices / auto-bind from estate loop | Treat COVERAGE growth as migration done | Morning bind only; residual stays human |
| Hand-edit `COVERAGE.md` | “Fix” coverage in markdown | Update `APP_MANIFEST.yaml` (or re-run inventory writers) and **regenerate** COVERAGE |
| Modern code lands without an inventory bump | Claim the behaviour converted | Set `impl_in_modern`; use `status: converted` only for `full`; record partial gaps in `notes`; regenerate COVERAGE in the same change set |
| `legacy_green` or tests replay goldens | Treat the behaviour as migrated | Characterization is not implementation; inspect `impl_in_modern` and COVERAGE Done / Partial / Remaining |
| Waiver path used | Claim `PARITY=GREEN` or skip Verification forever | Convert under waiver; Verification still required later for parity claims |
| Conversion without BOUND pack | “Just implement Spring-style…” | `architecture-pack-author` → human BIND |
| RECORD on modern / rewrite goldens from modern | “Make tests pass on new stack” | Verification `MODE=COMPARE`, goldens read-only |
| Agent self-binds MANIFEST / PACK | Accept agent-flipped `BOUND` | Human bind skills only |

---

## Stage spine (reminder)

```text
Discovery → Test Gen → Test Exec ─┬→ Architecture → Conversion → Verification
                                  │
                                  └→ WAIVED_PATHFINDER (skill: waive-characterization)
                                       → Architecture → Conversion
                                       → Verification still owns any future PARITY claim
```

Exit criteria and stage tutorials: [FIELD-GUIDE.md](./FIELD-GUIDE.md).  
Operator skill pack: [`../skills/operator/README.md`](../skills/operator/README.md).
