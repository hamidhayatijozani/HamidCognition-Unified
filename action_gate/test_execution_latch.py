from datetime import datetime, timezone
from validation_boundary import make_decision
from execution_latch import authorize_execution

NOW=datetime(2026,9,15,16,0,tzinfo=timezone.utc); ISSUED="2026-09-15T15:59:00+00:00"
REQ={"request_id":"r1","action":"read","target":"x","parameters":{},"requester":"agent","timestamp":"2026-09-15T15:58:00+00:00"}
EVIDENCE={"state":"PRESENT","artifact_ref":"e/1","sha256":"a"*64}

def test_latch_permits_bound_allow():
    d=make_decision(REQ,"ALLOW",ISSUED,EVIDENCE); a=authorize_execution(REQ,d,now=NOW); assert a.permitted and a.request_digest==d["request_digest"]

def test_latch_blocks_deny():
    d=make_decision(REQ,"DENY",ISSUED,EVIDENCE); assert not authorize_execution(REQ,d,now=NOW).permitted

def test_latch_blocks_mutation():
    d=make_decision(REQ,"ALLOW",ISSUED,EVIDENCE); REQ["target"]="attacker"; assert not authorize_execution(REQ,d,now=NOW).permitted
