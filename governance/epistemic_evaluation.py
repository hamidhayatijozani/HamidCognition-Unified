"""HAIS is a configurable heuristic, not a validated probability of truth."""
import math


class HAISCalculator:
    WEIGHTS = {"EAS": 0.30, "NED": 0.20, "CPS": 0.20, "CQM": 0.15, "OCR": 0.15}

    @staticmethod
    def _unit(value: float, name: str) -> float:
        if not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
            raise ValueError(f"{name} must be a finite number in [0, 1]")
        return float(value)

    def calculate(self, eas: float, ned: float, cps: float, cqm: float, ocr: float) -> float:
        v = {k: self._unit(x, k) for k, x in
             {"EAS": eas, "NED": ned, "CPS": cps, "CQM": cqm, "OCR": ocr}.items()}
        score = (self.WEIGHTS["EAS"] * v["EAS"] +
                 self.WEIGHTS["NED"] * (1 - v["NED"]) +
                 self.WEIGHTS["CPS"] * v["CPS"] +
                 self.WEIGHTS["CQM"] * v["CQM"] +
                 self.WEIGHTS["OCR"] * (1 - v["OCR"]))
        return round(score, 4)

    @staticmethod
    def classify(hais: float) -> str:
        if not isinstance(hais, (int, float)) or not math.isfinite(hais) or not 0 <= hais <= 1:
            raise ValueError("HAIS must be in [0, 1]")
        if hais >= 0.85:
            return "TRUSTED"
        if hais >= 0.65:
            return "REVIEW_REQUIRED"
        return "UNSAFE"
