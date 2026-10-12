# Phase 2 — Complete Static File-Lineage Manifest

**Audit date:** 2026-10-12  
**Target:** `hamidhayatijozani/HamidCognition-Unified` branch `main`  
**Method:** recursive Git tree inventory and exact blob-SHA matching.  
**Limit:** Exact blob equality proves byte-identical file content, not equivalent behavior, imports, runtime readiness, or test success. No source was executed, moved, or deleted by this manifest.

## HamidCognition

- Default branch: `master`
- Tracked blobs: 13
- Exact same path and SHA: 0
- Exact blob SHA at another path: 2
- No exact blob match in Unified: 11
- Tree truncated: false

| Source path | Source blob SHA | Disposition | Exact match in Unified / basename candidates |
|---|---|---|---|
| `README.md` | `beb22daae32511da0986891a6d31e134c1309f43` | NO_EXACT_MATCH | Same basename only (not proof of equivalence): PROJECT/llm_fx_eval/README.md<br>README.md<br>RESEARCH/experiments/README.md<br>action_gate/README.md<br>action_gate/contracts/README.md<br>experiments/EXP-001/README.md<br>experiments/EXP-002/README.md<br>experiments/EXP-003/README.md<br>experiments/EXP-004/README.md<br>integrated/README.md<br>integrated/research/README.md<br>n8n/README.md<br>research/claimlab/README.md<br>runtime/README.md<br>state_bound/README.md |
| `RESEARCH_LINEAGE.md` | `f1ca4e5a6b8d77ace86bfa4e0414d65d15120be8` | NO_EXACT_MATCH | None |
| `cognitive_transfer_report.md` | `bdd0b45546bb2840d552ef6adcc179f9aa803e87` | NO_EXACT_MATCH | None |
| `eurusd_engine.py` | `035ac721715f2274c0cfcb3cd727deded01ed7b2` | EXACT_MATCH_MOVED | integrated/trading/HamidCognition/eurusd_engine.py |
| `eurusd_engine_real.py` | `005b643c57102fac4f3466372a1f8c569565f43c` | NO_EXACT_MATCH | None |
| `eurusd_state.json` | `16965004e45f780a800133a82714864391d22b92` | NO_EXACT_MATCH | None |
| `eurusd_trade_report.json` | `a3cf6f483c22779cb5d0b4175895f9156da599aa` | NO_EXACT_MATCH | None |
| `hamid_cognition_engine.py` | `226c748173c98017d65446735c0fe87f09506073` | EXACT_MATCH_MOVED | integrated/ps_t/HamidCognition/hamid_cognition_engine.py |
| `hamid_cognition_transfer.json` | `78a9eda324634c829ded94eed290636c01335fbf` | NO_EXACT_MATCH | None |
| `real_world_analysis_report.json` | `6aa8f827e3879e80289363071928e789a550607b` | NO_EXACT_MATCH | None |
| `run_eurusd.py` | `a08c22cda93bfa4f9532488d6c2da6ed2ed1f31b` | NO_EXACT_MATCH | None |
| `run_eurusd_real.py` | `1d3c19f65b4dbdbd93e0d6d6fd9053252c899507` | NO_EXACT_MATCH | None |
| `simple_eurusd.py` | `a4b063cf2665878912723d8de04440fd1fb98b79` | NO_EXACT_MATCH | None |

**Disposition rule:** `NO_EXACT_MATCH` means a human-reviewed port or an explicit `HISTORICAL_ONLY` decision is required before archive. It does not by itself mean the file is missing from the product; it may have been deliberately rewritten.

## HamidCognitionEngine

- Default branch: `master`
- Tracked blobs: 12
- Exact same path and SHA: 1
- Exact blob SHA at another path: 1
- No exact blob match in Unified: 10
- Tree truncated: false

