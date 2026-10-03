"""Experimental state-bound execution governance prototype.

This module is research-only and does not alter the Action Gate commercial
commercial release path.
"""
from .models import Decision, ExecutionAuthority, WorldState
from .verifier import verify_authority

__all__ = ["Decision", "ExecutionAuthority", "WorldState", "verify_authority"]
