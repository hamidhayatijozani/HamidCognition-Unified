import json
import os
import time
from datetime import datetime, timedelta

import pandas as pd
import requests

LLM_API_URL = os.getenv("LLM_API_URL")
LLM_API_KEY = os.getenv("LLM_API_KEY")
HEADERS = {"Authorization": f"Bearer {LLM_API_KEY}"} if LLM_API_KEY else {}


def fetch_rates(start_date: str, end_date: str) -> pd.DataFrame:
    url = (
        "https://api.exchangerate.host/timeseries"
        f"?start_date={start_date}&end_date={end_date}"
        "&base=USD&symbols=EUR"
    )
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()
    if not data.get("success", True):
        raise RuntimeError(f"Exchange-rate API failure: {data}")

    rows = [
        {"date": d, "close": float(v["EUR"])}
        for d, v in sorted(data["rates"].items())
        if "EUR" in v
    ]
    return pd.DataFrame(rows)


def build_prompt(historical_df: pd.DataFrame, date_reference: str) -> str:
    hist_lines = "\n".join(
        f"{row.date},{row.close:.6f}"
        for row in historical_df.itertuples(index=False)
    )
    return f"""تو یک تحلیل‌گر کمّی ساده هستی. ورودی یک جدول تاریخی نرخ USD/EUR تا تاریخ مرجع است. بر اساس فقط همین داده‌ها، نرخ بسته‌شدن روز معاملاتی بعد را پیش‌بینی کن.

خروجی دقیقاً یک خط JSON باشد:
{{"date_target":"YYYY-MM-DD","pred_close":float,"confidence":float}}

قیدها:
- pred_close فقط عدد نرخ باشد.
- confidence بین 0.0 و 1.0 باشد.
- هیچ اطلاعاتی بعد از {date_reference} استفاده نکن.
- اگر داده ناکافی یا ناپایدار است: pred_close=null و confidence=0.0.
- از متن اضافی، Markdown و code fence استفاده نکن.

DATE_REFERENCE: {date_reference}
HISTORICAL:
{hist_lines}

الان فقط JSON خروجی بده."""


def call_llm(prompt: str) -> str:
    if not LLM_API_URL:
        raise RuntimeError("LLM_API_URL is not set")

    payload = {"prompt": prompt, "max_tokens": 64, "temperature": 0.2}
    response = requests.post(
        LLM_API_URL, headers=HEADERS, json=payload, timeout=30
    )
    response.raise_for_status()
    body = response.json()
    return body.get("text") or body.get("output") or body.get("response") or response.text


def parse_json_line(text: str):
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                return None
    return None


def normalize_prediction(parsed, expected_target: str):
    if not isinstance(parsed, dict):
        return None, 0.0

    target = parsed.get("date_target")
    if target and target != expected_target:
        return None, 0.0

    pc = parsed.get("pred_close")
    try:
        conf = float(parsed.get("confidence", 0.0))
    except (TypeError, ValueError):
        conf = 0.0

    conf = min(1.0, max(0.0, conf))
    if pc is None:
        return None, 0.0

    try:
        pc = float(pc)
    except (TypeError, ValueError):
        return None, 0.0

    if not pd.notna(pc):
        return None, 0.0

    return pc, conf


def evaluate(preds_df: pd.DataFrame):
    df = preds_df.dropna(subset=["pred_close"]).copy()
    if df.empty:
        return {
            "n_predictions": 0,
            "MAE": None,
            "MAPE": None,
            "DirectionalAcc": None,
            "AvgConfidence": None,
        }

    df["abs_err"] = (df["pred_close"] - df["actual"]).abs()
    df["ape"] = df["abs_err"] / df["actual"].abs()

    df["pred_dir"] = (df["pred_close"] - df["prev"]).apply(
        lambda x: 1 if x > 0 else (0 if x == 0 else -1)
    )
    df["act_dir"] = (df["actual"] - df["prev"]).apply(
        lambda x: 1 if x > 0 else (0 if x == 0 else -1)
    )

    return {
        "n_predictions": int(len(df)),
        "MAE": float(df["abs_err"].mean()),
        "MAPE": float(df["ape"].mean()),
        "DirectionalAcc": float((df["pred_dir"] == df["act_dir"]).mean()),
        "AvgConfidence": float(df["confidence"].mean()),
    }


def run_backtest(start_date: str, end_date: str, window: int = 10):
    fetch_start = (
        datetime.fromisoformat(start_date) - timedelta(days=max(30, window * 3))
    ).date().isoformat()

    rates = fetch_rates(fetch_start, end_date)
    rates["date"] = pd.to_datetime(rates["date"]).dt.date
    rates = rates.sort_values("date").drop_duplicates("date").reset_index(drop=True)

    if len(rates) < window + 2:
        raise RuntimeError("Insufficient historical observations for requested window")

    results = []

    for idx in range(window, len(rates) - 1):
        hist = rates.iloc[idx - window : idx + 1]
        date_ref = rates.loc[idx, "date"].isoformat()
        date_target = rates.loc[idx + 1, "date"].isoformat()

        try:
            response = call_llm(build_prompt(hist, date_ref))
            parsed = parse_json_line(response or "")
            pred_close, confidence = normalize_prediction(parsed, date_target)
            raw = response
        except Exception as exc:
            pred_close, confidence = None, 0.0
            raw = str(exc)

        results.append(
            {
                "date_reference": date_ref,
                "date_target": date_target,
                "pred_close": pred_close,
                "confidence": confidence,
                "actual": float(rates.loc[idx + 1, "close"]),
                "prev": float(rates.loc[idx, "close"]),
                "raw": raw,
            }
        )
        time.sleep(0.5)

    df = pd.DataFrame(results)
    return df, evaluate(df)


if __name__ == "__main__":
    START = os.getenv("BACKTEST_START", "2025-09-01")
    END = os.getenv("BACKTEST_END", "2025-11-01")
    WINDOW = int(os.getenv("BACKTEST_WINDOW", "10"))

    predictions, metrics = run_backtest(START, END, WINDOW)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    predictions.to_csv("predictions.csv", index=False)
    print("Saved predictions.csv")
