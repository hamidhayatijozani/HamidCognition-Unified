"""
ماژول دریافت داده‌های لحظه‌ای فارکس
استفاده از چندین منبع با قابلیت fallback
"""

import requests
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import time


class ForexDataProvider:
    """
    ارائه‌دهنده داده‌های فارکس با قابلیت fallback
    """
    
    def __init__(self, symbol="EURUSD", cache_duration=30):
        self.symbol = symbol
        self.cache_duration = cache_duration  # ثانیه
        self.last_fetch_time = None
        self.cached_data = None
        self.api_keys = {
            "alpha_vantage": "demo",  # کلید demo - باید جایگزین شود
        }
        
    def get_current_price(self) -> Optional[float]:
        """دریافت قیمت فعلی با استفاده از چندین منبع"""
        
        # بررسی کش
        if self._is_cache_valid():
            return self.cached_data.get("price")
        
        # تلاش برای دریافت از yfinance
        price = self._fetch_from_yfinance()
        if price:
            self._update_cache(price)
            return price
        
        # fallback به Alpha Vantage
        price = self._fetch_from_alpha_vantage()
        if price:
            self._update_cache(price)
            return price
        
        # اگر هیچ منبعی کار نکرد، از کش قدیمی استفاده کن
        if self.cached_data:
            return self.cached_data.get("price")
        
        return None
    
    def _fetch_from_yfinance(self) -> Optional[float]:
        """دریافت از yfinance"""
        try:
            ticker = yf.Ticker(f"{self.symbol}=X")
            data = ticker.history(period="1d", interval="1m")
            if len(data) > 0:
                return float(data['Close'].iloc[-1])
        except Exception as e:
            print(f"❌ خطا در yfinance: {e}")
        return None
    
    def _fetch_from_alpha_vantage(self) -> Optional[float]:
        """دریافت از Alpha Vantage"""
        try:
            api_key = self.api_keys.get("alpha_vantage")
            from_currency = self.symbol[:3]
            to_currency = self.symbol[3:]
            
            url = f"https://www.alphavantage.co/query"
            params = {
                "function": "CURRENCY_EXCHANGE_RATE",
                "from_currency": from_currency,
                "to_currency": to_currency,
                "apikey": api_key
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                rate = data.get("Realtime Currency Exchange Rate", {}).get("5. Exchange Rate")
                if rate:
                    return float(rate)
        except Exception as e:
            print(f"❌ خطا در Alpha Vantage: {e}")
        return None
    
    def get_historical_data(self, days=30, interval="1h") -> pd.DataFrame:
        """
        دریافت داده‌های تاریخی
        
        Args:
            days: تعداد روزهای گذشته
            interval: بازه زمانی (1m, 5m, 15m, 1h, 1d)
        """
        try:
            ticker = yf.Ticker(f"{self.symbol}=X")
            data = ticker.history(period=f"{days}d", interval=interval)
            return data
        except Exception as e:
            print(f"❌ خطا در دریافت داده‌های تاریخی: {e}")
            return pd.DataFrame()
    
    def compute_technical_indicators(self, data: pd.DataFrame) -> Dict[str, float]:
        """محاسبه اندیکاتورهای تکنیکال"""
        if len(data) < 20:
            return {
                "volatility": 0.5,
                "trend_strength": 0.5,
                "momentum": 0.0,
                "rsi": 50.0
            }
        
        # محاسبه بازدهی
        returns = data['Close'].pct_change().dropna()
        
        # نوسان (Volatility)
        volatility = returns.std() * np.sqrt(252)  # سالانه
        volatility_normalized = min(1.0, volatility * 10)
        
        # قدرت روند (Trend Strength)
        sma_20 = data['Close'].rolling(window=20).mean()
        sma_50 = data['Close'].rolling(window=min(50, len(data))).mean()
        current_price = data['Close'].iloc[-1]
        
        if len(sma_20) > 0 and len(sma_50) > 0:
            trend_strength = abs(sma_20.iloc[-1] - sma_50.iloc[-1]) / current_price
            trend_strength = min(1.0, trend_strength * 100)
        else:
            trend_strength = 0.5
        
        # مومنتوم
        if len(returns) > 10:
            momentum = returns.iloc[-10:].mean()
        else:
            momentum = 0.0
        
        # RSI (Relative Strength Index)
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-9)
        rsi = 100 - (100 / (1 + rs.iloc[-1])) if len(rs) > 0 else 50.0
        
        return {
            "volatility": round(volatility_normalized, 3),
            "trend_strength": round(trend_strength, 3),
            "momentum": round(momentum, 6),
            "rsi": round(rsi, 2)
        }
    
    def _is_cache_valid(self) -> bool:
        """بررسی اعتبار کش"""
        if not self.last_fetch_time or not self.cached_data:
            return False
        elapsed = (datetime.now() - self.last_fetch_time).total_seconds()
        return elapsed < self.cache_duration
    
    def _update_cache(self, price: float):
        """به‌روزرسانی کش"""
        self.cached_data = {
            "price": price,
            "timestamp": datetime.now().isoformat()
        }
        self.last_fetch_time = datetime.now()


class MarketAnalyzer:
    """تحلیلگر بازار برای استخراج ویژگی‌ها"""
    
    def __init__(self, data_provider: ForexDataProvider):
        self.data_provider = data_provider
        
    def get_market_context(self) -> Dict[str, float]:
        """دریافت context کامل بازار"""
        # دریافت داده‌های تاریخی
        data = self.data_provider.get_historical_data(days=7, interval="1h")
        
        if data.empty:
            return {
                "volatility": 0.5,
                "trend_strength": 0.5,
                "momentum": 0.0,
                "rsi": 50.0
            }
        
        # محاسبه اندیکاتورها
        indicators = self.data_provider.compute_technical_indicators(data)
        return indicators
