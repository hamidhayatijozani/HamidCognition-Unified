"""Static leakage audit for the recorded EUR/USD predictor source.

This intentionally does not execute the historical predictor or claim OOS skill.
It checks source-level properties that can be established without market data.
"""
from pathlib import Path

SOURCE = """import numpy as np\nfrom sklearn.preprocessing import MinMaxScaler\nfrom sklearn.linear_model import LinearRegression\n\nclass ForexPredictor:\n    def __init__(self, window_size=60):\n        self.scaler = MinMaxScaler(feature_range=(0, 1))\n        self.model = LinearRegression()\n    def prepare_features(self, data):\n        prices = data['Close'].values[-self.window_size:]\n        prices_normalized = self.scaler.fit_transform(prices.reshape(-1, 1))\n        X = np.arange(len(prices_normalized)).reshape(-1, 1)\n        y = prices_normalized.flatten()\n        return X, y, prices[-1]\n    def train(self, data):\n        result = self.prepare_features(data)\n        X, y, _ = result\n        self.model.fit(X, y)\n"""

FINDINGS = {
    "uses_linear_regression": "LinearRegression()" in SOURCE,
    "uses_lstm": "LSTM" in SOURCE,
    "fits_scaler_on_supplied_window": "fit_transform(prices" in SOURCE,
    "has_native_temporal_split": "train_test_split" in SOURCE or "TimeSeriesSplit" in SOURCE,
    "has_walk_forward_loop": "walk_forward" in SOURCE,
    "requires_external_future_target": True,
}

print({"audit": "EXP-002", "findings": FINDINGS})
assert FINDINGS["uses_linear_regression"]
assert not FINDINGS["uses_lstm"]
assert FINDINGS["fits_scaler_on_supplied_window"]
assert not FINDINGS["has_native_temporal_split"]
assert not FINDINGS["has_walk_forward_loop"]
