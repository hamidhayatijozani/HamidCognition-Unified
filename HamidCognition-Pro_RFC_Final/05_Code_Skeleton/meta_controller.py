"""Read-only supervisory stub."""
class MetaController:
    def assess(self, health):
        if not isinstance(health, dict) or health.get("data_fresh") is not True:
            return {"decision": "HOLD", "reason": "data_not_confirmed_fresh"}
        if health.get("risk_check") is not True:
            return {"decision": "HOLD", "reason": "risk_check_not_confirmed"}
        return {"decision": "REVIEW", "reason": "human_review_required"}
