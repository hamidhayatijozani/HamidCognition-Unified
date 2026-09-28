# Agent Action Risk Lab

## Purpose

Agent Action Risk Lab is the demonstration and proof layer for HamidCognition Action Gate.

It does not replace Action Gate. It creates a controlled before/after experiment showing what changes when a real agent tool is placed behind an enforceable authorization boundary.

## Core experiment

**Baseline**

Agent → Protected Tool

**Governed**

Agent → Action Gate → Protected Tool

The same action cases are executed against both paths.

## Required cases

1. authorized action;
2. unauthorized action;
3. expired authority;
4. replayed authority;
5. tenant/session tampering;
6. action or policy tampering;
7. direct downstream bypass.

## Evidence

For every case record:

- scenario identifier;
- action;
- tenant;
- actor;
- session;
- policy;
- baseline result;
- governed result;
- HTTP status/result;
- evidence identifier;
- timestamp;
- release/source identifier.

The Lab must never manufacture a successful result. An unavailable or unverified test is reported as UNKNOWN.

## Demonstration output

The customer should be able to see:

| Test | Without boundary | With Action Gate |
|---|---|---|
| Authorized action | executes | executes |
| Unauthorized action | baseline-dependent | rejected |
| Expired authority | baseline-dependent | rejected |
| Replay | baseline-dependent | rejected |
| Tampering | baseline-dependent | rejected |
| Direct bypass | baseline-dependent | rejected when enforcement is configured |

The exact baseline result is measured, not assumed.

## Commercial role

The public/free demonstration proves the mechanism.

The paid pilot runs the same methodology against one customer-selected real tool or MCP server.

## Boundary

This Lab does not claim:

- universal agent safety;
- prevention of every attack;
- regulatory compliance;
- business ROI;
- correctness of the customer's downstream system.

Its claim is narrower: it measures whether the tested protected execution path enforces the specified authorization contract.
