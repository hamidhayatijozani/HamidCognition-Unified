# LLM FX Forecast Evaluation

A reproducible backtest harness for testing a large language model on one-step-ahead USD/EUR closing-rate forecasts.

For each reference date, only observations at or before that date are placed in the prompt. The next observed trading-day rate is withheld until after the prediction is recorded.

Reported metrics:
- MAE
- MAPE
- directional accuracy
- average reported confidence
- number of valid predictions

Model output contract:

{"date_target":"YYYY-MM-DD","pred_close":float,"confidence":float}

Invalid, malformed, date-mismatched, or unavailable predictions are treated as pred_close=null and confidence=0.0.

Install:

    pip install requests pandas

Configure:

    export LLM_API_URL="https://your-endpoint.example/v1/generate"
    export LLM_API_KEY="..."

Optional:

    export BACKTEST_START="2025-09-01"
    export BACKTEST_END="2025-11-01"
    export BACKTEST_WINDOW="10"

Run:

    python PROJECT/llm_fx_eval/eval_gbt_fx.py

The script writes predictions.csv.

Scientific caution: this harness tests forecasting behavior. It does not establish that an LLM possesses predictive market information. Temporal ordering and leakage controls are part of the evaluation.
