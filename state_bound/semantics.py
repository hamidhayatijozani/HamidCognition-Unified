from .models import digest

def equivalent_request(request_a:dict,request_b:dict)->bool:
    """Replay-equivalence: same business-critical action; context may differ."""
    return digest(request_a.get("action"))==digest(request_b.get("action"))
