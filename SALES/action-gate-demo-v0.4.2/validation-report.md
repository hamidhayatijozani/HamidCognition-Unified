# گزارش فنی دمو ۳۰ثانیه‌ای Action Gate

## نسخه و دامنه

مبنای محتوا: **Action Gate v0.4.2**، commit دقیق `6a8aa17a28ba50c73de1ba714f25bfc04e3268c9` در مخزن عمومی [HamidCognition-Unified](https://github.com/hamidhayatijozani/HamidCognition-Unified/tree/6a8aa17a28ba50c73de1ba714f25bfc04e3268c9/action_gate).

ویدیو یک **بازسازی گرافیکی/نمایشی** از مسیر تست است، نه ضبط صفحهٔ محصول یا اجرای زنده در سامانهٔ مشتری. به همین دلیل عبارت `ILLUSTRATIVE SIMULATION · LOCAL TEST RESULTS` در تمام صحنه‌ها و `TEST FIXTURES · NO CUSTOMER SYSTEM · NOT LIVE PRODUCTION DATA` در پایین تصویر درج شده است. نمونهٔ `/production/data.db` فقط مقدار آزمایشی تست است؛ هیچ فایل یا سامانهٔ production تغییر نکرده است.

## شواهدی که در این محیط اجرا شدند

- اجرای `pytest -q` روی سورس همان commit، با `TMPDIR` اختصاصی برای ساخت پایگاه دادهٔ تمیز: **۸۰ تست موفق، ۳ هشدار deprecation**.
- اجرای `enforcement_integration.py`: بنر واقعی `REAL_ENFORCEMENT_INTEGRATION_PASS` ثبت شد. assertions این تست شامل رد درخواست `delete_file` روی هدف آزمایشی production، اجرای `read_public_file` فقط پس از اتصال تصمیم به همان درخواست، ثبت وضعیت `EXECUTED`، رد replay، رد action binding ناهماهنگ، جداسازی tenant و رد دسترسی مستقیم/attestation جعلی است.
- اجرای `mcp_integration.py`: بنر واقعی `REAL_MCP_ENFORCEMENT_INTEGRATION_PASS` ثبت شد. assertions شامل رد عمل مخرب، اجرای ابزار مجاز، رد روش MCP پشتیبانی‌نشده و رد دسترسی مستقیم با attestation مفقود یا جعلی است.
- فایل‌ها و جریان‌ها در همین محیط روی loopback اجرا شدند؛ این‌ها **تست محلی با دادهٔ آزمایشی** هستند، نه customer deployment.

یک اجرای تکراری اولیهٔ pytest سه خطای idempotency به‌دلیل فایل SQLite ثابتی داشت که یکی از تست‌ها در `/tmp` می‌سازد. علت در کد تست پیدا شد؛ با `TMPDIR` تازه، اجرای مجدد کامل ۸۰ تست موفق شد. لاگ تحویل‌شده نتیجهٔ اجرای ایزولهٔ موفق را نشان می‌دهد.

در این محیط Docker نصب نبود؛ بنابراین اجرای PostgreSQL production stack و production E2E به‌صورت محلی بازتولید نشد. هرچند مستند نسخه دربارهٔ این مسیر توضیح می‌دهد، این گزارش و ویدیو آن را به‌عنوان نتیجهٔ تازهٔ این اجرا ادعا نمی‌کنند. وضعیت استقرار روی مشتری، گواهی انطباق، تأخیر/کارایی و تضمین امنیت نیز بررسی یا ادعا نشده‌اند.

## وضعیت ادعاها

| ادعا/نمایش | وضعیت | دامنه و شاهد |
|---|---|---|
| UI و دیاگرام‌های داخل ویدیو | `SIMULATED` | موشن‌گرافیک بازسازی‌شده است، نه رابط ضبط‌شدهٔ محصول. برچسب شبیه‌سازی همیشگی است. |
| رد درخواست HTTP برای عمل مخربِ نمونه | `VERIFIED` | تست integration محلی v0.4.2؛ دادهٔ آزمایشی و بدون تغییر سامانهٔ واقعی. |
| اجرای درخواست مجاز پس از bind شدن تصمیم | `VERIFIED` | تست HTTP محلی، با test tool server همان مخزن. |
| ثبت evidence، رد replay، action binding و جداسازی tenant | `VERIFIED` | assertions تست HTTP محلی همان commit. |
| رفتار مسیر MCP و رد دسترسی مستقیم جعلی/بدون مجوز | `VERIFIED` | تست MCP محلی همان commit. |
| اجرای ۸۰ تست مخزن | `VERIFIED` | `pytest -q` با `TMPDIR` مستقل؛ ۳ هشدار deprecation. |
| PostgreSQL production E2E در این نشست | `UNKNOWN` | اجرا نشد؛ Docker در محیط نصب نبود. |
| اجرای مشتری/دادهٔ مشتری/استقرار production | `UNKNOWN` | در این کار انجام یا ادعا نشد. |
| اعداد latency، مشتریان، کاهش ریسک یا تضمین امنیت | `UNKNOWN` | در ویدیو نمایش داده نشده‌اند. |

## فهرست صحنه‌ها

| زمان | نمایش |
|---|---|
| 00:00–00:05 | پرسش آغازین و درخواست آزمایشی `delete_file`. |
| 00:05–00:11 | tenant، actor، action و policy متناظر با test fixture. |
| 00:11–00:18 | دو مسیر تست‌شده: `DENY` و `ALLOW` با decision ID متصل. |
| 00:18–00:24 | اثر تصمیم روی مسیر اجرای HTTP؛ ابزار تست فقط پس از تصمیم مجاز اجرا می‌شود. |
| 00:24–00:28 | وضعیت evidence، رد replay، و نتیجهٔ تست‌های HTTP/MCP و pytest. |
| 00:28–00:30 | نام محصول، نسخه، commit، مخزن و یادآوری اینکه این استقرار مشتری نیست. |

## کنترل فایل نهایی

- نام: `action-gate-demo-30s.mp4`
- مدت: دقیقاً ۳۰٫۰۰۰ ثانیه
- تصویر: ۱۹۲۰×۱۰۸۰، ۳۰ fps، H.264، ۱۶:۹
- صدا: AAC، استریو، ۴۸ kHz؛ موسیقی بی‌کلامِ ساخته‌شده برای این ویدیو، بدون گفتار
- رمزگشایی کامل با FFmpeg انجام شد؛ اندازهٔ فایل حدود ۱٫۵ MB است.
- SHA-256: `b3252ebb1054aff77053a415d46fe545fea55c36db6f64896aca02f0350af47c`
- مسیر: `/home/ubuntu/action_gate_demo/action-gate-demo-30s.mp4`
- نسخهٔ عمودی ۹:۱۶ ساخته نشده؛ ترکیب‌بندی فنی برای ۱۶:۹ طراحی شده و برش مستقیم، متن و مسیرهای نموداری را ناخوانا می‌کرد.

## فایل‌های شاهد

- [گزارش test suite ایزوله](pytest.log)
- [خروجی تست HTTP](http-integration.log)
- [خروجی تست MCP](mcp-integration.log)
- [سورس رندر موشن‌گرافیک](render_action_gate_demo.py)

## منابع نسخه

- [README نسخهٔ v0.4.2 در commit دقیق](https://github.com/hamidhayatijozani/HamidCognition-Unified/blob/6a8aa17a28ba50c73de1ba714f25bfc04e3268c9/action_gate/README.md)
- [قرارداد آمادگی محصول](https://github.com/hamidhayatijozani/HamidCognition-Unified/blob/6a8aa17a28ba50c73de1ba714f25bfc04e3268c9/action_gate/PRODUCT_READINESS.md)
- [تست HTTP enforcement](https://github.com/hamidhayatijozani/HamidCognition-Unified/blob/6a8aa17a28ba50c73de1ba714f25bfc04e3268c9/action_gate/enforcement_integration.py)
- [تست MCP enforcement](https://github.com/hamidhayatijozani/HamidCognition-Unified/blob/6a8aa17a28ba50c73de1ba714f25bfc04e3268c9/action_gate/mcp_integration.py)
