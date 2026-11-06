# Awareness Layer

The repository now contains a hierarchical awareness core, registry, supervisor, canonical component contracts, schemas, tests, and governance documentation.

The implementation is bounded: components may observe, detect needs, request authorized actions, verify outcomes, and escalate outside their authority. This is an engineering architecture, not a claim of consciousness.

## Mother Memory

The MEMORY component now has a local, private multi-model perspective store. It records attributed model assessments with provenance, evidence references, explicit uncertainty and human review. Cross-provider pattern recurrence is surfaced only as a review candidate.

See [docs/MOTHER_MEMORY.md](docs/MOTHER_MEMORY.md) for the data contract, privacy boundary and CLI.

Runtime personal data is excluded from Git by the repository's `/data/` ignore rule. Do not commit user assessments or conversation exports.
