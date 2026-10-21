---
name: Jira cards
description: Use when a factory output or a human bind/accept must be written onto the Jira ticket for that feature.
---

# Jira cards (operator skill)

Write all output in ASD-STE100 only. See skills/operator/asd-ste100/SKILL.md.

Post every factory station output and every human bind, accept, reject, or defer onto the Jira ticket for that feature. The named owner of this skill is the **operator** (not a foreman and not an agent acting as one). Git artefacts remain the source of truth; Jira is claims and tracking only.

## Context hard gate

Read `docs/FIELD-GUIDE.md` and `docs/OPERATOR-RUNBOOK.md` first. **Refuse** if either is missing from context.

Also **refuse** if `JIRA_CLOUD_ID` or `JIRA_PROJECT_KEY` is unset. This skill is the only operator skill that hard-refuses missing Jira configuration. Other skills warn and still write git artefacts.

Do not create an MCP server, a Slack bot, a Slack account, or a GitHub Personal Access Token. Use the **existing** Atlassian MCP only. Never scrape session cookies or mint credentials.

## When to use

- A station has written an artefact (Discovery card, Test gen pack, RECORD / `WAIVED_*`, Architecture DRAFT or PACK BIND, Conversion PR, Verification COMPARE / `PARITY`).
- A human has bound, accepted, rejected, or deferred a feature (or answered a mid-gate that should appear on the ticket).
- The operator says “Post this output / bind to the feature ticket.”

## Inputs

| Input | Notes |
| --- | --- |
| `JIRA_CLOUD_ID` | Cloud id or your Atlassian site URL. |
| `JIRA_PROJECT_KEY` | Project key. |
| `FEATURE_ID`(s) | One or more factory feature identifiers. |
| Event type | `output` \| `bind-accept` \| `bind-reject` \| `bind-defer` \| `gate`. |
| Decision | Required when Event type is `gate`: `approve` \| `approve-with-nits` \| `waive` \| `block` \| `defer` \| `drop`. |
| Station | Discovery, Test generation, Test execution, Architecture, Conversion, Verification. |
| Artefact path(s) | Git paths that landed (summarise; do not paste whole files). |
| Who | Named human or agent identity that produced the event. |
| When | Timestamp in your timezone (state the zone). |

The default factory columns below are example names. Resolve transitions from the issue’s actual project.

## Recipe

### 1. Resolve the ticket

Search in this order, using Atlassian MCP and looking up each tool’s schema at call time:

1. Label matching `FEATURE_ID` in `JIRA_PROJECT_KEY`.
2. Summary / text search for the id in that project.
3. `jira_key` on the Discovery behaviour card or `MANIFEST.yaml`.

If none exists, **create a Task**:

- Summary: `{FEATURE_ID} — {name}`
- Labels: always include the feature id.
- Description: a **Behaviour ID** line plus a short STE-style behaviour (Stimulus / Transform / Expect). Keep it short.

`createJiraIssue` **cannot** set status. New Tasks take the project’s **initial** workflow status. After create, immediately `getJiraIssue` (or read the create response) and inspect the status **name** and `statusCategory.key`.

- If the status is not Backlog, call `getTransitionsForJiraIssue` then `transitionJiraIssue` to **Backlog** (To Do category).
- If the issue is in a **Done-category** status (`statusCategory.key` is `done`, e.g. a Done-category column such as **Ready to convert**), this is a **fail**, not a shrug. Keep trying a transition to Backlog (or any To Do / In Progress named Backlog or Discovery). Do **not** apply the “leave it if the named column is missing” rule while the card is Done-category. If no safe transition exists, **stop** and tell the operator the project’s initial status is Done-category and the board will hide the card.

Never create or leave **new / in-flight** work in Done-category. A Done-category column such as **Ready to convert** **hides** cards.

### 2. Comment on every event

Add a comment for every station output and every human bind / accept / reject / defer. Summarise what changed. Do not paste huge files.

Use your timezone for `when` and state the zone. Include feature id, station, artefact path(s), what changed, who, and when.

### 3. Transition (never invent statuses)

