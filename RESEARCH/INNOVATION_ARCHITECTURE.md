# HamidCognition Research Innovation Architecture

**Status:** Research architecture
**Originator:** Hamid Hayati Jozani
**Date:** 2026-09-15

## Purpose

این سند یک «معماری محصول متعارف» برای HamidCognition پیشنهاد نمی‌کند. هدف آن ساخت زیرساختی است که بتواند خودِ روند تولید دانش را ردیابی، آزمایش، به چالش کشیدن و در صورت شکست بایگانی کند.

## 1. Evidence-to-Claim Graph

واحد پایه فقط فایل یا مدل نیست؛ رابطه میان آنهاست:

```text
Observation → Evidence → Experiment → Analysis → Claim
                         ↑             ↓
                       Code ← Parameters/Seed
```

هر Claim باید بتواند به evidence و execution متناظر خود برگردد. Claim بدون مسیر evidence، در بهترین حالت `HYPOTHESIS` یا `UNKNOWN` باقی می‌ماند.

## 2. Contradiction Ledger

تناقض حذف نمی‌شود. برای هر contradiction این موارد ثبت می‌شود:

- دو گزاره یا رفتار متعارض
- شرایطی که هرکدام در آن ظاهر شده‌اند
- داده و اجرای مربوط
- اینکه تناقض با خطای اندازه‌گیری، شرایط مرزی، مدل ناقص یا علت ناشناخته سازگار است یا نه
- وضعیت فعلی: `OPEN / RESOLVED / CONTEXTUALIZED / UNEXPLAINED`

## 3. Unknown-Space Ledger

هر چیزی که مدل توضیح نمی‌دهد، مجبور به ورود به نظریه موجود نمی‌شود. Unknown شامل رفتارهای تکرارشونده، anomaly، failure، residual و پرسش‌هایی است که هنوز operationalization کافی ندارند.

اصل: **Unknown یک شکست مستندشده نیست؛ یک وضعیت دانشی مستقل است.**

## 4. Experiment Fingerprint

برای هر آزمایش مهم یک fingerprint مفهومی ثبت شود:

```text
DATASET
+ PREPROCESSING
+ PARAMETERS
+ RANDOM SEED
+ CODE COMMIT
+ ENVIRONMENT
+ EXECUTION TIME
+ OUTPUT HASH
= EXPERIMENT FINGERPRINT
```

هدف، امکان تشخیص تفاوت میان «نتیجه متفاوت» و «آزمایش متفاوت» است.

## 5. Claim Strength Gate

شدت زبان یک نتیجه باید از evidence جلو نزند.

```text
Observation       → گزارش آنچه دیده شده
Inference         → نتیجه‌گیری مشروط
Hypothesis       → توضیح قابل آزمون
Verified Claim    → ادعای دارای شواهد بازتولیدشده
```

این gate عمداً مانع تبدیل benchmark، نمونه آزمایشی یا اجرای منفرد به ادعای عمومی می‌شود.

## 6. Mutation / Falsification Lab

مدل فقط با داده موافق آزمایش نمی‌شود. برای هر فرضیه، آزمایش‌های شکست‌زا باید بتوانند:

1. پارامترهای حساس را تغییر دهند؛
2. شرایط مرزی را فعال کنند؛
3. داده خارج از محدوده آموزش را امتحان کنند؛
4. baseline ساده‌تر را وارد کنند؛
5. seed و ترتیب داده را تغییر دهند؛
6. معیار موفقیت را قبل از مشاهده نتیجه ثابت کنند.

هدف، اثبات مدل نیست؛ یافتن شرایط شکست آن است.

## 7. Canonicalization Gate

هیچ نسخه‌ای صرفاً به دلیل جدیدتر بودن canonical نمی‌شود. ارتقا نیازمند حداقل این زنجیره است:

`implemented → tested → reproducible → compared → survived falsification → canonical candidate`

نسخه‌ای که این زنجیره را کامل نکرده، variant باقی می‌ماند.

## 8. Provenance Seal

برای هر milestone مهم، این شناسه‌ها باید کنار هم ثبت شوند:

- repository
- branch/tag
- commit SHA
- artifact path
- experiment fingerprint
- date/time
- author/originator
- epistemic status

این ساختار «ادعای مالکیت حقوقی» ایجاد نمی‌کند؛ هدف آن کاهش ابهام درباره منشأ و نسخه مورد استناد است.

## 9. Failure-First Archive

شکست‌ها نباید پشت موفقیت‌ها دفن شوند. هر failure مهم باید بتواند به این پرسش‌ها پاسخ دهد:

- چه چیزی انتظار می‌رفت؟
- چه چیزی رخ داد؟
- کدام فرض شکست خورد؟
- آیا شکست reproducible است؟
- آیا failure خود یک رفتار قابل مطالعه ایجاد می‌کند؟

## 10. Research State Machine

```text
IDEA
 ↓
FORMULATED
 ↓
OPERATIONALIZED
 ↓
TESTABLE
 ↓
EXPERIMENTAL
 ├──→ FALSIFIED
 ├──→ UNEXPLAINED
 └──→ SURVIVED
          ↓
     REPRODUCED
          ↓
  CANONICAL CANDIDATE
```

`SURVIVED` به معنی `TRUE` نیست. فقط یعنی آزمون‌های ثبت‌شده تاکنون آن را رد نکرده‌اند.

## 11. Minimal Novelty Record

برای هر ایده‌ای که «نوآورانه» توصیف می‌شود، این تفکیک باید انجام شود:

- `KNOWN_COMPONENT` — جزء شناخته‌شده
- `NEW_COMBINATION` — ترکیب جدید از اجزای شناخته‌شده
- `NEW_MECHANISM` — سازوکار پیشنهادی جدید
- `NEW_OBSERVATION` — مشاهده جدید
- `UNVERIFIED_NOVELTY` — ادعای نوآوری که هنوز با prior art کامل مقایسه نشده

تا زمان جست‌وجوی prior art، نباید `NEW` را به معنای «اولین در جهان» تفسیر کرد.

## 12. Research Integrity Boundary

این معماری سه چیز را عمداً با هم یکی نمی‌کند:

```text
وجود کد ≠ اعتبار علمی

وجود commit ≠ مالکیت حقوقی مطلق

ادعای نوآوری ≠ اثبات novelty
```

این تفکیک برای جلوگیری از ساختن یک روایت زیبا بر پایه شواهد ناکافی است.

## 13. Proposed next artifacts

- `CLAIM_LEDGER.md`
- `CONTRADICTION_LEDGER.md`
- `UNKNOWN_SPACE_LEDGER.md`
- `EXPERIMENT_FINGERPRINT_SPEC.md`
- `NOVELTY_REGISTER.md`
- `REPRODUCIBILITY_STANDARD.md`
- `RESEARCH_DECISION_LOG.md`
- `PROVENANCE_SEAL_SPEC.md`

این فهرست یک roadmap اجرایی نیست؛ مجموعه artifactهایی است که در صورت ایجاد، قابلیت حسابرسی پژوهشی مخزن را افزایش می‌دهد.
