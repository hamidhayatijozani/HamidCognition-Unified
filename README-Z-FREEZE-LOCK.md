# Z-FREEZE-LOCK

این implementation مرز میان «متن سیاست» و «اجرای واقعی» را عمداً سخت می‌کند.

## اجرا

```bash
python -m pytest tests/test_z_freeze_lock.py
```

یا:

```bash
printf '%s\n' '{"action":"AUDIT_DEEP","payload":{},"signer":"HAMID-ALPHA","moduleId":"demo","requestId":"req-001"}' | python src/z_freeze_lock.py
```

خروجی معتبر باید `ALLOW` و `SIMULATED` باشد، نه ادعای کنترل بر خود مدل.

برای تبدیل آن به `ENFORCED` باید یک runtime خارجی، adapter احراز هویت‌شده و مجوز اجرایی واقعی وجود داشته باشد. صرف تغییر JSON یا prompt چنین اختیاری ایجاد نمی‌کند.
