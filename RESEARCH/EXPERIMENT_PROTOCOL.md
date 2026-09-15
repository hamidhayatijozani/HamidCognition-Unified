# HamidCognition Unified — Experiment Protocol

## هدف
هیچ ایده مهمی بدون مسیر آزمون وارد معماری اصلی نشود.

## Experiment record
هر آزمایش باید ثبت کند:
- hypothesis
- null hypothesis
- exact implementation/version
- source commit
- dataset/input provenance
- parameters
- random seed
- environment/dependencies
- preprocessing
- train/test split or temporal split
- baseline
- primary metric
- secondary metrics
- preregistered threshold if applicable
- expected failure condition
- actual result
- interpretation
- limitations
- reproducibility instructions

## Comparative model protocol
برای مقایسه engineها:
- identical input vectors
- identical initial state where meaningful
- deterministic timestamp handling
- identical step sequence
- compare trajectory, phase, energy, bounds, bias and failure behavior

برای predictorها:
- same dataset
- same horizon
- temporal/walk-forward evaluation
- naive baseline
- leakage audit
- repeated windows/seeds where applicable
- error distribution, not only average score
- stability under regime change

## Falsification priority
اول باید شرایطی را آزمایش کرد که احتمال شکست hypothesis در آن بالاست. انتخاب benchmark صرفاً برای گرفتن عدد بهتر ممنوع است.

## Result classes
- SUPPORTED: شواهد با فرضیه سازگار است، بدون اثبات قطعی.
- WEAK_SUPPORT: اثر کوچک/ناپایدار یا حساس به protocol.
- INCONCLUSIVE: داده برای تصمیم کافی نیست.
- FALSIFIED: نتیجه با پیش‌بینی قابل آزمون فرضیه ناسازگار است.
- INVALID_EXPERIMENT: protocol دارای خطای بنیادی است.

## Anti-overclaim rule
نتیجه آزمایش فقط همان ادعایی را پشتیبانی می‌کند که طراحی آزمایش قادر به آزمون آن بوده است.
