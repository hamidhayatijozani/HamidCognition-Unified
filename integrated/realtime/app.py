"""
🧠 HamidCognition Real-Time Platform
پلتفرم پیش‌بینی لحظه‌ای فارکس با موتور شناختی
"""

from flask import Flask, render_template, jsonify
import threading
import time
from datetime import datetime
import sys
import os

# اضافه کردن مسیر ماژول‌ها
sys.path.insert(0, os.path.dirname(__file__))

from core.hamid_cognition import HamidCognition
from api.forex_data import ForexDataProvider, MarketAnalyzer
from models.predictor import ForexPredictor, PredictionEngine

app = Flask(__name__, template_folder='ui/templates', static_folder='ui/static')

# ======================== راه‌اندازی سیستم ========================

# موتور شناختی
cognition = HamidCognition(initial_p=0.75, initial_s=0.65, initial_t=0.50)

# ارائه‌دهنده داده
data_provider = ForexDataProvider(symbol="EURUSD", cache_duration=30)
market_analyzer = MarketAnalyzer(data_provider)

# مدل پیش‌بینی
predictor = ForexPredictor(window_size=60)
prediction_engine = PredictionEngine(predictor, cognition)

# داده‌های زنده
live_data = {
    "status": "initializing",
    "current_price": None,
    "predictions": [],
    "cognitive_state": cognition.get_state(),
    "market_context": {},
    "timestamp": datetime.now().isoformat(),
    "error": None
}

# ======================== تابع به‌روزرسانی زنده ========================

def update_live_data():
    """به‌روزرسانی مداوم داده‌های زنده"""
    global live_data
    
    print("🚀 سیستم پیش‌بینی زنده شروع شد...")
    
    # آموزش اولیه مدل
    print("📚 آموزش مدل با داده‌های تاریخی...")
    historical_data = data_provider.get_historical_data(days=7, interval="1h")
    if not historical_data.empty:
        predictor.train(historical_data)
        print("✅ مدل آموزش داده شد")
    else:
        print("⚠️ داده‌های تاریخی در دسترس نیست")
    
    while True:
        try:
            # دریافت قیمت فعلی
            current_price = data_provider.get_current_price()
            
            if current_price is None:
                live_data["status"] = "error"
                live_data["error"] = "Unable to fetch current price"
                time.sleep(30)
                continue
            
            # دریافت context بازار
            market_context = market_analyzer.get_market_context()
            
            # دریافت داده‌های تاریخی برای پیش‌بینی
            historical_data = data_provider.get_historical_data(days=3, interval="1h")
            
            if historical_data.empty:
                live_data["status"] = "warning"
                live_data["error"] = "Limited historical data"
            else:
                live_data["status"] = "active"
                live_data["error"] = None
            
            # تولید پیش‌بینی‌ها
            result = prediction_engine.generate_predictions(
                current_price=current_price,
                historical_data=historical_data,
                market_context=market_context
            )
            
            # به‌روزرسانی داده‌های زنده
            live_data.update({
                "status": "active",
                "current_price": current_price,
                "predictions": result["predictions"],
                "cognitive_state": result["cognitive_state"],
                "market_context": result["market_context"],
                "timestamp": result["timestamp"],
                "error": None
            })
            
            print(f"✅ به‌روزرسانی: {current_price} | فاز: {result['cognitive_state']['phase']}")
            
        except Exception as e:
            print(f"❌ خطا در به‌روزرسانی: {e}")
            live_data["status"] = "error"
            live_data["error"] = str(e)
        
        # صبر 30 ثانیه تا به‌روزرسانی بعدی
        time.sleep(30)

# ======================== روت‌های Flask ========================

@app.route("/")
def index():
    """صفحه اصلی داشبورد"""
    return render_template("dashboard.html")

@app.route("/api/live")
def api_live():
    """API برای دریافت داده‌های زنده"""
    return jsonify(live_data)

@app.route("/api/status")
def api_status():
    """وضعیت سیستم"""
    return jsonify({
        "status": live_data["status"],
        "timestamp": datetime.now().isoformat(),
        "model_trained": predictor.is_trained,
        "last_update": live_data["timestamp"]
    })

@app.route("/api/history")
def api_history():
    """تاریخچه تصمیمات شناختی"""
    return jsonify({
        "history": cognition.history[-50:],  # آخرین 50 رکورد
        "total_records": len(cognition.history)
    })

# ======================== راه‌اندازی ========================

if __name__ == "__main__":
    # شروع thread برای به‌روزرسانی زنده
    update_thread = threading.Thread(target=update_live_data, daemon=True)
    update_thread.start()
    
    print("="*60)
    print("🧠 HamidCognition Real-Time Platform")
    print("="*60)
    print("🌐 Dashboard: http://127.0.0.1:5000")
    print("📊 API: http://127.0.0.1:5000/api/live")
    print("="*60)
    
    # اجرای Flask
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