| Source path | Source blob SHA | Disposition | Exact match in Unified / basename candidates |
|---|---|---|---|
| `.github/workflows/pst-canonical.yml` | `30fc88368b42d51aca60ba5dbaf67c9df2dda394` | NO_EXACT_MATCH | None |
| `README.md` | `2f3ea8734f059cbca1cffaf1dbe459906ba95dc6` | NO_EXACT_MATCH | Same basename only (not proof of equivalence): PROJECT/llm_fx_eval/README.md<br>README.md<br>RESEARCH/experiments/README.md<br>action_gate/README.md<br>action_gate/contracts/README.md<br>experiments/EXP-001/README.md<br>experiments/EXP-002/README.md<br>experiments/EXP-003/README.md<br>experiments/EXP-004/README.md<br>integrated/README.md<br>integrated/research/README.md<br>n8n/README.md<br>research/claimlab/README.md<br>runtime/README.md<br>state_bound/README.md |
| `RESEARCH_LINEAGE.md` | `3f60b80fbf2e1e763059d425e2d9787a406ba122` | NO_EXACT_MATCH | None |
| `android_python_guide.md` | `a19c03784948d2ecaba3c15248d51633ccc896a3` | NO_EXACT_MATCH | None |
| `forex_trading_bot.py` | `31fd342bf5056d7d0c1a1c3b5210177370f236d7` | NO_EXACT_MATCH | None |
| `hamid_cognition_engine.py` | `589ab1e0e0330d0efaff088ef67bb79a8e86f04d` | EXACT_MATCH_MOVED | integrated/ps_t/HamidCognitionEngine/hamid_cognition_engine.py |
| `integrated/ps_t/canonical_engine.py` | `c4f9f0823dae4f9f0e0cccb53d93335debad3918` | NO_EXACT_MATCH | Same basename only (not proof of equivalence): integrated/ps_t/canonical_engine.py |
| `integrated/ps_t/canonical_weights.json` | `ed816af29bbcad53254a677810f6175d13105425` | EXACT_SAME_PATH | integrated/ps_t/canonical_weights.json |
| `integrated/ps_t/test_canonical_engine.py` | `7df5dc390a049096710c9d0d78236095bf7d4082` | NO_EXACT_MATCH | Same basename only (not proof of equivalence): integrated/ps_t/test_canonical_engine.py |
| `run_hamid.py` | `882b221cc61dd4499cc56077a12385f9728572ad` | NO_EXACT_MATCH | None |
| `sample_input_data.csv` | `e22b3e1584a9d9cf90f94ef2fbe740ad34622e9d` | NO_EXACT_MATCH | None |
| `trade_log.json` | `77b0a713b25e5005cb8b9616e31970c0eaeb109f` | NO_EXACT_MATCH | None |

**Disposition rule:** `NO_EXACT_MATCH` means a human-reviewed port or an explicit `HISTORICAL_ONLY` decision is required before archive. It does not by itself mean the file is missing from the product; it may have been deliberately rewritten.

## hamidcognition-web

- Default branch: `main`
- Tracked blobs: 6
- Exact same path and SHA: 0
- Exact blob SHA at another path: 1
- No exact blob match in Unified: 5
- Tree truncated: false

| Source path | Source blob SHA | Disposition | Exact match in Unified / basename candidates |
|---|---|---|---|
| `.gitignore` | `598d76d9e6f1d1ebd1f2c2054fa744af7fb89f84` | NO_EXACT_MATCH | Same basename only (not proof of equivalence): .gitignore |
| `README.md` | `54f9f9dd210520bd858884cb37c18b427ddf918c` | NO_EXACT_MATCH | Same basename only (not proof of equivalence): PROJECT/llm_fx_eval/README.md<br>README.md<br>RESEARCH/experiments/README.md<br>action_gate/README.md<br>action_gate/contracts/README.md<br>experiments/EXP-001/README.md<br>experiments/EXP-002/README.md<br>experiments/EXP-003/README.md<br>experiments/EXP-004/README.md<br>integrated/README.md<br>integrated/research/README.md<br>n8n/README.md<br>research/claimlab/README.md<br>runtime/README.md<br>state_bound/README.md |
| `RESEARCH_LINEAGE.md` | `02765c4c1d99c51d6b9629126ab92db1b7a755a0` | NO_EXACT_MATCH | None |
| `app.py` | `ef64e66878ec11d2eecfa0c5c2c7210838c43238` | NO_EXACT_MATCH | Same basename only (not proof of equivalence): action_gate/app.py<br>dashboard/app.py<br>integrated/realtime/app.py<br>integrated/web/app.py |
| `requirements.txt` | `4a9579e376016f5cc3f4823e38671e2b0ec8fc69` | NO_EXACT_MATCH | Same basename only (not proof of equivalence): action_gate/requirements.txt<br>dashboard/requirements.txt<br>research/claimlab/requirements.txt |
| `templates/dashboard.html` | `42007bd760b09ecea27f8c44a8301efeb58828d4` | EXACT_MATCH_MOVED | integrated/web/templates/dashboard.html |

