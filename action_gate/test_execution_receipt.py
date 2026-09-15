"""Adversarial tests for Execution Receipt binding and integrity."""
from datetime import datetime, timezone, timedelta
from execution_receipt import make_receipt, validate_receipt, digest

NOW=datetime(2026,9,15,16,0,tzinfo=timezone.utc); START=(NOW-timedelta(seconds=10)).isoformat(); FINISH=NOW.isoformat()
REQUEST={"action":"send_email","target":"recipient-A","parameters":{"body":"controlled"}}
REQUEST_DIGEST=digest(REQUEST); DECISION_ID="dec-001"; DECISION_DIGEST=digest({"decision_id":DECISION_ID,"decision":"ALLOW"})
ACTION_HASH=digest({"action":REQUEST["action"],"target":REQUEST["target"],"parameters":REQUEST["parameters"]}); NONCE="nonce-001"

def receipt():
    return make_receipt(request=REQUEST,request_digest=REQUEST_DIGEST,decision_id=DECISION_ID,decision_digest=DECISION_DIGEST,action_hash=ACTION_HASH,nonce=NONCE,executor_id="executor-A",started_at=START,finished_at=FINISH,status="EXECUTED",outcome={"provider_status":200})

def check(r,executor="executor-A"):
    return validate_receipt(r,request=REQUEST,request_digest=REQUEST_DIGEST,decision_id=DECISION_ID,decision_digest=DECISION_DIGEST,action_hash=ACTION_HASH,nonce=NONCE,expected_executor_id=executor)

def test_valid_receipt(): assert check(receipt()).valid
def test_request_rebinding_fails():
    r=receipt(); r["request_digest"]=digest({"action":"delete_file"}); assert not check(r).valid
def test_decision_rebinding_fails():
    r=receipt(); r["decision_id"]="dec-attacker"; assert not check(r).valid
def test_action_rebinding_fails():
    r=receipt(); r["action_hash"]="0"*64; assert not check(r).valid
def test_nonce_rebinding_fails():
    r=receipt(); r["nonce"]="attacker-nonce"; assert not check(r).valid
def test_tampered_outcome_fails_integrity():
    r=receipt(); r["outcome"]["provider_status"]=500; result=check(r); assert not result.valid and "integrity:receipt_digest_mismatch" in result.errors
def test_finished_before_started_fails():
    r=receipt(); r["finished_at"]=(NOW-timedelta(seconds=20)).isoformat(); assert not check(r).valid
def test_status_cannot_be_invented():
    r=receipt(); r["status"]="SUCCESSFUL_IN_THE_REAL_WORLD"; assert not check(r).valid
def test_executor_identity_is_bound_when_expected():
    r=receipt(); r["executor_id"]="attacker"; r["receipt_digest"]=digest({k:r[k] for k in r if k!="receipt_digest"}); result=check(r); assert not result.valid and "executor:identity_mismatch" in result.errors
