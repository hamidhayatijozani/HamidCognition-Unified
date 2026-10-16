"""Research-only decision interface; not a trained or profitable trading model."""
class CognitiveEngine:
    def update_state(self, tick):
        return {"symbol": tick.symbol, "timestamp": tick.timestamp.isoformat(),
                "mid": (tick.bid + tick.ask) / 2, "spread": tick.ask - tick.bid}

    def decide(self, state):
        # Deliberately no BUY/SELL output until a validated model is supplied.
        return {"action": "HOLD", "reason": "research_skeleton_no_validated_model",
                "state": state}

    def learn_from_trade(self, reward):
        raise NotImplementedError("training loop requires a specified offline experiment")
