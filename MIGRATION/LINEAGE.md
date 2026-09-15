# Phase 0.5 — Lineage Map

This file records observed source-to-source relationships. It is not a claim that the target is already merged.

## Exact content lineage established by blob SHA

| Artifact | Repository A | Repository B | Evidence | Interpretation |
|---|---|---|---|---|
| P/S/T behavior engine | `hamidcognition-complete/core/hamid_cognition.py` | `hamidcognition-v0-max/core/behavior.py` | SHA `1c71fd77b7bf3cde5665a7eb413d3a55aac0e402` | exact same blob |
| GradientBoosting predictor | `hamidcognition-complete/model.py` | `hamidcognition-v0-max/core/model.py` | SHA `3d7c10c3ea868e3d9652dfaddcfbb399cd49116c` | exact same blob |
| market feed | `hamidcognition-complete/market_feed.py` | `hamidcognition-v0-max/data/market_feed.py` | SHA `84204f60af2fce96d9b35881acd6078cb3e7972c` | exact same blob |
| configuration | `hamidcognition-complete/config.py` | `hamidcognition-v0-max/config.py` | SHA `7317d096ebb0ee39fd0621e3259463a25cbda82c` | exact same blob |
| dashboard template | `hamidcognition-complete/templates/index.html` | `hamidcognition-v0-max/ui/templates/dashboard.html` | SHA `8c2b7a0e886ab687ac2a6cb5e2979e6a02a045e4` | exact same blob, renamed/repositioned |
| Python dependencies | `hamidcognition-complete/requirements.txt` | `hamidcognition-realtime/requirements.txt` | SHA `72b5fc9cf0940c8a8aed3c93ee5acd478b612217` | exact same dependency file |

## Distinct implementations

### Realtime cognition
`hamidcognition-realtime/core/hamid_cognition.py` is a different implementation (SHA `3cf67fec9a95198a1045dab98ee0ce6016d90e54`). It changes initial P/S/T, phase thresholds, exposes market-context update, confidence, jump risk, state export and decision bias. It must not be silently collapsed into the baseline engine.

### Standalone HamidCognition
`HamidCognition/hamid_cognition_engine.py` is a different implementation (SHA `226c748173c98017d65446735c0fe87f09506073`). It retains the same broad incremental P/S/T transition family but adds initial-state recording and jump-risk calculation and also embeds transfer-package generation.

### HamidCognitionEngine
`HamidCognitionEngine/hamid_cognition_engine.py` is materially different (SHA `589ab1e0e0330d0efaff088ef67bb79a8e86f04d`). Its `hamid_step_absolute` multiplies P and S by external factors and divides T by freedom, and its phase model uses absolute thresholds above 1.5 for P/S. This is not interchangeable with the normalized 0–1 family.

## Provenance rule

Exact SHA equality is evidence of identical blob content. It is not evidence of authorship chronology, semantic equivalence of the surrounding systems, or preservation of Git history.

No source repository has been deleted or rewritten by this phase.
