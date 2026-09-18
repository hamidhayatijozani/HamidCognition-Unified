# RFC-0001: Runtime Event Model

**Status:** Proposed  
**Author:** Hamid Hayati Jozani  
**Date:** 2026-07-13  
**Version:** 1.0  

---

## 1. Overview

This RFC defines the complete schema for all runtime observations that HHJ-CSG collects, validates, and uses for decision-making. The event model is designed to be:

- **Immutable:** Once recorded, events cannot be modified
- **Traceable:** Every event has a unique ID and timestamp
- **Deterministic:** Same events always produce same decisions
- **Auditable:** Complete lineage from observation to decision

---

## 2. Event Taxonomy

```
RuntimeEvent
├── IdentityEvent
│   ├── AuthenticationEvent
│   ├── AuthorizationEvent
│   └── RoleChangeEvent
├── ContextEvent
│   ├── EnvironmentEvent
│   ├── SessionEvent
│   └── NetworkEvent
├── ToolEvent
│   ├── ToolRegistrationEvent
│   ├── ToolInvocationEvent
│   └── ToolResultEvent
├── PolicyEvent
│   ├── PolicyLoadEvent
│   ├── PolicyChangeEvent
│   └── PolicyViolationEvent
└── SystemEvent
    ├── GatewayHealthEvent
    ├── PerformanceEvent
    └── ErrorEvent
```

---

## 3. Base Event Schema

