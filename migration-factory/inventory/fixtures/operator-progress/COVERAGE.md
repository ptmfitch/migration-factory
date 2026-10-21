# Coverage — operator-progress-fixture

> **Generated from APP_MANIFEST.yaml. Never hand-edit.** Characterization flags (`legacy_green`) ≠ done in modern; use Operator progress for modern implementation.

## Operator progress (modern implementation)

| State | Count | Meaning |
| --- | ---: | --- |
| none | 1 | Not started in modern |
| partial | 1 | Some modern execution; gaps in notes |
| full (converted) | 1 | Done in modern; parity may still be UNVERIFIED |
| deferred / rejected | 1 | Explicitly out |

### Done in modern (impl_in_modern=full)

- example-done — Return an existing item

### Partial in modern

- example-partial — Persists in memory, but durable storage and duplicate handling remain.

### Remaining (impl_in_modern none/absent, not deferred/rejected)

- example-remaining — example — legacy_green yes

## Inventory context

### Seeds

| State | Count |
| --- | ---: |
| scanned | 1 |
| unscanned hints | 1 |

### Surface status histogram

| Status | Count |
| --- | ---: |
| accepted | 1 |

### Behaviour status histogram

| Status | Count |
| --- | ---: |
| converted | 1 |
| deferred | 1 |
| documented | 2 |

### Characterization flags

| Flag | Count |
| --- | ---: |
| legacy_green | 3 |
| parity_green | 0 |

### Unscanned hints

- background jobs
