# HamidCognition Unified — Phase 0 Inventory

Status: **INVENTORY IN PROGRESS — NO MERGE PERFORMED**

Generated from direct GitHub repository inspection. This document records observed repository state only. It does not declare a canonical implementation.

## Target repository

- Repository: `hamidhayatijozani/HamidCognition-Unified`
- ID: `1371234221`
- Default branch: `main`
- Visibility: public
- Observed repository size: 0 before migration metadata
- Prior observed content: `README.md` only

## Source repositories

| Repository | Default branch | GitHub size | Observed role | Phase-0 status |
|---|---|---:|---|---|
| `hamidhayatijozani/hamidcognition-complete` | `main` | 24 | multi-component Python/platform repository | inspected |
| `hamidhayatijozani/hamidcognition-realtime` | `main` | 18 | real-time platform + ML/P-S-T | inspected |
| `hamidhayatijozani/hamidcognition-web` | `main` | 5 | Flask web application | inspected |
| `hamidhayatijozani/hamidcognition-v0-max` | `main` | 23 | earlier/max variant with core/API/data/UI | inspected |
| `hamidhayatijozani/HamidCognition` | `master` | 31 | standalone cognition + EUR/USD experiments/reports | inspected |
| `hamidhayatijozani/HamidCognitionEngine` | `master` | 13 | standalone cognition/trading engine | inspected |

## Confirmed file/component observations

### hamidcognition-complete

Observed root components include:
- `app.py`
- `config.py`
- `main.py`
- `market_feed.py`
- `model.py`
- `requirements.txt`
- `Procfile`
- `core/`
- `mobile/`
- `creative-generator/`
- `templates/`
- `__pycache__/`

Observed `core/` contains `core/hamid_cognition.py` (2840 bytes) plus `__pycache__/`.

Latest observed commit:
- SHA: `f15508f00c9d6c9087aaf766fd201181d1de8232`
- Date: `2025-12-26T22:47:20Z`
- Message: `🧹 Clean & Simple: Root-level deployment ready`

### hamidcognition-realtime

Observed root components include:
- `app.py`
- `README.md`
- `requirements.txt`
- `api/`
- `core/`
- `models/`
- `ui/`
- `.gitignore`

Observed `core/` contains:
- `core/__init__.py`
- `core/hamid_cognition.py` (5626 bytes)

Latest/only observed commit:
- SHA: `a8bc3bce0b619ec2009a554e816fe8df5b4e8003`
- Date: `2025-12-26T22:20:47Z`
- Message: `🚀 Initial commit: HamidCognition Real-Time Platform with ML prediction and P/S/T cognitive engine`

### hamidcognition-web

Observed root components:
- `app.py`
- `requirements.txt`
- `templates/`
- `README.md`
- `.gitignore`

No P/S/T core file has been established from the root inventory yet.

### hamidcognition-v0-max

Observed root components include:
- `config.py`
- `main.py`
- `README.md`
- `api/`
- `core/`
- `data/`
- `ui/`
- `.github/`
- `__pycache__/`

Notably, `config.py` has the same blob SHA observed in `hamidcognition-complete` (`7317d096ebb0ee39fd0621e3259463a25cbda82c`). This is evidence of identical file content, not yet proof of identical repository history.

### HamidCognition

Observed root contains multiple cognition/forex artifacts, including:
- `hamid_cognition_engine.py` (9464 bytes)
- `hamid_cognition_transfer.json`
- `cognitive_transfer_report.md`
- `eurusd_engine.py` (17360 bytes)
- `eurusd_engine_real.py` (18798 bytes)
- `eurusd_state.json`
- `eurusd_trade_report.json`
- `real_world_analysis_report.json`
- `run_eurusd.py`
- `run_eurusd_real.py`
- `simple_eurusd.py`
- `README.md`
- `__pycache__/`

The repository README explicitly describes `hamid_cognition_engine.py` as the complete `HamidCognition` class and simulation logic, and describes the transfer package as a transferable state/package artifact.

### HamidCognitionEngine

Observed root contains:
- `hamid_cognition_engine.py` (5964 bytes)
- `forex_trading_bot.py` (13439 bytes)
- `run_hamid.py` (7300 bytes)
- `sample_input_data.csv`
- `trade_log.json`
- `README.md`
- `android_python_guide.md`

## Initial collision signals

1. Multiple repositories contain a file named `hamid_cognition_engine.py`, but observed sizes and blob SHAs differ. Therefore they must be treated as separate implementations until code-level comparison proves otherwise.
2. `hamidcognition-complete/core/hamid_cognition.py` and `hamidcognition-realtime/core/hamid_cognition.py` are distinct blobs and sizes (2840 vs 5626 bytes). They are not identical files.
3. `hamidcognition-complete/requirements.txt` and `hamidcognition-realtime/requirements.txt` were observed with the same blob SHA. This strongly indicates identical dependency declarations at the observed revision.
4. `hamidcognition-complete/config.py` and `hamidcognition-v0-max/config.py` were observed with the same blob SHA. This indicates identical file content at the observed revisions.
5. `__pycache__/` directories are present in several repositories. These are generated artifacts and should not be treated as canonical source during migration.
6. `HamidCognition` contains substantially different standalone EUR/USD experiment artifacts from the platform-shaped repositories. It should not automatically be classified as a duplicate of the platform code.

## Not yet established

- Exact total file count for each repository.
- Exact total commit count for each repository except where API pagination exposed the observed commit set.
- Full dependency graph.
- Code-level equivalence of P/S/T implementations.
- Predictor equivalence/complementarity.
- Runtime/API compatibility.
- Test coverage and test validity.
- Which implementation, if any, is canonical.
- Whether historical commits should be preserved inside the unified repository or represented through provenance only.

## Phase-0 rule

**No source code has been copied, renamed, merged, deleted, or declared canonical as part of this inventory.**

The next audit layer is file-tree completion, dependency extraction, code-level comparison of cognition engines, and commit/lineage mapping.