**Disposition rule:** `NO_EXACT_MATCH` means a human-reviewed port or an explicit `HISTORICAL_ONLY` decision is required before archive. It does not by itself mean the file is missing from the product; it may have been deliberately rewritten.

## hamidcognition-realtime

- Default branch: `main`
- Tracked blobs: 16
- Exact same path and SHA: 0
- Exact blob SHA at another path: 8
- No exact blob match in Unified: 8
- Tree truncated: false

| Source path | Source blob SHA | Disposition | Exact match in Unified / basename candidates |
|---|---|---|---|
| `.gitignore` | `bea7a225a74547aa260aa7f031c8db9a3bce02ea` | NO_EXACT_MATCH | Same basename only (not proof of equivalence): .gitignore |
| `README.md` | `8fd97f451138658bc61df624716536516229854d` | NO_EXACT_MATCH | Same basename only (not proof of equivalence): PROJECT/llm_fx_eval/README.md<br>README.md<br>RESEARCH/experiments/README.md<br>action_gate/README.md<br>action_gate/contracts/README.md<br>experiments/EXP-001/README.md<br>experiments/EXP-002/README.md<br>experiments/EXP-003/README.md<br>experiments/EXP-004/README.md<br>integrated/README.md<br>integrated/research/README.md<br>n8n/README.md<br>research/claimlab/README.md<br>runtime/README.md<br>state_bound/README.md |
| `RESEARCH_LINEAGE.md` | `1414468b72ff9071c1544f6764114074ffca201a` | NO_EXACT_MATCH | None |
| `api/__init__.py` | `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391` | EXACT_MATCH_MOVED | RESEARCH/experiments/__init__.py |
| `api/forex_data.py` | `cc6d0e99a6ffe81b8dcd642e59bdbe8aaff878f4` | EXACT_MATCH_MOVED | integrated/realtime/api/forex_data.py |
| `app.py` | `4c2c2cd820946af0e68d7e76db2764e1996c8292` | EXACT_MATCH_MOVED | integrated/realtime/app.py |
| `core/__init__.py` | `3e83c630dd1490116c306cfaf22393cdebc7b8da` | NO_EXACT_MATCH | Same basename only (not proof of equivalence): RESEARCH/experiments/__init__.py<br>RESEARCH/market_lab/__init__.py<br>action_gate/__init__.py<br>broker_runtime/__init__.py<br>financial_runtime/__init__.py<br>protected_tools/__init__.py<br>research/claimlab/__init__.py<br>state_bound/__init__.py |
| `core/hamid_cognition.py` | `3cf67fec9a95198a1045dab98ee0ce6016d90e54` | EXACT_MATCH_MOVED | integrated/realtime/core/hamid_cognition.py |
| `integrated/ps_t/canonical_engine.py` | `a52ea135755e3b31f804134cb53d1e0d525e4c69` | NO_EXACT_MATCH | Same basename only (not proof of equivalence): integrated/ps_t/canonical_engine.py |
| `integrated/ps_t/canonical_weights.json` | `5a6cfef3cc40ff8eef6ce95eaafd9ab4247cb4f3` | NO_EXACT_MATCH | Same basename only (not proof of equivalence): integrated/ps_t/canonical_weights.json |
| `integrated/ps_t/test_canonical_engine.py` | `8f4ce9a531c2e1faf5294484ea959f821678b069` | NO_EXACT_MATCH | Same basename only (not proof of equivalence): integrated/ps_t/test_canonical_engine.py |
| `models/__init__.py` | `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391` | EXACT_MATCH_MOVED | RESEARCH/experiments/__init__.py |
| `models/predictor.py` | `df584043edb5fa5a2037adbc72f1bf90568ac9da` | EXACT_MATCH_MOVED | integrated/realtime/models/predictor.py |
| `requirements.txt` | `72b5fc9cf0940c8a8aed3c93ee5acd478b612217` | NO_EXACT_MATCH | Same basename only (not proof of equivalence): action_gate/requirements.txt<br>dashboard/requirements.txt<br>research/claimlab/requirements.txt |
| `ui/__init__.py` | `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391` | EXACT_MATCH_MOVED | RESEARCH/experiments/__init__.py |
| `ui/templates/dashboard.html` | `7308a0e58edfdf763a541015e5fdcc62ad414ba4` | EXACT_MATCH_MOVED | integrated/realtime/ui/templates/dashboard.html |

