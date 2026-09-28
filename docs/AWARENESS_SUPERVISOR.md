# Awareness Supervisor

The supervisor is the top coordination layer of the awareness tree.

It does not own every capability. It observes component health, receives detected needs, routes authorized work to the component that owns the capability, and escalates work that has no local authority.

The hierarchy is deliberately asymmetric:

ROOT
-> GOVERNANCE
-> COGNITION
-> EXECUTION
-> FEEDBACK

A component can be active without being sovereign.

Routing rules:
1. Local authorized action wins.
2. If local authority is absent, route to the parent for escalation.
3. If no parent authority exists, route to HUMAN_APPROVAL.
4. No child may grant itself a new permission.
5. Every completed action must be capable of binding to evidence.

This keeps autonomy bounded while allowing proactive behavior.