Call `getTransitionsForJiraIssue`, then `transitionJiraIssue` with a transition that **exists**. If the named column is absent **and the issue is not in a Done-category status**, comment that the board does not expose it and leave the issue where it is. That leave-it rule does **not** apply while the card is Done-category (see step 1).

**Default factory columns** (example names, not a single hard-coded board): Backlog, Discovery, Test generation, Test execution, Architecture, Conversion, Verification, Done, Deferred.

**Conversion must stay an In Progress category status, never Done.** A Done-category Conversion column hides in-flight implementation.

| Event | Target column |
| --- | --- |
| Discovery artefacts, or `bind-accept` from Backlog | Discovery |
| `bind-defer` or `bind-reject` | Deferred (comment the reason; **do not delete** the issue) |
| Test gen artefacts | Test generation |
| Test exec RECORD or `WAIVED_*` | Test execution |
| Architecture DRAFT or PACK BIND | Architecture |
| Conversion PR / implementation | Conversion |
| Verification COMPARE | Verification |
| Verification `PARITY` GREEN | **Done** (this is allowed; it is finished work — the only Done move this skill makes) |
| `gate` + `approve` / `approve-with-nits` | Comment; **stay** on the current station column (do not skip ahead unless the operator names a next station) |
| `gate` + `waive` | If it is a characterisation waiver (`WAIVED_*`), Test execution; otherwise stay |
| `gate` + `defer` / `drop` | Deferred (comment the reason; **do not delete**) |
| `gate` + `block` | Stay; comment the block. Do not move |

Do not skip columns to “catch up” unless the operator explicitly asks. One event → one comment → one attempted transition.

## Tools (existing Atlassian MCP)

Look up input schemas at call time. Do not invent fields.

- `searchJiraIssuesUsingJql`
- `createJiraIssue`
- `getJiraIssue`
- `editJiraIssue`
- `addCommentToJiraIssue`
- `getTransitionsForJiraIssue`
- `transitionJiraIssue`

Never scrape cookies. Never create GitHub PATs or Slack bots. Never stand up a new MCP server.

## Proof vs tracking

Jira is **claims and tracking**, not proof. Git artefacts remain source of truth (`MANIFEST.yaml`, bind records, `WAIVED_*`, PACK `status: BOUND`, `PARITY.yaml`, Conversion inventory / generated COVERAGE).

This skill **does not** replace `record-bind` or `architecture-pack-bind`. It must **not** self-bind. A ticket comment is never parity proof and never a BIND.

## Paste-ready comment template

```text
Factory update — {FEATURE_ID}
Ticket: {JIRA_KEY}   Project: {JIRA_PROJECT_KEY}

Event: output | bind-accept | bind-reject | bind-defer | gate
Station: {Discovery | Test generation | Test execution | Architecture | Conversion | Verification}
Artefacts:
- {path}
- {path}

What changed:
{Write two to five short sentences. Write one idea in each sentence. Do not paste full files.}

Who: {name}
When: {YYYY-MM-DD HH:MM TZ}

Column: {from} → {to}  (or: left in {column}; no matching transition)
Git artefacts are the source of truth. This comment is tracking. This comment is not proof.
```

## Refuse

- No Field Guide (or no Operator Runbook) in context
- `JIRA_CLOUD_ID` or `JIRA_PROJECT_KEY` unset
- Posting COMPARE as RECORD (or otherwise mis-labelling the station)
- Treating a ticket comment as parity proof, BIND, or `REPLAY_GREEN`
- Creating a new MCP server, Slack bot / Slack account, or GitHub PAT
- Scraping cookies or minting credentials
- Creating **new** work in a Done-category status, or moving **in-flight / unfinished** work into Done-category (e.g. a Done-category column such as “Ready to convert”)
- Putting Conversion into a Done-category status
- Deleting tickets on reject/defer (move to Deferred and comment the reason)
- Agent self-bind of MANIFEST or Architecture PACK via this skill

Verification `PARITY` GREEN **must** move to Done. That is finished work and the **only** Done-category move this skill makes; do not refuse it.
