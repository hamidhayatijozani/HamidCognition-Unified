# Z-FREEZE-LOCK v2 — Policy Execution Contract

نسخهٔ 2.0.0، stamp: HAMID-ALPHA

## اصل مرکزی

Z-FREEZE-LOCK یک قرارداد اجرای سیاست است، نه یک prompt و نه ادعای کنترل بر مدل. هر اجرای معتبر باید از زنجیرهٔ زیر عبور کند:

`INPUT → SCHEMA → AUTH → POLICY → SAFE-SIMULATION → DECISION → AUDIT → ACK`

هیچ متن ورودی به‌تنهایی نمی‌تواند مرحله‌ای را دور بزند.

## سه وضعیت حقیقت

- `SPECIFIED`: قرارداد تعریف شده.
- `SIMULATED`: قرارداد توسط موتور آزمایشی اجرا شده.
- `ENFORCED`: یک runtime واقعی آن را enforce کرده است.

موتور این مخزن فقط زمانی `ENFORCED` صادر می‌کند که adapter اجرایی صریحاً ثبت شده باشد؛ در غیر این صورت خروجی `SIMULATED` است.

## امنیت

`signer` یک شناسه است، نه اثبات هویت. احراز هویت واقعی باید با امضای دیجیتال و کلید عمومی انجام شود. replay با `requestId` و sequence/nonce کنترل می‌شود. secret و private key هرگز در repository قرار نمی‌گیرند.

## invariantهای اصلی

1. فرمان خارج از allowlist اجرا نمی‌شود.
2. فرمان ردشده هرگز به execution نمی‌رسد.
3. simulation شکست‌خورده execution را متوقف می‌کند.
4. simulation هرگز به‌عنوان execution واقعی گزارش نمی‌شود.
5. audit event بعد از هر تصمیم تولید می‌شود.
6. ACK بدون کانال واقعی فقط `PENDING` یا `UNAVAILABLE` است.
7. policy نمی‌تواند محدودیت‌های بالادستی runtime را لغو کند.
8. دادهٔ hashشده شامل signature خودش نیست.

## قرارداد تصمیم

```json
{
  "decision": "ALLOW|DENY",
  "truthState": "SPECIFIED|SIMULATED|ENFORCED",
  "reason": "schema_ok;auth_ok;policy_ok;simulation_ok",
  "sideEffects": false,
  "auditRequired": true
}
```

این سند مرجع v2 است. فایل اجرایی `src/z_freeze_lock.py` مرجع implementation و تست‌های `tests/test_z_freeze_lock.py` مرجع رفتار قابل‌تکرار هستند.