**Disposition rule:** `NO_EXACT_MATCH` means a human-reviewed port or an explicit `HISTORICAL_ONLY` decision is required before archive. It does not by itself mean the file is missing from the product; it may have been deliberately rewritten.

## hamidcognition-v0-max

- Default branch: `main`
- Tracked blobs: 21
- Exact same path and SHA: 0
- Exact blob SHA at another path: 6
- No exact blob match in Unified: 15
- Tree truncated: false

| Source path | Source blob SHA | Disposition | Exact match in Unified / basename candidates |
|---|---|---|---|
| `.github/workflows/ci-cd.yml` | `72afa5ebf706a805f46ab705ab4ebe7a5e91e46a` | NO_EXACT_MATCH | None |
| `.github/workflows/python-publish.yml` | `82f8dbd960d2ee51c15733a17ca612a00645c862` | NO_EXACT_MATCH | None |
| `.github/workflows/rfc-0003.yml` | `c25c29b0e7188943d8640d93be3accaa29d94dde` | NO_EXACT_MATCH | None |
| `Dockerfile` | `6cf48d893899dbea80689276758216f880217886` | NO_EXACT_MATCH | Same basename only (not proof of equivalence): action_gate/Dockerfile<br>dashboard/Dockerfile |
| `README.md` | `dd16ec77cbdb07394d988668095da835b51993d4` | NO_EXACT_MATCH | Same basename only (not proof of equivalence): PROJECT/llm_fx_eval/README.md<br>README.md<br>RESEARCH/experiments/README.md<br>action_gate/README.md<br>action_gate/contracts/README.md<br>experiments/EXP-001/README.md<br>experiments/EXP-002/README.md<br>experiments/EXP-003/README.md<br>experiments/EXP-004/README.md<br>integrated/README.md<br>integrated/research/README.md<br>n8n/README.md<br>research/claimlab/README.md<br>runtime/README.md<br>state_bound/README.md |
| `RESEARCH_LINEAGE.md` | `5ddaeb1701b19dd46e5849f6abc4bbe3a9a7eafe` | NO_EXACT_MATCH | None |
| `api/app.py` | `2fed882489ae3a6d893ac9e70ccf3736a61408d1` | NO_EXACT_MATCH | Same basename only (not proof of equivalence): action_gate/app.py<br>dashboard/app.py<br>integrated/realtime/app.py<br>integrated/web/app.py |
| `api/server.py` | `2c87e5a75098a6cdad2022169813a557c60b49cd` | NO_EXACT_MATCH | None |
| `config.py` | `7317d096ebb0ee39fd0621e3259463a25cbda82c` | EXACT_MATCH_MOVED | integrated/runtime/complete/config.py |
| `core/behavior.py` | `1c71fd77b7bf3cde5665a7eb413d3a55aac0e402` | EXACT_MATCH_MOVED | integrated/legacy/v0-max/core/behavior.py<br>integrated/ps_t/complete/core/hamid_cognition.py |
| `core/model.py` | `3d7c10c3ea868e3d9652dfaddcfbb399cd49116c` | EXACT_MATCH_MOVED | integrated/legacy/v0-max/core/model.py<br>integrated/trading/complete/model.py |
| `data/market_feed.py` | `84204f60af2fce96d9b35881acd6078cb3e7972c` | EXACT_MATCH_MOVED | integrated/legacy/v0-max/data/market_feed.py<br>integrated/trading/complete/market_feed.py |
| `docker-compose.yml` | `bef5f9d0c1d4b0b4e1517d370fef67d3fdbb8258` | NO_EXACT_MATCH | Same basename only (not proof of equivalence): action_gate/docker-compose.yml<br>n8n/docker-compose.yml |
| `governance/RFC-0003-INTEGRATION.md` | `eb0f8974c9a3f7cded499fdb4199d969b51f0ce6` | NO_EXACT_MATCH | None |
| `governance/__init__.py` | `9b1d5e0db4f5090c393284cad6b7bad2fee87d85` | NO_EXACT_MATCH | Same basename only (not proof of equivalence): RESEARCH/experiments/__init__.py<br>RESEARCH/market_lab/__init__.py<br>action_gate/__init__.py<br>broker_runtime/__init__.py<br>financial_runtime/__init__.py<br>protected_tools/__init__.py<br>research/claimlab/__init__.py<br>state_bound/__init__.py |
| `governance/governance_engine.py` | `ca0afa0ddb0b58517e7dfe265801f9e4745c1262` | NO_EXACT_MATCH | None |
| `main.py` | `96961db12f610c6b79172ca02e2ab22e0de7bce9` | EXACT_MATCH_MOVED | integrated/runtime/v0-max/main.py |
| `requirements.txt` | `994febc5fe847260d41d475e14014a177275094c` | NO_EXACT_MATCH | Same basename only (not proof of equivalence): action_gate/requirements.txt<br>dashboard/requirements.txt<br>research/claimlab/requirements.txt |
| `tests/test_api.py` | `e895fc1005f4a478c003f3cd64de563c1495c20d` | NO_EXACT_MATCH | None |
| `tests/test_governance_engine.py` | `59ad82b984eae308e69a0ba0a14cea7ae2dd2a8a` | NO_EXACT_MATCH | None |
| `ui/templates/dashboard.html` | `8c2b7a0e886ab687ac2a6cb5e2979e6a02a045e4` | EXACT_MATCH_MOVED | integrated/web/complete/templates/index.html |

