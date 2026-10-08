# Version Truth Report — Pre-Outreach Audit

**Audit date:** 2026-10-08  
**Method:** GitHub API reads of the default branch, canonical version file, release metadata, workflow run, and commercial documents. No local clean-room rebuild was performed during this audit.

## Canonical identity

- **Project:** BESAZ.
- **Product/line:** HamidCognition Action Gate.
- **Canonical executable version source:** `action_gate/VERSION`.
- **Current main version string:** `1.1.1`.
- **Latest published technical release:** `action-gate-v1.1.1`.

## Exact version truth

| Field | Observed value | Interpretation |
|---|---|---|
| `action_gate/VERSION` on main | `1.1.1` | Current mutable branch's version string |
| Main SHA at audit | `a27a8a8f15dada67fba6567fb32ddb3ef37f6563` | Current development head observed in GitHub |
| Release tag | `action-gate-v1.1.1` | Published release |
| Release source SHA | `e9ea7565f4ddea91f5c45104237bd20564c80894` | Exact source revision recorded by release metadata |
| Release workflow | `36966012148` | GitHub reports completed / success for the release SHA |
| Artifact | `action-gate-1.1.1.tar` | Published release asset |
| Artifact digest | `sha256:517064de0427286ff4f346d46996642aca3b9def891d1c08bfaebc25546fb791` | Digest in GitHub release metadata |
| Published at | `2026-10-02T04:47:41Z` | Release metadata timestamp |

## Reconciled truth

The version string on main and the release tag both say 1.1.1, but their source SHAs differ. A matching version string does not establish binary/source equivalence.

```text
CANONICAL_PROJECT = BESAZ
PRODUCT = HamidCognition Action Gate
PUBLISHED_RELEASE = action-gate-v1.1.1
RELEASE_SHA = e9ea7565f4ddea91f5c45104237bd20564c80894
MAIN_SHA = a27a8a8f15dada67fba6567fb32ddb3ef37f6563
VERSION_STRING_MATCH = true
SOURCE_SHA_MATCH = false
MAIN_EQUIVALENT_TO_RELEASE = UNKNOWN / NOT ESTABLISHED
```

For customer delivery, quote the immutable release/tag and checksum. Do not describe current main as independently validated until same-SHA gates and artifact generation establish that fact.

## Contradictions found and disposition

1. `PRODUCT/CURRENT_COMMERCIAL_RELEASE.md` could be read as saying that main is the same validated release because it says the development line is v1.1.1. It is being clarified to distinguish version string from exact source revision.
2. `SALES/PILOT_OFFER.md` described price as negotiated while `pilot.html` advertises a $2,500 fixed 30-day pilot. The standard scoped offer is being aligned to $2,500, with any deviation requiring an explicit written quote.
3. Issue #66 contains the historical v1.0.10 / $7,500–10,000 launch proposal. Those terms are superseded for the current standard pilot; the issue is retained as historical launch tracking and must not be used as current quoting authority.

## Commercial truth boundary

The release workflow validates only its exact tested revision. It does not establish customer deployment, acceptance, payment, revenue, regulatory certification, or customer production use.

## Evidence sources

- [README](../README.md)
- [Canonical version file](../action_gate/VERSION)
- [Published v1.1.1 release](https://github.com/hamidhayatijozani/HamidCognition-Unified/releases/tag/action-gate-v1.1.1)
- [Release workflow run 36966012148](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/36966012148)
- [Current main commit](https://github.com/hamidhayatijozani/HamidCognition-Unified/commit/a27a8a8f15dada67fba6567fb32ddb3ef37f6563)
- [Commercial launch issue #66](https://github.com/hamidhayatijozani/HamidCognition-Unified/issues/66)
