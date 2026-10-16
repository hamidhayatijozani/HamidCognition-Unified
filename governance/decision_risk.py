"""Decision-risk heuristic. All inputs must be normalized to [0, 1]."""
import math


class DecisionRiskScore:
    WEIGHTS = {"impact": 0.30, "autonomy": 0.25, "irreversibility": 0.25, "uncertainty": 0.20}

    def __init__(self, impact_severity: float, autonomy_level: float,
                 reversibility_factor: float, uncertainty: float):
        # Input is explicitly the difficulty of reversing an action: 1 = hard to reverse.
        self.values = {
            "impact": impact_severity, "autonomy": autonomy_level,
            "irreversibility": reversibility_factor, "uncertainty": uncertainty,
        }
        for name, value in self.values.items():
            if not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"{name} must be a finite number in [0, 1]")

    def calculate(self) -> float:
        return round(sum(self.WEIGHTS[k] * v for k, v in self.values.items()), 4)
