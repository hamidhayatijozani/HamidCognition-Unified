# Model Weight Provenance Contract

## Purpose

This contract defines how model weights become part of a HamidCognition release without treating a mutable model name, branch, tag, or download URL as proof of identity.

A model is admitted to production only when the exact bytes used by the runtime are bound to an immutable source revision and a SHA-256 digest.

## Weight identity

Every admitted model must have:

- model_id
- source_repository
- source_revision
- artifact_path
- artifact_sha256
- weight_format
- runtime
- license
- verified_at
- release_binding

source_revision must identify an immutable revision. A mutable branch such as main is not sufficient.

artifact_sha256 is calculated from the actual bytes consumed by the runtime. A checksum copied from a model card is not accepted as the runtime artifact hash.

## Repository alignment

The registry distinguishes source repositories from actual model-weight repositories. The current GitHub inventory contains several HamidCognition source repositories, but no verified model-weight artifact has been discovered in them. They are therefore recorded as no_weight_artifact_verified rather than being falsely promoted to model repositories.

Code provenance is not weight provenance.

## Accepted artifact forms

Preferred tensor format is safetensors where the runtime supports it. Other formats such as ONNX, GGUF, PyTorch state dictionaries, or TensorFlow checkpoints require explicit format declaration and runtime compatibility evidence.

Each quantized, optimized, merged, pruned, converted, fine-tuned, or otherwise transformed artifact receives its own model_id and SHA-256 digest.

## Lineage

The release chain is:

source repository -> immutable revision -> actual bytes -> SHA-256 -> runtime package -> release

A transformed model receives a new identity. Its parent is recorded as lineage metadata rather than silently treating the two artifacts as identical.

## Admission rule

An entry with missing or placeholder provenance is never eligible for production release.

No weight bytes, credentials, private keys, or live payment information belong in this registry.

## Release binding

A final release binds:

release tag/commit -> model_id -> artifact_sha256 -> runtime image/container identity -> attestation

Changing the weight bytes without changing the registered hash must fail verification.

## Current state

The registry is intentionally empty of admitted models until an exact model repository, immutable revision, artifact, hash, runtime compatibility, and license evidence are verified. This is a control, not a missing placeholder.
