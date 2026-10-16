"""Research proposal registry; never edits source code or production policy."""
class SelfRewritingGrammar:
    def propose(self, metrics):
        if not isinstance(metrics, dict):
            raise TypeError("metrics must be a dictionary")
        return {"status": "PROPOSAL_ONLY", "metrics": dict(metrics),
                "requires_human_review": True}
