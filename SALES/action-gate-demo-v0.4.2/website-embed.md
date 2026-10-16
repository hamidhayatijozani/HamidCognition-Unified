# قراردادن دموی Action Gate در وب‌سایت

فایل MP4 و پوستر را در پوشهٔ رسانه‌های وب‌سایت بارگذاری کنید و مسیرها را در snippet زیر جایگزین کنید:

```html
<video
  class="action-gate-demo"
  autoplay
  muted
  loop
  playsinline
  preload="metadata"
  poster="/media/action-gate-demo-poster.jpg"
  aria-label="30-second illustrative simulation of Action Gate v0.4.2 local HTTP and MCP integration tests"
>
  <source src="/media/action-gate-demo-30s.mp4" type="video/mp4" />
</video>
```

```css
.action-gate-demo {
  display: block;
  width: 100%;
  height: auto;
  border-radius: 16px;
}
```

برچسب‌های `ILLUSTRATIVE SIMULATION` و `LOCAL TEST RESULTS` در خود ویدیو عمداً باقی مانده‌اند تا رابط بازسازی‌شده با اجرای زنده یا استقرار مشتری اشتباه نشود.
