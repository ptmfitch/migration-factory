# Migration factory

This repo holds your **migration factory** playbooks: the Field Guide, stage agent prompts, schemas, operator skills, and portfolio inventory patterns.

It is the control plane for how you run application modernisation with Cursor. Your legacy application code lives in its own repos. This repo is the operating system for the agents and for the humans who run them.

## What is in here

```text
migration-factory/
  docs/          Field Guide, operator runbook, new-user guide
  prompts/       Stage agent prompts (Discovery -> Verification)
  schemas/       MANIFEST / TRACEABILITY / PACK / APP_MANIFEST schemas
  skills/        Architecture PACK skill, operator skill pack, factory quick-start
  inventory/     How to stand up APP_MANIFEST + generated COVERAGE.md
```

To bootstrap an application repository, copy `migration-factory/skills/factory-quick-start/` to that repository's `.cursor/skills/factory-quick-start/` and ask the agent to bootstrap the factory. The skill vendors this pack and stops before Discovery.

Start here if you are new:

1. `migration-factory/docs/MIGRATION-FOR-NEW-USERS.md`
2. `migration-factory/docs/OPERATOR-RUNBOOK.md` (gate -> skill routing)
3. `migration-factory/docs/FIELD-GUIDE.md` (full operating detail)

## How to think about it

You are not asking one chatbot to rewrite a legacy estate.

You run a staged factory:

1. **Discovery** - what the old system actually does (slice by slice)
2. **Test generation** - characterization specs and stubs
3. **Test execution** - freeze goldens on legacy (or an explicit waiver)
4. **Architecture** - BOUND PACK the Conversion agent must obey
5. **Conversion** - implement documented behaviours under that pack
6. **Verification** - COMPARE modern against the same goldens; only stage that may claim parity

Humans own the stamps (bind, matrix, goldens, PACK BIND, waiver, parity, merge). Agents own the clipboard and the heavy lifting.

## What this repo is not

- Not your legacy codebase
- Not a claim that a pathfinder run equals production parity
- Not a place to hand-edit generated `COVERAGE.md` (regenerate from `APP_MANIFEST.yaml`)

## Experimental

See `migration-factory/docs/EXPERIMENTAL.md`.

- **Estate discovery loop** (`prompts/estate-discovery-loop-v0.1.md`) - overnight inventory radar. Phase A candidates only. Never auto-bind. Never claims all slices found.
- **Overnight conductor** (`prompts/overnight-conductor-v0.1.md`) - ambitious single-slice conveyor under a provisional charter. Separate from estate discovery.
