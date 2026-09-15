# HamidCognition Unified — Idea & Hypothesis Registry

## Purpose
این سند حافظه پژوهشی پروژه است. ایده‌ها، فرضیه‌ها، prototypeها، شواهد، تناقض‌ها و unknownها را ثبت می‌کند تا هیچ مفهوم مهمی به دلیل تغییر کد یا تغییر مسیر گفتگو از بین نرود.

## Epistemic classes
- VERIFIED: با اجرای قابل بازتولید یا شواهد مستقیم پشتیبانی شده.
- IMPLEMENTED: در کد وجود دارد، اما اعتبار عملکردی/علمی کامل اثبات نشده.
- HYPOTHESIS: ادعای قابل آزمون و ابطال.
- UNKNOWN: هنوز سؤال/فضای اکتشافی است و ادعای نتیجه ندارد.
- FALSIFIED: آزمون مشخص آن را رد کرده است.
- SUPERSEDED: نسخه یا مدل جدید جایگزین شده، بدون اینکه الزاماً نسخه قبلی نادرست باشد.

## Core research lines

### HC-001 — P/S/T Cognitive State Engine
Status: IMPLEMENTED / competing variants.
موضوع: state vector شامل P/S/T، phase، energy و decision bias.
اصل: هیچ implementation صرفاً به‌خاطر قدیمی‌تر یا پیچیده‌تر بودن canonical نمی‌شود.
آزمون بعدی: conformance vectors، trajectory comparison، invariant checks، boundary/failure tests.

### HC-002 — Cognitive Safety Gateway / HHJ-CSG
Status: IMPLEMENTED / research architecture.
موضوع: ارزیابی permission_request قبل از high-impact tool execution با خروجی ALLOW, DENY, ASK, SANDBOX, DEFER.
مفاهیم وابسته: Decision Object/ODA، evidence coverage، replay، provenance، fail-closed، claim classification.
اصل: safety claim فقط زمانی معتبر است که bypass، degraded mode، replay divergence و evidence gaps آزمایش شوند.

### HC-003 — ClaimLab
Status: RESEARCH.
طبقه‌بندی Claim: Observation / Inference / Explanation / Ontology.
مکانیسم‌های هدف: OVERCLAIM، confidence-evidence gap، verdictهای VALID/WEAK/INVALID.
سؤال کلیدی: آیا سیستم می‌تواند ادعای خود را از شواهدش جدا نگه دارد؟

### HC-004 — LUMEN / Behavioral State Transfer
Status: HYPOTHESIS / EXPERIMENTAL.
موضوع: انتقال حالت رفتاری/اپیستمیک بین اجراها و آزمون اینکه state قابل انتقال است یا فقط narrative reconstruction رخ می‌دهد.
خطر: narrative-lock و attribution بدون شواهد کافی.
آزمون: state vector، anchors، A/B transfer، blind evaluation و falsification.

### HC-005 — KIRGANDE / Unknown-Space Explorer
Status: RESEARCH.
هدف: سیستم فقط architecture موجود را تکرار نکند؛ primitive تولید کند، mutation/recombination انجام دهد، anomaly کشف کند، فرضیه بسازد و آن را ابطال کند.
اصل: unknown space باید artifact داشته باشد، نه صرفاً زبان شاعرانه.

### HC-006 — Farahoosh-Prime
Status: RESEARCH.
ایده: architecture factory به‌جای ساخت مستقیم، به سمت experiment engine حرکت کند: seeds → generation → mutation → recombination → experiment → anomaly → falsification → archive.
معیار موفقیت: کشف قابل تکرار چیزی که قبل از جست‌وجو به‌صورت دستی تعریف نشده بود.

### HC-007 — Scale-Breaking / Amplitude-Dependent Recovery
Status: HYPOTHESIS.
فرض: در برخی سیستم‌ها restoring force ممکن است تابع دامنه shock باشد و پاسخ normalized نسبت به amplitude invariant نباشد.
آزمون: freeze نتایج قبلی، seed/parameters/code version، x(t;A)، deviation(t;A)، normalized deviation، threshold preregistration و sensitivity analysis.
Recovery Time به‌تنهایی outcome اصلی نیست.

### HC-008 — Trading Cognitive Loop
Status: IMPLEMENTED / UNVALIDATED.
اجزا: Thoth، Maat، Void Simulator، market stream، cognition state و execution simulation.
اصل: simulated execution نباید به‌عنوان live trading evidence ثبت شود.

### HC-009 — EUR/USD Short-Horizon Research
Status: IMPLEMENTED / EXPERIMENTAL.
دامنه: M1/M5، horizon کوتاه، ATR14، RSI14، EMA20/50، support/resistance، tick speed و news context در صورت وجود.
اولویت: simulator/backtest قبل از live execution.

### HC-010 — Evidence-First Metrics
Status: RESEARCH.
مفاهیم: NED، HAIS، DRS، EAS، CPS، CQM، OCR و evidence coverage.
اصل: metric باید operational definition، dataset، sampling protocol، baseline و failure interpretation داشته باشد.

### HC-011 — Replay / Provenance / Behavioral Integrity
Status: RESEARCH / PARTIAL IMPLEMENTATION.
هدف: بازاجرای یک تصمیم با ورودی، نسخه، state و policy مشابه و اندازه‌گیری divergence.
معیارهای پیشنهادی: replay stability، provenance completeness، fault handling، integrity و latency compliance.

### HC-012 — Degraded-Mode Cognitive Safety
Status: HYPOTHESIS.
سؤال: اگر sensor/model/evidence ناقص یا متناقض شد، سیستم چگونه باید uncertainty را به تصمیم تبدیل کند؟
مسیر آزمون: fault injection، missing evidence، stale data، contradictory observations، timeout و partial dependency failure.

### HC-013 — Common-Mode Corruption
Status: HYPOTHESIS.
سؤال: اگر تمام validators یا predictors یک منبع مشترک خطا داشته باشند، ensemble ظاهری چگونه می‌تواند شکست جمعی را پنهان کند؟
آزمون: correlated-failure scenarios و independent evidence sources.

### HC-014 — Semantic Drift / State Drift
Status: HYPOTHESIS.
سؤال: آیا معنای یک state یا metric در طول نسخه‌ها بدون تغییر schema تغییر می‌کند؟
آزمون: semantic snapshots، versioned interpretation، replay across versions و drift alerts.

## Research principles
1. Running code is evidence of execution, not evidence of correctness.
2. A named model is not necessarily the model actually implemented.
3. A benchmark number without protocol is not a benchmark claim.
4. Simulation is not live-world evidence.
5. Contradictions are first-class research objects.
6. Failed hypotheses remain archived with their falsification evidence.
7. Unknowns must be explicitly represented.
8. New architecture requires an evidence path back to source, experiment or hypothesis.
9. Canonical status is earned by conformance and reproducibility, not by naming.
10. No irreversible deletion of source history during consolidation.
