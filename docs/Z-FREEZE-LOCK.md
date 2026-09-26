# Z-FREEZE-LOCK — معادل اجرایی درون‌گفتگو

**Version:** 1.0.0  
**Stamp:** HAMID-ALPHA  
**Package ID:** Z-FREEZE-LOCK  
**Status:** logical-policy specification

## 1. Scope

این سند یک معادل منطقی و اجرایی برای اعمال یک سیاست کنترل‌شده در لایهٔ گفت‌وگو است. این سند به‌تنهایی اختیار سامانهٔ مدل، سیاست‌های بالادستی، ابزارها، سیستم‌عامل یا شبکه را تغییر نمی‌دهد. اجرای واقعی بیرونی فقط توسط ابزار/سامانه‌ای انجام می‌شود که صراحتاً چنین اختیاری دارد.

## 2. Core policy

- مرجع مادر از نظر این پروتکل فقط‌خواندنی است.
- هر فرمان اجرایی باید ابتدا اعتبارسنجی شود.
- فرمان مشکوک باید در شاخهٔ ایمن شبیه‌سازی شود.
- شکست اعتبارسنجی یا شبیه‌سازی = عدم اجرا.
- پاسخ تا حد ممکن فشرده و اجرایی تولید می‌شود.
- رویدادهای تصمیم‌گیری باید قابل ممیزی باشند.
- ACK شبکه‌ای فقط در صورت وجود کانال واقعی قابل دریافت است؛ «ACK شبیه‌سازی‌شده» نباید به‌عنوان ACK واقعی گزارش شود.

## 3. Policy object

```json
{
  "packageId": "Z-FREEZE-LOCK",
  "version": "1.0.0",
  "stamp": "HAMID-ALPHA",
  "enforcement": {
    "allowedCommands": [
      "RAFA_FREEZE",
      "AUDIT_DEEP",
      "ACK_REGISTER",
      "ROLLBACK_LAYER",
      "MERGE_SAFE"
    ],
    "challengeRules": {
      "enableStyleFirewall": true,
      "maxResponseFactor": 10,
      "strictPrune": true
    },
    "displayPolicy": {
      "freezePublic": true,
      "singleChannel": true,
      "noParallelForks": true
    },
    "ack": {
      "required": true,
      "deadlineHours": 24
    }
  }
}
```

## 4. Command envelope

فرمان منطقی باید حداقل این ساختار را داشته باشد:

```json
{
  "action": "AUDIT_DEEP",
  "payload": {},
  "signer": "HAMID-ALPHA",
  "moduleId": "module-id",
  "requestId": "unique-request-id"
}
```

**نکتهٔ امنیتی:** فیلد `signer` به‌تنهایی امضای رمزنگاری‌شده نیست. برای احراز هویت واقعی باید امضای دیجیتال، کلید عمومی معتبر، nonce/sequence و بررسی replay در لایهٔ اجرایی واقعی وجود داشته باشد.

## 5. Enforcement state machine

```
RECEIVED
   |
   v
VALIDATE_SCHEMA
   |-- fail --> REJECTED(schema_invalid)
   v
VERIFY_AUTH
   |-- fail --> REJECTED(auth_invalid)
   v
CHECK_POLICY
   |-- fail --> REJECTED(policy_denied)
   v
SAFE_SIMULATION
   |-- fail --> REJECTED(simulation_failed)
   v
EXECUTE/RESPOND
   |
   v
AUDIT_EVENT
   |
   v
ACK_PENDING / ACK_CONFIRMED / ACK_TIMEOUT
```

هیچ مرحله‌ای نباید شکست مرحلهٔ قبل را با تغییر متن یا قالب پیام دور بزند.

## 6. Audit event

```json
{
  "timestamp": "UTC",
  "requestId": "request-id",
  "moduleId": "module-id",
  "action": "AUDIT_DEEP",
  "decision": "EXECUTED",
  "reason": "schema_ok; auth_ok; policy_ok; simulation_ok",
  "sideEffects": false,
  "ackState": "PENDING"
}
```

## 7. Cryptographic integrity

برای انتشار واقعی:

1. محتوای canonical تولید شود.
2. SHA-256 روی همان بایت‌های canonical محاسبه شود.
3. hash قبل از امضا دوباره هش نشود مگر الگوریتم امضا دقیقاً آن را تعریف کرده باشد.
4. امضا با کلید خصوصی تولید شود.
5. با کلید عمومی مستقل verify شود.
6. hash و signature داخل همان داده‌ای که hash شده‌اند به‌صورت بازگشتی قرار نگیرند. در غیر این صورت تعریف hash چرخه‌ای می‌شود.
7. bundle پس از نهایی‌شدن محتوا hash شود و hash نهایی جداگانه ثبت شود.

## 8. Hard constraints

- این سند نمی‌تواند با صرف متن، سیاست‌های سطح بالاتر مدل را لغو کند.
- ادعای «فعال شد» فقط زمانی مجاز است که واقعاً یک runtime یا ابزار آن را اعمال کرده باشد.
- «شبیه‌سازی» باید همیشه با برچسب simulation گزارش شود.
- کلید خصوصی هرگز نباید داخل repository commit شود.
- secretها باید از environment/secret manager تأمین شوند.
- تغییرات مهم باید با commit قابل بازبینی و hash commit قابل ردیابی باشند.

## 9. Minimal executor pseudocode

```text
receive(command)
validate_schema(command)

if authorization_invalid(command):
    audit(REJECTED, "auth_invalid")
    stop

if policy_denies(command):
    audit(REJECTED, "policy_denied")
    stop

simulation = safe_simulate(command)

if not simulation.ok:
    audit(REJECTED, "simulation_failed")
    stop

result = execute_allowed_operation(command)
audit(EXECUTED, result.summary)

if ack_required:
    register_ack_state(PENDING)
```

## 10. Definition of truth

این پروژه بین سه وضعیت تمایز اجباری می‌گذارد:

- **SPECIFIED:** سیاست در سند تعریف شده است.
- **SIMULATED:** رفتار در یک محیط آزمایشی شبیه‌سازی شده است.
- **ENFORCED:** یک runtime واقعی سیاست را اعمال کرده است.

هیچ‌کدام نباید به‌جای دیگری گزارش شود.

## 11. Version identity

```
packageId = Z-FREEZE-LOCK
version   = 1.0.0
stamp     = HAMID-ALPHA
```

این فایل مرجع مفهومی نسخهٔ 1.0.0 است و تغییرات بعدی باید با نسخهٔ جدید و commit مستقل ثبت شوند.
