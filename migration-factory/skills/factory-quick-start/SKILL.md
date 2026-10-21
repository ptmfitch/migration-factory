---
name: factory-quick-start
description: >-
  Bootstraps the migration factory in an application repository. Vendors the
  factory pack, writes an incomplete APP_MANIFEST, generates COVERAGE.md, and
  adds the Cursor factory rule. Use when the user asks to bootstrap, stand up,
  quick-start, or drop in the migration factory in a Cursor project. Do not
  use for Discovery, Conversion, Verification, or other factory stages.
---

# Factory quick start

Write the operator summary in ASD-STE100 only. See `migration-factory/skills/operator/asd-ste100/SKILL.md` after the pack is on disk. Use short sentences. Do not use contractions.

This skill stands the factory up in an **application repository**. It is the skill you copy into that repository. It does not migrate a slice.

## Drop-in

From a factory pack checkout:

```bash
mkdir -p .cursor/skills
cp -R <factory-checkout>/migration-factory/skills/factory-quick-start .cursor/skills/factory-quick-start
```

`<factory-checkout>` is the git root that contains `migration-factory/docs/FIELD-GUIDE.md`. Run the copy in the application repository. Then ask Cursor to bootstrap the factory and give an `APP_ID`.

The tracked copy in the factory pack is the source. The copy under `.cursor/skills/factory-quick-start/` is what Cursor loads. After you update the pack, copy the skill directory again. Do not edit only one copy.

## Context

This skill may run before the Field Guide is in the workspace. That is the exception. Do not invent pack files, schemas, or prompts. The script vendors them or stops.

After a successful run, later chats use `migration-factory/docs/FIELD-GUIDE.md` and `migration-factory/docs/OPERATOR-RUNBOOK.md`. Do not start those stages here.

## When to use

- An application repository has no `migration-factory/docs/FIELD-GUIDE.md`
- The operator asked to bootstrap, stand up, or quick-start the factory

## Refuse

- Do not run the script in the factory pack repository. That repository's root README starts with `# Migration factory`.
- Do not start Discovery, test generation, test execution, architecture, Conversion, or Verification.
- Do not scan the estate. Do not fill `surfaces` or `behaviours`. Leave `scanned_seeds` empty.
- Do not set `completeness` to `complete_bound`.
- Do not hand-write `COVERAGE.md`.
- Do not overwrite an existing `APP_MANIFEST.yaml`.
- Do not bind a manifest or a PACK.
- Do not run the estate-discovery loop or the overnight conductor.

## Recipe

1. Confirm the workspace root is the application repository (the legacy code), not the factory pack repository. If it is the factory pack repository, tell the operator to copy this skill into the application repository and stop.
2. If the operator did not give an `APP_ID`, propose the repository directory name in kebab-case and wait. Continue only with a confirmed id. Pattern: `account-opening`.
3. Pass `--hint` only for residuals the operator stated. If they stated none, omit `--hint`. The script then records that the estate is not scanned.
4. Tell the operator which repository you will change. Then run the script. Do not ask for a second confirmation after they asked to bootstrap and named an `APP_ID`.

```bash
python3 "<skill-dir>/scripts/bootstrap.py" \
  --app-id "<APP_ID>" \
  --repo-root "<application-repository>"
```

`<skill-dir>` is the directory that contains this `SKILL.md`.

Add `--factory-src` when a local factory checkout is available. Point it at the git root or at the inner `migration-factory/` directory. The script copies that pack and does not clone.

Omit `--factory-src` when you want the script to clone `https://github.com/ptmfitch/migration-factory` (branch `main`) and copy the inner pack to `migration-factory/`. If the clone fails for lack of network, rerun with network access. Do not type the pack in by hand.

5. If the script exits non-zero, relay the error and stop. Do not build a substitute tree.
6. If the script exits zero, relay the summary below. Stop. The next human step is slice scoping.

## What the script writes

| Path | Role |
| --- | --- |
| `migration-factory/` | Factory pack (docs, prompts, schemas, skills, `inventory/gen_coverage.py`). A new copy includes `VENDOR.txt` (source and commit). |
| `inventory/<APP_ID>/APP_MANIFEST.yaml` | Portfolio source of truth. Incomplete. No behaviours. |
| `inventory/<APP_ID>/COVERAGE.md` | Generated. Never hand-edit. |
| `.cursor/rules/migration-factory.mdc` | Agent-requested hard gate for later factory work |
| `.cursor/skills/factory-quick-start/` | Cursor copy of this skill, if that path was missing |
| `discovery/`, `testgen/`, `testexec/`, `architecture/`, `verification/`, `tests/characterization/` | Empty artefact dirs |

A second run does not overwrite the pack, the manifest, the coverage file, or the rule.

PyYAML is required for `COVERAGE.md`. If it is missing, install `pyyaml` and run the script again. The manifest stays. Do not hand-edit coverage.

## Summary to the operator

Use these sentences. Fill the paths from the script output. Do not add a parity claim.

```text
Factory bootstrap is complete for <APP_ID>.
The factory pack is at migration-factory/.
The inventory source of truth is inventory/<APP_ID>/APP_MANIFEST.yaml.
COVERAGE.md is generated. Do not edit COVERAGE.md by hand.
The inventory is incomplete. Discovery has not started.
No behaviours are known.
Next step: scope one slice. Use the slice-scoping skill.
Do not start Discovery in this chat.
```

If a line says `present`, say that the file was already there and was left unchanged.

If `PACK_SKILL` is `injected`, say the published pack had no quick-start skill. The drop-in copy was added under `migration-factory/skills/factory-quick-start/`.

If `WARNING` says this repository ignores `.cursor/`, say that the rule works on this machine and is not committed until `.cursor/` is tracked.

## Next skill

`migration-factory/skills/operator/slice-scoping/SKILL.md`

Attach `migration-factory/docs/FIELD-GUIDE.md` when you run that skill. Not in this chat.
