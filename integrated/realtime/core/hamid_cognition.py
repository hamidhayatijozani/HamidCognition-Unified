"""
موتور شناختی HamidCognition - نسخه پیشرفته
این موتور بر اساس معماری P/S/T (Power/Synchronicity/Tenacity) کار می‌کند
"""

import numpy as np
from datetime import datetime
from typing import Dict, List, Any
import json


class HamidCognition:
    """
    موتور شناختی مبتنی بر بردار P/S/T
    
    P (Power/Penetration): قدرت نفوذ و تأثیرگذاری
    S (Synchronicity/Sensitivity): همزمانی و حساسیت به تغییرات
    T (Tenacity/Stability): پایداری و مقاومت در برابر تغییرات
    """
    
    def __init__(self, initial_p=0.75, initial_s=0.65, initial_t=0.50):
        self.P = initial_p
        self.S = initial_s
        self.T = initial_t
        self.history = []
        self.phase_history = []
        
    def compute_energy(self) -> float:
        """محاسبه انرژی شناختی بر اساس P, S, T"""
        numerator = self.P * self.S
        denominator = (1.1 - self.T + 1e-9)
        stability_factor = (1 - self.T / (self.P + self.S + 1e-9))
        energy = numerator / denominator * stability_factor
        return min(energy, 2.0)  # محدود کردن انرژی
    
    def compute_phase(self, market_context: Dict[str, float]) -> Dict[str, Any]:
        """
        محاسبه فاز شناختی فعلی
        
        فازها:
        - RUPTURE_IMMINENT: خطر شکست و تغییر ناگهانی
        - SYNTHESIS_PEAK: اوج هماهنگی و قدرت
        - UNSTABLE_CREATIVITY: خلاقیت ناپایدار
        - STEADY_EXPLORATION: کاوش پایدار
        """
        energy = self.compute_energy()
        convergence = abs(self.P - self.S)
        
        # تشخیص فاز
        if convergence < 0.12:
            phase = "RUPTURE_IMMINENT"
            confidence = 0.3
        elif self.T < 0.40:
            phase = "UNSTABLE_CREATIVITY"
            confidence = 0.5
        elif self.P > 0.80 and self.S > 0.75:
            phase = "SYNTHESIS_PEAK"
            confidence = 0.9
        else:
            phase = "STEADY_EXPLORATION"
            confidence = 0.7
        
        jump_risk = min(1.0, convergence * 3.0)
        
        return {
            "phase": phase,
            "energy": round(energy, 3),
            "confidence": round(confidence, 3),
            "jump_risk": round(jump_risk, 3),
            "convergence": round(convergence, 3)
        }
    
    def update(self, market_context: Dict[str, float]) -> Dict[str, Any]:
        """
        به‌روزرسانی وضعیت شناختی بر اساس شرایط بازار
        
        Args:
            market_context: شامل volatility, trend_strength, momentum
        """
        volatility = market_context.get("volatility", 0.5)
        trend_strength = market_context.get("trend_strength", 0.5)
        momentum = market_context.get("momentum", 0.0)
        
        # محاسبه فشار و نوآوری
        pressure = min(1.0, volatility * 1.5)
        novelty = min(1.0, abs(momentum) * 2.0)
        
        # به‌روزرسانی P (قدرت)
        P_change = 0.05 * pressure * (1 - self.T)
        self.P = np.clip(self.P + P_change, 0.1, 0.95)
        
        # به‌روزرسانی S (حساسیت)
        S_change = 0.04 * novelty * (1 - abs(self.P - self.S))
        self.S = np.clip(self.S + S_change, 0.1, 0.95)
        
        # به‌روزرسانی T (پایداری)
        T_change = 0.03 * (self.S / (self.P + 1e-9)) * (1 + pressure)
        self.T = np.clip(self.T + T_change, 0.1, 0.85)
        
        # محاسبه فاز
        phase_info = self.compute_phase(market_context)
        
        # ذخیره تاریخچه
        state = {
            "timestamp": datetime.now().isoformat(),
            "P": round(self.P, 3),
            "S": round(self.S, 3),
            "T": round(self.T, 3),
            "phase": phase_info["phase"],
            "energy": phase_info["energy"],
            "confidence": phase_info["confidence"],
            "market_context": market_context
        }
        self.history.append(state)
        
        # نگه‌داری فقط 1000 رکورد آخر
        if len(self.history) > 1000:
            self.history = self.history[-1000:]
        
        return state
    
    def get_state(self) -> Dict[str, Any]:
        """دریافت وضعیت فعلی"""
        phase_info = self.compute_phase({})
        return {
            "P": round(self.P, 3),
            "S": round(self.S, 3),
            "T": round(self.T, 3),
            "energy": phase_info["energy"],
            "phase": phase_info["phase"],
            "confidence": phase_info["confidence"],
            "jump_risk": phase_info["jump_risk"]
        }
    
    def get_decision_bias(self) -> float:
        """
        محاسبه bias برای تصمیم‌گیری
        
        Returns:
            عددی بین -1 تا 1 که جهت و قدرت تصمیم را نشان می‌دهد
        """
        phase_info = self.compute_phase({})
        energy = phase_info["energy"]
        confidence = phase_info["confidence"]
        
        # bias مثبت = تمایل به خرید، منفی = تمایل به فروش
        bias = (self.P - self.S) * energy * confidence
        return np.clip(bias, -1.0, 1.0)
    
    def export_history(self, filename: str):
        """ذخیره تاریخچه در فایل"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
