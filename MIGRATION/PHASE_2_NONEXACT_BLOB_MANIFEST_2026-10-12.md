# Phase 2 — Non-Exact Source Blob Manifest (2026-10-12)

**Scope:** tracked blobs in the six historical HamidCognition-family repositories whose Git blob SHA does not appear anywhere in the current `HamidCognition-Unified` default tree as inspected on 2026-10-12.
**Critical interpretation:** non-matching SHA means exact byte identity was not found. It does **not** prove a semantic equivalent is absent. Each item needs an explicit disposition before archive. SHA values are recorded to make the audit reproducible.

## `HamidCognition` — 11 non-exact blobs

| Path | Blob SHA | Initial review class |
|---|---|---|
| `README.md` | `beb22daae32511da0986891a6d31e134c1309f43` | Documentation |
| `RESEARCH_LINEAGE.md` | `f1ca4e5a6b8d77ace86bfa4e0414d65d15120be8` | Provenance documentation |
| `cognitive_transfer_report.md` | `bdd0b45546bb2840d552ef6adcc179f9aa803e87` | Research report |
| `eurusd_engine_real.py` | `005b643c57102fac4f3466372a1f8c569565f43c` | Executable / simulated broker behavior to inspect |
| `eurusd_state.json` | `16965004e45f780a800133a82714864391d22b92` | State artifact |
| `eurusd_trade_report.json` | `a3cf6f483c22779cb5d0b4175895f9156da599aa` | Generated/research result; validate provenance |
| `hamid_cognition_transfer.json` | `78a9eda324634c829ded94eed290636c01335fbf` | Transfer artifact |
| `real_world_analysis_report.json` | `6aa8f827e3879e80289363071928e789a550607b` | Research result; do not treat as independently reproduced |
| `run_eurusd.py` | `a08c22cda93bfa4f9532488d6c2da6ed2ed1f31b` | Executable entrypoint |
| `run_eurusd_real.py` | `1d3c19f65b4dbdbd93e0d6d6fd9053252c899507` | Executable entrypoint; real execution claim needs inspection |
| `simple_eurusd.py` | `a4b063cf2665878912723d8de04440fd1fb98b79` | Executable prototype |

Two other source blobs were found elsewhere in Unified under different paths: `hamid_cognition_engine.py` and `eurusd_engine.py`. This does not settle the eleven entries above.

## `HamidCognitionEngine` — 9 non-exact blobs

| Path | Blob SHA | Initial review class |
|---|---|---|
| `README.md` | `2f3ea8734f059cbca1cffaf1dbe459906ba95dc6` | Documentation |
| `RESEARCH_LINEAGE.md` | `3f60b80fbf2e1e763059d425e2d9787a406ba122` | Provenance documentation |
| `android_python_guide.md` | `a19c03784948d2ecaba3c15248d51633ccc896a3` | User guide; inspect freshness before port |
| `forex_trading_bot.py` | `31fd342bf5056d7d0c1a1c3b5210177370f236d7` | Executable trading simulation; dependencies and behavior need review |
| `integrated/ps_t/canonical_engine.py` | `c4f9f0823dae4f9f0e0cccb53d93335debad3918` | Canonical engine lineage; current Unified copy is not byte-identical |
| `integrated/ps_t/test_canonical_engine.py` | `8e303cde47212c0923208d48e368a9beea6bc1ef` | Test source; hardened version merged via PR #2, compare exact test behavior |
| `run_hamid.py` | `882b221cc61dd4499cc56077a12385f9728572ad` | Executable simulation |
| `sample_input_data.csv` | `e22b3e1584a9d9cf90f94ef2fbe740ad34622e9d` | Sample data |
| `trade_log.json` | `77b0a713b25e5005cb8b9616e31970c0eaeb109f` | Trade log; not validated market performance by itself |

