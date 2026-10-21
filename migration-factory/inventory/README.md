# Portfolio inventory

Per-app source of truth for what the factory knows about a legacy application.

`APP_MANIFEST.yaml` is the source of truth. `COVERAGE.md` is generated output; never hand-edit it.

## Layout

```text
inventory/<APP_ID>/
  APP_MANIFEST.yaml   # source of truth (agents write; humans residual-gate)
  COVERAGE.md         # generated human glance. Never hand-edit
```

## How to start an app

The [`factory-quick-start`](../skills/factory-quick-start/SKILL.md) skill performs the steps below in an application repository. It does not start Discovery.

1. Create `inventory/<APP_ID>/APP_MANIFEST.yaml` following `schemas/app-manifest.schema.md` (and `schemas/app-manifest.schema.json` for CI validation).
2. Generate `inventory/<APP_ID>/COVERAGE.md` from the manifest after each inventory update:
   ```bash
   python3 migration-factory/inventory/gen_coverage.py <APP_ID> --repo-root <REPO_ROOT>
   ```
   You may instead pass a manifest path directly:
   ```bash
   python3 migration-factory/inventory/gen_coverage.py inventory/<APP_ID>/APP_MANIFEST.yaml
   ```
3. Never hand-edit `COVERAGE.md`. Regenerate it from `APP_MANIFEST.yaml`.

The generator requires Python 3 and PyYAML. It writes the operator's Done / Partial / Remaining modern implementation view before discovery and characterization histograms. It never emits completion percentages.

Every Conversion or engine-rewrite change set that lands modern behaviour must update the manifest's `impl_in_modern` value (and use `status: converted` only for `full`) and regenerate COVERAGE in the same change set.

## Pack policy

This factory pack **ships no seed manifests**. Operators bring their own `APP_ID` inventory. Generic methodology (Pathfinder sequencing, `WAIVED_PATHFINDER` as a waiver code) lives in the docs and skills, not under `inventory/`.

## Experimental growth path

Optional overnight Cloud Agent: `../prompts/estate-discovery-loop-v0.1.md` can propose candidate surfaces into this inventory. Humans still bind. Completeness remains a residual gate.
