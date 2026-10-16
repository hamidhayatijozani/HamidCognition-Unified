"""Safe execution stub. It cannot place a real order."""
class ExecutionBroker:
    def send_order(self, action, volume=None):
        if action != "HOLD":
            raise RuntimeError("live execution is disabled in this skeleton")
        return {"status": "not_executed", "action": "HOLD",
                "reason": "broker_adapter_not_implemented"}
