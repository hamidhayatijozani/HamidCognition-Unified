# Experiment Fingerprint Specification

## Purpose

یک آزمایش زمانی قابل بازسازی‌تر است که تفاوت میان داده، کد، پارامتر و محیط قابل تشخیص باشد.

## Required fields

```yaml
experiment_id: EXP-YYYYMMDD-NNN
claim_ids: []
dataset:
  source: ""
  version: ""
  snapshot: ""
preprocessing:
  description: ""
parameters: {}
seed: null
code:
  repository: ""
  commit: ""
environment:
  runtime: ""
  dependencies: []
execution:
  started_at: ""
  finished_at: ""
outputs:
  artifact_paths: []
  hashes: []
result:
  observation: ""
  status: UNKNOWN
```

## Rule

اگر یک field حیاتی نامعلوم باشد، آن missingness باید در گزارش نتیجه آشکار بماند و نباید با مقدار حدسی جایگزین شود.