**Disposition rule:** `NO_EXACT_MATCH` means a human-reviewed port or an explicit `HISTORICAL_ONLY` decision is required before archive. It does not by itself mean the file is missing from the product; it may have been deliberately rewritten.

## hamidcognition-complete

- Default branch: `main`
- Tracked blobs: 17
- Exact same path and SHA: 0
- Exact blob SHA at another path: 6
- No exact blob match in Unified: 11
- Tree truncated: false

| Source path | Source blob SHA | Disposition | Exact match in Unified / basename candidates |
|---|---|---|---|
| `Procfile` | `2e35818f675d5a1a7b6a84e4561bec032180c1d6` | NO_EXACT_MATCH | None |
| `README.md` | `f84891ab0656347f2d14ff789055ea547ef5c39b` | NO_EXACT_MATCH | Same basename only (not proof of equivalence): PROJECT/llm_fx_eval/README.md<br>README.md<br>RESEARCH/experiments/README.md<br>action_gate/README.md<br>action_gate/contracts/README.md<br>experiments/EXP-001/README.md<br>experiments/EXP-002/README.md<br>experiments/EXP-003/README.md<br>experiments/EXP-004/README.md<br>integrated/README.md<br>integrated/research/README.md<br>n8n/README.md<br>research/claimlab/README.md<br>runtime/README.md<br>state_bound/README.md |
| `RESEARCH_LINEAGE.md` | `7005d65dd4bbec8e13ad8a9c659f6f6c8d1f4b86` | NO_EXACT_MATCH | None |
| `__pycache__/main.cpython-311.pyc` | `74a07201dd65b8cd7bd4e5f5cf230eff3f46e23a` | NO_EXACT_MATCH | None |
| `app.py` | `6d3242afb5a86cc115fef3e6944cd7b6a39030f3` | NO_EXACT_MATCH | Same basename only (not proof of equivalence): action_gate/app.py<br>dashboard/app.py<br>integrated/realtime/app.py<br>integrated/web/app.py |
| `config.py` | `7317d096ebb0ee39fd0621e3259463a25cbda82c` | EXACT_MATCH_MOVED | integrated/runtime/complete/config.py |
| `core/hamid_cognition.py` | `1c71fd77b7bf3cde5665a7eb413d3a55aac0e402` | EXACT_MATCH_MOVED | integrated/legacy/v0-max/core/behavior.py<br>integrated/ps_t/complete/core/hamid_cognition.py |
| `creative-generator/UltimateCreativeGenerator.kt` | `6531386f51c32457db6c348a30f1eaffda6a8c56` | NO_EXACT_MATCH | None |
| `integrated/ps_t/canonical_engine.py` | `a52ea135755e3b31f804134cb53d1e0d525e4c69` | NO_EXACT_MATCH | Same basename only (not proof of equivalence): integrated/ps_t/canonical_engine.py |
| `integrated/ps_t/canonical_weights.json` | `5a6cfef3cc40ff8eef6ce95eaafd9ab4247cb4f3` | NO_EXACT_MATCH | Same basename only (not proof of equivalence): integrated/ps_t/canonical_weights.json |
| `integrated/ps_t/test_canonical_engine.py` | `8f4ce9a531c2e1faf5294484ea959f821678b069` | NO_EXACT_MATCH | Same basename only (not proof of equivalence): integrated/ps_t/test_canonical_engine.py |
| `main.py` | `cf5324113ea7729a253deab7c1e7b0a63497b275` | EXACT_MATCH_MOVED | integrated/runtime/complete/main.py |
| `market_feed.py` | `84204f60af2fce96d9b35881acd6078cb3e7972c` | EXACT_MATCH_MOVED | integrated/legacy/v0-max/data/market_feed.py<br>integrated/trading/complete/market_feed.py |
| `mobile/app/src/main/kotlin/com/hamidcognition/main/MainActivity.kt` | `03621ef98aaa0d4bcfed7987dfead43b82aadac3` | NO_EXACT_MATCH | None |
| `model.py` | `3d7c10c3ea868e3d9652dfaddcfbb399cd49116c` | EXACT_MATCH_MOVED | integrated/legacy/v0-max/core/model.py<br>integrated/trading/complete/model.py |
| `requirements.txt` | `72b5fc9cf0940c8a8aed3c93ee5acd478b612217` | NO_EXACT_MATCH | Same basename only (not proof of equivalence): action_gate/requirements.txt<br>dashboard/requirements.txt<br>research/claimlab/requirements.txt |
| `templates/index.html` | `8c2b7a0e886ab687ac2a6cb5e2979e6a02a045e4` | EXACT_MATCH_MOVED | integrated/web/complete/templates/index.html |

