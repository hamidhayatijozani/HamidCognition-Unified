# HamidCognition-Unified

🧠 **HamidCognition Unified**  
یک برنامه پژوهشی و مهندسی برای بررسی حالت‌های شناختی، تصمیم‌گیری مبتنی بر شواهد، حاکمیت تصمیم، انتقال وضعیت رفتاری، کشف فضای ناشناخته و سامانه‌های آزمایشی پیش‌بینی.

**Originator:** Hamid Hayati Jozani  
**Status:** Public research, engineering & provenance record  
**Record date:** 2026-09-15

## What this repository is

HamidCognition فقط یک مجموعه کد نیست. این مخزن باید بتواند نشان دهد یک ایده از کجا آمده، چه چیزی از آن پیاده‌سازی شده، چه چیزی فقط فرضیه است، چه چیزی شکست خورده، چه چیزی هنوز ناشناخته است و هر نتیجه دقیقاً به کدام آزمایش و نسخه متصل است.

هدف Unified بنابراین «یکسان‌سازی مصنوعی» نیست؛ هدف، ساختن یک **ردیابی قابل بازسازی از تکامل ایده تا آزمون و نتیجه** است.

## Core research lines

- **P/S/T Cognitive State Engine** — محاسبه و بررسی وضعیت شناختی و رفتارهای مشتق‌شده.
- **HHJ-CSG / Cognitive Safety Gateway** — ارزیابی و حاکمیت تصمیم پیش از اقدامات پراثر.
- **ClaimLab** — تفکیک Observation، Inference، Explanation و Ontology و کنترل overclaim.
- **LUMEN / Behavioral State Transfer** — بررسی انتقال وضعیت رفتاری در برابر بازسازی روایی.
- **KIRGANDE / Unknown-Space Explorer** — جست‌وجوی فضای ناشناخته، ناهنجاری، تناقض و ساختارهای جدید.
- **Farahoosh-Prime** — تولید، جهش، ترکیب، آزمون و ابقای نتایج توضیح‌نشده.
- **Scale-Breaking hypothesis** — آزمون وابستگی پاسخ ترمیمی به دامنه شوک.
- **Trading / EUR/USD research** — آزمایش‌های پیش‌بینی و شبیه‌سازی بازار با تفکیک صریح simulation از شواهد live.

## The research loop

```text
IDEA
  ↓
CLAIM / HYPOTHESIS
  ↓
OPERATIONALIZATION
  ↓
EXPERIMENT
  ↓
OBSERVATION
  ↓
FALSIFICATION / SURVIVAL
  ↓
REPRODUCTION
  ↓
STATUS TRANSITION
  ↓
CANONICALIZATION or ARCHIVE
```

هیچ مرحله‌ای مجاز نیست نتیجه مرحله بعد را از قبل فرض کند.

## Epistemic status

هر ادعا یا artifact، در صورت امکان، با یکی از این وضعیت‌ها ثبت می‌شود:

`VERIFIED` · `IMPLEMENTED` · `HYPOTHESIS` · `UNKNOWN` · `FALSIFIED` · `SUPERSEDED`

وجود کد، commit، benchmark یا نام پروژه به‌تنهایی اثبات علمی یک ادعا نیست.

## New research infrastructure

این نسخه از Unified علاوه بر آرشیو پروژه، یک لایه پژوهشی برای جلوگیری از گم‌شدن شکست‌ها و ادعاهای بدون پشتوانه تعریف می‌کند:

- **Evidence-to-Claim Graph** — اتصال هر ادعا به مشاهده، داده، آزمایش، کد و commit.
- **Contradiction Ledger** — ثبت تناقض‌ها به‌عنوان داده پژوهشی، نه خطایی که باید پنهان شود.
- **Unknown-Space Ledger** — نگهداری پرسش‌ها و رفتارهای توضیح‌نشده بدون مجبورکردن آنها به یک نظریه.
- **Experiment Fingerprint** — شناسه بازسازی‌پذیر برای داده، seed، پارامتر، نسخه کد و محیط آزمایش.
- **Canonicalization Gate** — هیچ implementation صرفاً به دلیل کامل‌تر یا جدیدتر بودن canonical نمی‌شود.
- **Claim Strength Gate** — شدت ادعا نباید از قدرت evidence فراتر برود.
- **Provenance Seal** — اتصال نسخه پژوهشی به commit و release برای جلوگیری از ابهام درباره اینکه «کدام نسخه» مورد استناد بوده است.
- **Mutation / Falsification Lab** — تغییر کنترل‌شده فرضیات برای تلاش فعالانه جهت شکست مدل.

جزئیات در `RESEARCH/INNOVATION_ARCHITECTURE.md` ثبت شده است.

## Project lineage

`PROJECT_CATALOG.md` رابطه خطوط پژوهشی و مخازن پیشین را نگه می‌دارد. `MIGRATION/` برای ثبت lineage، تضادها، تصمیم‌های ادغام و مواردی است که عمداً حذف یا canonical نشده‌اند.

## Provenance & rights

این مخزن یک رکورد عمومی provenance و انتساب است. برای مالکیت، نحوه ارجاع و وضعیت حقوقی به `RIGHTS_AND_PROVENANCE.md` و `CITATION.cff` مراجعه کنید.

**Copyright © 2026 Hamid Hayati Jozani. All rights reserved.**

عمومی بودن مخزن به‌تنهایی به معنی اعطای مجوز عمومی برای بازتولید، تغییر، توزیع یا تجاری‌سازی نیست.

## Reproducibility principle

هر نتیجه مهم باید، در حد امکان، به این موارد متصل شود:

`dataset → preprocessing → parameters → seed → code version → environment → execution → observation → analysis → claim`

اگر یکی از این زنجیره‌ها نامعلوم باشد، سطح قطعیت نتیجه باید متناسب با همان عدم‌قطعیت کاهش یابد.

## Project documentation

- `PROJECT_CATALOG.md` — کاتالوگ رسمی خطوط پروژه
- `RIGHTS_AND_PROVENANCE.md` — provenance، انتساب و حقوق
- `CITATION.cff` — فرمت machine-readable برای citation
- `RESEARCH/INNOVATION_ARCHITECTURE.md` — معماری پژوهشی و نوآوری‌های زیرساختی
- `RESEARCH/IDEA_REGISTRY.md` — رجیستری ایده‌ها
- `RESEARCH/RESEARCH_GRAPH.md` — گراف مفهومی و lineage
- `RESEARCH/EXPERIMENT_PROTOCOL.md` — پروتکل آزمایش
- `RESEARCH/UNKNOWN_SPACE.md` — فضای ناشناخته و پرسش‌های باز
- `RESEARCH/CANONICALIZATION_GATE.md` — معیار ارتقای implementation به canonical
- `MIGRATION/` — lineage، تضادها و تصمیم‌های ادغام

## Citation

برای ارجاع، **Hamid Hayati Jozani — HamidCognition / HamidCognition-Unified** و لینک مخزن را ذکر کنید و در صورت وجود، release/commit/DOI دقیق را نیز ثبت کنید.

## Important distinction

این مخزن هم‌زمان **research archive، engineering record و public project introduction** است. هیچ ادعای علمی، عملکردی یا نوآورانه صرفاً به دلیل حضور در این مخزن authoritative تلقی نمی‌شود؛ ادعا باید به evidence و مسیر آزمون متناظر متصل باشد.