All events inherit from this base schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "event_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique identifier for this event"
    },
    "event_type": {
      "type": "string",
      "enum": [
        "AUTHENTICATION",
        "AUTHORIZATION",
        "TOOL_INVOCATION",
        "ENVIRONMENT_CHANGE",
        "POLICY_VIOLATION",
        "SYSTEM_ERROR"
      ]
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "Event timestamp (UTC, ISO8601)"
    },
    "workspace_id": {
      "type": "string",
      "format": "uuid"
    },
    "agent_id": {
      "type": "string",
      "format": "uuid"
    },
    "source": {
      "type": "string",
      "enum": ["agentRQ", "external_api", "user_action", "system"],
      "description": "Origin of this event"
    },
    "severity": {
      "type": "string",
      "enum": ["info", "warning", "error", "critical"]
    },
    "metadata": {
      "type": "object",
      "additionalProperties": true
    }
  },
  "required": [
    "event_id",
    "event_type",
    "timestamp",
    "workspace_id",
    "source"
  ]
}
```

---

## 4. Identity Events

### 4.1 AuthenticationEvent

```json
{
  "event_id": "evt-auth-001",
  "event_type": "AUTHENTICATION",
  "timestamp": "2026-07-13T12:34:56Z",
  "workspace_id": "ws-uuid",
  "agent_id": "agent-uuid",
  "source": "agentRQ",
  "severity": "info",
  "authentication": {
    "method": "oauth|mTLS|api_key|service_account",
    "identity": "user@example.com",
    "identity_hash": "sha256(...)",
    "success": true,
    "failure_reason": null,
    "session_id": "sess-uuid",
    "ip_address": "192.168.1.1",
    "user_agent": "string"
  }
}
```

### 4.2 AuthorizationEvent

```json
{
  "event_id": "evt-authz-001",
  "event_type": "AUTHORIZATION",
  "timestamp": "2026-07-13T12:34:56Z",
  "workspace_id": "ws-uuid",
  "agent_id": "agent-uuid",
  "source": "agentRQ",
  "severity": "info",
  "authorization": {
    "identity": "user@example.com",
    "roles": ["admin", "developer"],
    "permissions": [
      "tool:execute",
      "resource:read",
      "resource:write"
    ],
    "effective_permissions": ["tool:execute"],
    "denied_permissions": ["resource:delete"],
    "scope": "workspace|global",
    "expires_at": "2026-07-14T12:34:56Z"
  }
}
```

### 4.3 RoleChangeEvent

```json
{
  "event_id": "evt-role-001",
  "event_type": "ROLE_CHANGE",
  "timestamp": "2026-07-13T12:34:56Z",
  "workspace_id": "ws-uuid",
  "source": "system",
  "severity": "warning",
  "role_change": {
    "identity": "user@example.com",
    "previous_roles": ["user"],
    "new_roles": ["admin"],
    "changed_by": "admin@example.com",
    "reason": "Promotion to admin"
  }
}
```

---

## 5. Context Events

### 5.1 EnvironmentEvent

```json
{
  "event_id": "evt-env-001",
  "event_type": "ENVIRONMENT_CHANGE",
  "timestamp": "2026-07-13T12:34:56Z",
  "workspace_id": "ws-uuid",
  "source": "system",
  "severity": "info",
  "environment": {
    "name": "production|staging|development",
    "region": "us-east-1",
    "cluster": "cluster-1",
    "capacity_available": 0.85,
    "health_status": "healthy|degraded|critical",
    "resource_limits": {
      "cpu_percent": 45,
      "memory_percent": 62,
      "disk_percent": 78
    }
  }
}
```

### 5.2 SessionEvent

```json
{
  "event_id": "evt-sess-001",
  "event_type": "SESSION_EVENT",
  "timestamp": "2026-07-13T12:34:56Z",
  "workspace_id": "ws-uuid",
  "agent_id": "agent-uuid",
  "source": "agentRQ",
  "severity": "info",
  "session": {
    "session_id": "sess-uuid",
    "identity": "agent@workspace",
    "started_at": "2026-07-13T10:00:00Z",
    "last_activity": "2026-07-13T12:34:56Z",
    "duration_seconds": 9296,
    "request_count": 42,
    "error_count": 1
  }
}
```

### 5.3 NetworkEvent

```json
{
  "event_id": "evt-net-001",
  "event_type": "NETWORK_EVENT",
  "timestamp": "2026-07-13T12:34:56Z",
  "workspace_id": "ws-uuid",
  "source": "system",
  "severity": "warning",
  "network": {
    "source_ip": "192.168.1.1",
    "destination_ip": "10.0.0.1",
    "protocol": "https",
    "port": 443,
    "latency_ms": 45,
    "packet_loss_percent": 0,
    "geo_location": "US-CA",
    "is_vpn": false,
    "is_proxy": false
  }
}
```

---

## 6. Tool Events

### 6.1 ToolInvocationEvent

```json
{
  "event_id": "evt-tool-001",
  "event_type": "TOOL_INVOCATION",
  "timestamp": "2026-07-13T12:34:56Z",
  "workspace_id": "ws-uuid",
  "agent_id": "agent-uuid",
  "source": "agentRQ",
  "severity": "info",
  "tool_invocation": {
    "tool_name": "restart_service",
    "tool_version": "1.0.0",
    "parameters": {
      "service_name": "api-server",
      "force": false,
      "timeout_seconds": 30
    },
    "parameters_hash": "sha256(...)",
    "requested_by": "agent@workspace",
    "request_id": "req-uuid",
    "estimated_impact": "high|medium|low",
    "requires_approval": true,
    "retry_count": 0
  }
}
```

### 6.2 ToolResultEvent

```json
{
  "event_id": "evt-tool-result-001",
  "event_type": "TOOL_RESULT",
  "timestamp": "2026-07-13T12:35:01Z",
  "workspace_id": "ws-uuid",
  "agent_id": "agent-uuid",
  "source": "agentRQ",
  "severity": "info",
  "tool_result": {
    "tool_name": "restart_service",
    "request_id": "req-uuid",
    "status": "success|failure|timeout",
    "exit_code": 0,
    "stdout": "Service restarted successfully",
    "stderr": null,
    "execution_time_ms": 5000,
    "resources_affected": {
      "services": ["api-server"],
      "databases": [],
      "users_impacted": 150
    }
  }
}
```

---

## 7. Policy Events

### 7.1 PolicyLoadEvent

```json
{
  "event_id": "evt-policy-load-001",
  "event_type": "POLICY_LOAD",
  "timestamp": "2026-07-13T12:34:56Z",
  "workspace_id": "ws-uuid",
  "source": "system",
  "severity": "info",
  "policy_load": {
    "policy_id": "pol-uuid",
    "policy_name": "production_safety_policy",
    "version": "2.1.0",
    "rules_count": 42,
    "policy_hash": "sha256(...)",
    "loaded_by": "admin@example.com",
    "effective_from": "2026-07-13T12:34:56Z"
  }
}
```

### 7.2 PolicyViolationEvent

```json
{
  "event_id": "evt-policy-violation-001",
  "event_type": "POLICY_VIOLATION",
  "timestamp": "2026-07-13T12:34:56Z",
  "workspace_id": "ws-uuid",
  "agent_id": "agent-uuid",
  "source": "agentRQ",
  "severity": "critical",
  "policy_violation": {
    "policy_id": "pol-uuid",
    "violated_rule": "no_delete_in_production",
    "violation_type": "resource_deletion",
    "resource_type": "database",
    "resource_id": "db-prod-001",
    "action_attempted": "DELETE",
    "enforcement": "deny|warn|allow",
    "remediation": "Request escalated to admin"
  }
}
```

---

## 8. System Events

### 8.1 GatewayHealthEvent

```json
{
  "event_id": "evt-health-001",
  "event_type": "GATEWAY_HEALTH",
  "timestamp": "2026-07-13T12:34:56Z",
  "workspace_id": "ws-uuid",
  "source": "system",
  "severity": "info",
  "gateway_health": {
    "status": "healthy|degraded|unhealthy",
    "uptime_seconds": 86400,
    "requests_processed": 50000,
    "errors_count": 5,
    "error_rate": 0.0001,
    "latency_p95_ms": 145,
    "memory_usage_mb": 256,
    "cpu_usage_percent": 12
  }
}
```

### 8.2 PerformanceEvent

```json
{
  "event_id": "evt-perf-001",
  "event_type": "PERFORMANCE_EVENT",
  "timestamp": "2026-07-13T12:34:56Z",
  "workspace_id": "ws-uuid",
  "source": "system",
  "severity": "warning",
  "performance": {
    "metric_name": "decision_latency",
    "value": 450,
    "unit": "ms",
    "threshold": 500,
    "status": "warning|critical",
    "trend": "increasing|stable|decreasing"
  }
}
```

---

## 9. Event Validation Rules

### 9.1 Immutability

- Events MUST NOT be modified after creation
- Corrections require a new CorrectionEvent with reference to original
- Hash chain MUST be maintained for audit trail

### 9.2 Ordering

- Events MUST be ordered by timestamp
- Clock skew tolerance: ±1 second
- Out-of-order events flagged for investigation

### 9.3 Completeness

- All required fields MUST be present
- Missing fields trigger validation error
- Null values only allowed for optional fields

### 9.4 Consistency

- workspace_id MUST match workspace context
- agent_id MUST be registered in workspace
- Timestamp MUST be recent (within 5 minutes)

---

## 10. Event Storage

### 10.1 Format

**Recommended:** JSONL (JSON Lines)

```
{"event_id": "...", "event_type": "AUTHENTICATION", ...}
{"event_id": "...", "event_type": "AUTHORIZATION", ...}
{"event_id": "...", "event_type": "TOOL_INVOCATION", ...}
```

### 10.2 Retention

- **Hot Storage:** 7 days (fast access)
- **Warm Storage:** 90 days (slower access)
- **Cold Storage:** 2 years (archive)
- **Deletion:** After 2 years (compliance)

### 10.3 Indexing

**Primary Index:** event_id  
**Secondary Indices:**
- workspace_id + timestamp
- agent_id + event_type
- event_type + severity

---

## 11. Implementation Checklist

- [ ] JSON Schema validation implemented
- [ ] All event types tested
- [ ] Event ordering verified
- [ ] Immutability enforced
- [ ] Storage backend configured
- [ ] Retention policies applied
- [ ] Indexing optimized
- [ ] Audit trail verified

---

**End of RFC-0001**