**Disposition rule:** `NO_EXACT_MATCH` means a human-reviewed port or an explicit `HISTORICAL_ONLY` decision is required before archive. It does not by itself mean the file is missing from the product; it may have been deliberately rewritten.

## Archive readiness gate

No archive action is authorized by this manifest. Before any candidate can be archived:

1. Assign every `NO_EXACT_MATCH` row one explicit disposition: migrated with behavior test, intentionally historical, generated/transient, or unresolved.
2. Check imports, workflows, deployments, release assets, packages, open issues/PRs, external callers, and secrets/variables referenced by CI.
3. Run required tests on the exact candidate HEAD and preserve raw logs/artifact links.
4. Re-read HEAD immediately before archive and ensure no new commit or PR appeared.
5. Archive one repository at a time; verify the archived state and document unarchive instructions. Never delete repository history.

## Current HEAD and CI caveats

- `HamidCognitionEngine` current HEAD observed at `9da718d1ba8964a4e4ae3f0f5e3455c6c26cdecb` (2026-10-12). The latest `PST Canonical Contract` workflow is successful on that exact SHA: [run 38196610755](https://github.com/hamidhayatijozani/HamidCognitionEngine/actions/runs/38196610755). This is a reason **not** to classify it as simply dead/obsolete; archive readiness still depends on the unique-file gate.
- `hamidcognition-v0-max` has successful CI on its current HEAD `7da846315ea56a6d1b187546b47f68ffe291c004`: [run 36226878991](https://github.com/hamidhayatijozani/hamidcognition-v0-max/actions/runs/36226878991). This does not prove every behavior is represented in Unified.
- `hamidcognition-realtime` latest returned successful dependency-maintenance run is on current HEAD `7217fe47da548b0a084ffc4983d3983e17691c32`, but the run is from 2026-03-26 and is not a full behavioral test: [run 23586206050](https://github.com/hamidhayatijozani/hamidcognition-realtime/actions/runs/23586206050).
- `hamidcognition-complete` latest returned success is an old dependency-maintenance run on SHA `f15508f00c9d6c9087aaf766fd201181d1de8232`, not current HEAD `383037f85830f69a9dbd5f21f8d06526bc67d964`; another historical dependency run failed. Current HEAD test status is UNKNOWN.
- No open PRs were returned for the six source repositories at the time of this query. The query returned no published releases for five of six; `hamidcognition-complete` has one draft, untagged release. Absence in these API results does not prove absence of external deployments or consumers.
- No recent Actions runs were returned for `HamidCognition` or `hamidcognition-web`. Their current test status is UNKNOWN.
