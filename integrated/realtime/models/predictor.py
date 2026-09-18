"""
مدل پیش‌بینی قیمت با استفاده از LSTM و ترکیب با موتور شناختی
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LinearRegression
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import pickle
import os


class ForexPredictor:
    """
    پیش‌بینی‌کننده قیمت فارکس
    استفاده از رگرسیون خطی + تحلیل روند + موتور شناختی
    """
    
    def __init__(self, window_size=60):
        self.window_size = window_size
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = LinearRegression()
        self.is_trained = False
        self.last_training_time = None
        
    def prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """آماده‌سازی ویژگی‌ها برای مدل"""
        if len(data) < self.window_size:
            return None
        
        # استفاده از قیمت بسته شدن
        prices = data['Close'].values[-self.window_size:]
        
        # نرمال‌سازی
        prices_normalized = self.scaler.fit_transform(prices.reshape(-1, 1))
        
        # ساخت ویژگی‌های زمانی
        X = np.arange(len(prices_normalized)).reshape(-1, 1)
        y = prices_normalized.flatten()
        
        return X, y, prices[-1]
    
    def train(self, data: pd.DataFrame) -> bool:
        """آموزش مدل با داده‌های تاریخی"""
        try:
            result = self.prepare_features(data)
            if result is None:
                return False
            
            X, y, _ = result
            self.model.fit(X, y)
            self.is_trained = True
            self.last_training_time = datetime.now()
            return True
        except Exception as e:
            print(f"❌ خطا در آموزش مدل: {e}")
            return False
    
    def predict_future(
        self, 
        current_price: float,
        data: pd.DataFrame,
        minutes: List[int] = [5, 10, 20],
        cognitive_bias: float = 0.0
    ) -> List[Dict]:
        """
        پیش‌بینی قیمت برای دقایق آینده
        
        Args:
            current_price: قیمت فعلی
            data: داده‌های تاریخی
            minutes: لیست دقایق برای پیش‌بینی
            cognitive_bias: bias از موتور شناختی (-1 تا 1)
        """
        predictions = []
        
        # اگر مدل آموزش ندیده، ابتدا آموزش بده
        if not self.is_trained:
            self.train(data)
        
        # محاسبه روند
        if len(data) >= 20:
            recent_prices = data['Close'].values[-20:]
            X_trend = np.arange(len(recent_prices)).reshape(-1, 1)
            y_trend = recent_prices
            
            trend_model = LinearRegression()
            trend_model.fit(X_trend, y_trend)
            slope = trend_model.coef_[0]
        else:
            slope = 0.0
        
        # محاسبه نوسان
        if len(data) >= 20:
            returns = data['Close'].pct_change().dropna()
            volatility = returns.std()
        else:
            volatility = 0.001
        
        # پیش‌بینی برای هر بازه زمانی
        for minute in minutes:
            # پیش‌بینی پایه بر اساس روند
            base_change = slope * minute
            
            # تعدیل با bias شناختی
            cognitive_adjustment = cognitive_bias * volatility * current_price * 0.5
            
            # پیش‌بینی نهایی
            predicted_price = current_price + base_change + cognitive_adjustment
            
            # محاسبه بازه اطمینان
            confidence_interval = volatility * current_price * np.sqrt(minute / 60)
            upper_bound = predicted_price + confidence_interval
            lower_bound = predicted_price - confidence_interval
            
            # تعیین جهت
            direction = "UP 🟢" if predicted_price > current_price else "DOWN 🔴"
            if abs(predicted_price - current_price) < current_price * 0.0001:
                direction = "NEUTRAL ⚪"
            
            # محاسبه اطمینان
            confidence = self._calculate_confidence(minute, volatility)
            
            predictions.append({
                "timeframe": f"+{minute} min",
                "minutes": minute,
                "forecast_price": round(predicted_price, 5),
                "range": {
                    "high": round(upper_bound, 5),
                    "low": round(lower_bound, 5)
                },
                "direction": direction,
                "confidence": round(confidence, 2),
                "change_pips": round((predicted_price - current_price) * 10000, 1)
            })
        
        return predictions
    
    def _calculate_confidence(self, minutes: int, volatility: float) -> float:
        """محاسبه سطح اطمینان پیش‌بینی"""
        # اطمینان کاهش می‌یابد با افزایش زمان و نوسان
        time_factor = 1.0 / (1.0 + minutes / 10.0)
        volatility_factor = 1.0 / (1.0 + volatility * 100)
        confidence = time_factor * volatility_factor * 100
        return min(95.0, max(30.0, confidence))
    
    def save_model(self, filepath: str):
        """ذخیره مدل"""
        try:
            with open(filepath, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'scaler': self.scaler,
                    'window_size': self.window_size,
                    'is_trained': self.is_trained
                }, f)
            return True
        except Exception as e:
            print(f"❌ خطا در ذخیره مدل: {e}")
            return False
    
    def load_model(self, filepath: str):
        """بارگذاری مدل"""
        try:
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    data = pickle.load(f)
                    self.model = data['model']
                    self.scaler = data['scaler']
                    self.window_size = data['window_size']
                    self.is_trained = data['is_trained']
                return True
        except Exception as e:
            print(f"❌ خطا در بارگذاری مدل: {e}")
        return False


class PredictionEngine:
    """موتور اصلی پیش‌بینی که همه چیز را ترکیب می‌کند"""
    
    def __init__(self, predictor: ForexPredictor, cognition):
        self.predictor = predictor
        self.cognition = cognition
        
    def generate_predictions(
        self,
        current_price: float,
        historical_data: pd.DataFrame,
        market_context: Dict[str, float]
    ) -> Dict:
        """تولید پیش‌بینی‌های کامل"""
        
        # به‌روزرسانی موتور شناختی
        self.cognition.update(market_context)
        
        # دریافت bias شناختی
        cognitive_bias = self.cognition.get_decision_bias()
        
        # تولید پیش‌بینی‌ها
        predictions = self.predictor.predict_future(
            current_price=current_price,
            data=historical_data,
            minutes=[5, 10, 20],
            cognitive_bias=cognitive_bias
        )
        
        # دریافت وضعیت شناختی
        cognitive_state = self.cognition.get_state()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "current_price": current_price,
            "predictions": predictions,
            "cognitive_state": cognitive_state,
            "market_context": market_context
        }
