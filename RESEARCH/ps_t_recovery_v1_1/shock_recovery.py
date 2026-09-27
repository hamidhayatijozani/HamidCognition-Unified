from dataclasses import dataclass

@dataclass(frozen=True)
class RecoveryConfig:
    t_base: float = 0.50
    t_min: float = 0.01
    t_max: float = 0.80
    recovery_rate: float = 0.10
    shock_rate: float = 0.20
    recovery_threshold: float = 1.0

def shock_saturation(d: float) -> float:
    if d < 0:
        raise ValueError("D_must_be_nonnegative")
    return d / (1.0 + d)

def update_t(t, d_prev, d_now, recovering, cfg=RecoveryConfig()):
    entered = d_now < d_prev and d_now <= cfg.recovery_threshold
    recovering = recovering or entered
    r = int(recovering and d_now <= cfg.recovery_threshold)
    raw = t + cfg.recovery_rate * (1.0 - t) * r - cfg.shock_rate * shock_saturation(d_now)
    t_new = min(max(raw, cfg.t_min), cfg.t_max)
    if t_new >= cfg.t_base and d_now <= cfg.recovery_threshold:
        recovering = False
    return t_new, r, recovering

def trajectory(d_values, cfg=RecoveryConfig()):
    t = cfg.t_base
    previous = d_values[0]
    recovering = False
    rows = []
    for step, d in enumerate(d_values):
        t, r, recovering = update_t(t, previous, d, recovering, cfg)
        rows.append({"step": step, "D": round(d, 8), "R": r, "T": round(t, 8)})
        previous = d
    return rows
