# Reproducibility Standard

## Minimum reproducibility record

برای هر نتیجه مهم، حداقل این زنجیره باید قابل پیگیری باشد:

`source → dataset snapshot → preprocessing → parameters → seed → code commit → environment → execution → output → analysis → claim`

## Reproducibility levels

### R0 — Narrative
نتیجه فقط توصیفی است و اجرای دقیق قابل بازسازی نیست.

### R1 — Artifact
کد یا artifact موجود است، اما داده/محیط/پارامتر کامل نیست.

### R2 — Re-runnable
اجرای مجدد با مشخصات کافی امکان‌پذیر است.

### R3 — Independently reproduced
فرد یا محیط مستقل نتیجه را با همان پروتکل بازتولید کرده است.

### R4 — Stress-tested
نتیجه علاوه بر reproduction، در آزمون‌های sensitivity، ablation، boundary و falsification نیز پایدار مانده است.

## Rule

سطح reproducibility بخشی از ادعای نتیجه است، نه یک تزئین مستنداتی.