The canonical P/S/T test/CI branch was merged through [HamidCognitionEngine PR #2](https://github.com/hamidhayatijozani/HamidCognitionEngine/pull/2). The PR-head workflow passed; the post-merge workflow was subsequently observed completing successfully on merge SHA `9da718d1ba8964a4e4ae3f0f5e3455c6c26cdecb`.

## `hamidcognition-web` — 5 non-exact blobs

| Path | Blob SHA | Initial review class |
|---|---|---|
| `.gitignore` | `598d76d9e6f1d1ebd1f2c2054fa744af7fb89f84` | Repository metadata |
| `README.md` | `54f9f9dd210520bd858884cb37c18b427ddf918c` | Documentation |
| `RESEARCH_LINEAGE.md` | `02765c4c1d99c51d6b9629126ab92db1b7a755a0` | Provenance documentation |
| `app.py` | `ef64e66878ec11d2eecfa0c5c2c7210838c43238` | Executable web application; differs from current same-name applications |
| `requirements.txt` | `4a9579e376016f5cc3f4823e38671e2b0ec8fc69` | Runtime dependencies |

The dashboard template blob is present in Unified under an integrated path; that is not proof that the full Flask behavior was ported.

## `hamidcognition-realtime` — 8 non-exact blobs

| Path | Blob SHA | Initial review class |
|---|---|---|
| `.gitignore` | `bea7a225a74547aa260aa7f031c8db9a3bce02ea` | Repository metadata |
| `README.md` | `8fd97f451138658bc61df624716536516229854d` | Documentation |
| `RESEARCH_LINEAGE.md` | `1414468b72ff9071c1544f6764114074ffca201a` | Provenance documentation |
| `core/__init__.py` | `3e83c630dd1490116c306cfaf22393cdebc7b8da` | Package marker |
| `integrated/ps_t/canonical_engine.py` | `a52ea135755e3b31f804134cb53d1e0d525e4c69` | Variant/contract source; not byte-identical to Unified copy |
| `integrated/ps_t/canonical_weights.json` | `5a6cfef3cc40ff8eef6ce95eaafd9ab4247cb4f3` | Model configuration lineage |
| `integrated/ps_t/test_canonical_engine.py` | `8f4ce9a531c2e1faf5294484ea959f821678b069` | Test source; compare contract semantics |
| `requirements.txt` | `72b5fc9cf0940c8a8aed3c93ee5acd478b612217` | Runtime dependencies |

The realtime cognition engine, predictor, forex-data provider, and UI template have exact source blobs elsewhere in Unified under integrated paths; the differing canonical engine/config/test trio still needs an explicit disposition.

## `hamidcognition-v0-max` — 15 non-exact blobs

| Path | Blob SHA | Initial review class |
|---|---|---|
| `.github/workflows/ci-cd.yml` | `72afa5ebf706a805f46ab705ab4ebe7a5e91e46a` | CI/deploy workflow |
| `.github/workflows/python-publish.yml` | `82f8dbd960d2ee51c15733a17ca612a00645c862` | Publishing workflow; inspect for secrets/deployment dependencies |
| `.github/workflows/rfc-0003.yml` | `c25c29b0e7188943d8640d93be3accaa29d94dde` | Governance workflow |
| `Dockerfile` | `6cf48d893899dbea80689276758216f880217886` | Build/deployment contract |
| `README.md` | `dd16ec77cbdb07394d988668095da835b51993d4` | Documentation |
| `RESEARCH_LINEAGE.md` | `5ddaeb1701b19dd46e5849f6abc4bbe3a9a7eafe` | Provenance documentation |
| `api/app.py` | `2fed882489ae3a6d893ac9e70ccf3736a61408d1` | API implementation |
| `api/server.py` | `2c87e5a75098a6cdad2022169813a557c60b49cd` | API implementation |
| `docker-compose.yml` | `bef5f9d0c1d4b0b4e1517d370fef67d3fdbb8258` | Runtime/deployment contract |
| `governance/RFC-0003-INTEGRATION.md` | `eb0f8974c9a3f7cded499fdb4199d969b51f0ce6` | Governance specification |
| `governance/__init__.py` | `9b1d5e0db4f5090c393284cad6b7bad2fee87d85` | Package marker |
| `governance/governance_engine.py` | `ca0afa0ddb0b58517e7dfe265801f9e4745c1262` | Governance implementation |
| `requirements.txt` | `994febc5fe847260d41d475e14014a177275094c` | Runtime dependencies |
| `tests/test_api.py` | `e895fc1005f4a478c003f3cd64de563c1495c20d` | API contract tests; branch diff removes specific DENY/SANDBOX assertions |
| `tests/test_governance_engine.py` | `59ad82b984eae308e69a0ba0a14cea7ae2dd2a8a` | Governance contract tests |

The default branch also has a diverged governance-integration branch. Its ahead-only changes must be reviewed before this repository can be called archive-ready.

## `hamidcognition-complete` — 11 non-exact blobs

| Path | Blob SHA | Initial review class |
|---|---|---|
| `Procfile` | `2e35818f675d5a1a7b6a84e4561bec032180c1d6` | Deployment entrypoint |
| `README.md` | `f84891ab0656347f2d14ff789055ea547ef5c39b` | Documentation |
| `RESEARCH_LINEAGE.md` | `7005d65dd4bbec8e13ad8a9c659f6f6c8d1f4b86` | Provenance documentation |
| `__pycache__/main.cpython-311.pyc` | `74a07201dd65b8cd7bd4e5f5cf230eff3f46e23a` | Generated bytecode; exclude from canonical source, retain in source history |
| `app.py` | `6d3242afb5a86cc115fef3e6944cd7b6a39030f3` | Executable web application; compare behavior, not just basename |
| `creative-generator/UltimateCreativeGenerator.kt` | `6531386f51c32457db6c348a30f1eaffda6a8c56` | Unique Android/Kotlin artifact |
| `integrated/ps_t/canonical_engine.py` | `a52ea135755e3b31f804134cb53d1e0d525e4c69` | Variant/contract source; not byte-identical to Unified copy |
| `integrated/ps_t/canonical_weights.json` | `5a6cfef3cc40ff8eef6ce95eaafd9ab4247cb4f3` | Model configuration lineage |
| `integrated/ps_t/test_canonical_engine.py` | `8f4ce9a531c2e1faf5294484ea959f821678b069` | Test source; compare contract semantics |
| `mobile/app/src/main/kotlin/com/hamidcognition/main/MainActivity.kt` | `03621ef98aaa0d4bcfed7987dfead43b82aadac3` | Unique Android application source |
| `requirements.txt` | `72b5fc9cf0940c8a8aed3c93ee5acd478b612217` | Runtime dependencies |

Several shared core/model/feed/template files have exact integrated blobs, but the unique mobile and creative-generator artifacts block an unqualified “fully migrated” claim.

## Disposition rule

All entries above remain **UNRESOLVED for archive purposes** until each receives a durable label:
- `MIGRATED_EXACT` with a matching target path/blob;
- `MIGRATED_CHANGED` with a behavior-preservation test;
- `HISTORICAL_ONLY` with a reason and preserved source history;
- `GENERATED_OR_TRANSIENT` with rationale; or
- `UNRESOLVED`, which blocks archive.

No source repository is deleted by this process. A successful file inventory is not a runtime test.
