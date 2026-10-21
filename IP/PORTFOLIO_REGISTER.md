# Portfolio Intellectual Property Evidence Register

**Prepared:** 2026-10-21  
**Owner/account under review:** `hamidhayatijozani`  
**Purpose:** Track evidence collection across repositories. This is an internal evidence register, not a legal registration or a declaration that all code, ideas, names, or inventions are exclusively owned.

## Rules for this register

- GitHub account ownership/admin access is not conclusive proof of authorship or exclusive IP ownership.
- No project is marked as legally registered unless a competent authority has issued verifiable confirmation.
- Source code, contributor history, dependency licences, assignments, and confidential information must be reviewed before making a definitive ownership claim.
- Hashes and transparency-log records support integrity and chronology; they do not create intellectual-property rights.
- Do not publicly disclose potentially patentable technical details before checking disclosure consequences in the relevant jurisdictions.

## Repository coverage

| Repository | Observed state | Evidence record | Attestation status |
|---|---|---|---|
| `HamidCognition-Unified` | Public, active | Merged; `IP/OWNERSHIP_EVIDENCE.md` and portfolio register | PASS: [run](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/39597673011); Rekor log index `3355741096`; [artifact](https://github.com/hamidhayatijozani/HamidCognition-Unified/actions/runs/39597673011) |
| `EURUSD-5M-Forecast` | Public, active | Merged | PASS: [run](https://github.com/hamidhayatijozani/EURUSD-5M-Forecast/actions/runs/39597682934); Rekor log index `3355743635`; [artifact](https://github.com/hamidhayatijozani/EURUSD-5M-Forecast/actions/runs/39597682934) |
| `EURUSD-5M-ForecastHamid` | Active | Merged | PASS: [run](https://github.com/hamidhayatijozani/EURUSD-5M-ForecastHamid/actions/runs/39597692437); Rekor log index `3355741500`; [artifact](https://github.com/hamidhayatijozani/EURUSD-5M-ForecastHamid/actions/runs/39597692437) |
| `epistemic-filter` | Public, active; default branch `master` | Merged | PASS: [run](https://github.com/hamidhayatijozani/epistemic-filter/actions/runs/39597657211); Rekor log index `3355737237`; [artifact](https://github.com/hamidhayatijozani/epistemic-filter/actions/runs/39597657211) |
| `hhj-cognitive-safety-gateway` | Public, active | Merged | PASS: [run](https://github.com/hamidhayatijozani/hhj-cognitive-safety-gateway/actions/runs/39597664879); Rekor log index `3355737816`; [artifact](https://github.com/hamidhayatijozani/hhj-cognitive-safety-gateway/actions/runs/39597664879) |
| `vahshi-` | Public, active | Merged | PASS: [run](https://github.com/hamidhayatijozani/vahshi-/actions/runs/39597647803); Rekor log index `3355736033`; [artifact](https://github.com/hamidhayatijozani/vahshi-/actions/runs/39597647803) |
| `quant-smart-money-tracker` | Active | Merged | PASS: [run](https://github.com/hamidhayatijozani/quant-smart-money-tracker/actions/runs/39597701432); Rekor log index `3355742731`; [artifact](https://github.com/hamidhayatijozani/quant-smart-money-tracker/actions/runs/39597701432) |
| `aegis-csg` | Public, active; empty before evidence file | Merged evidence file; still no product source code observed | PASS for evidence snapshot: [run](https://github.com/hamidhayatijozani/aegis-csg/actions/runs/39597711479); Rekor log index `3355744608`; [artifact](https://github.com/hamidhayatijozani/aegis-csg/actions/runs/39597711479) |
| `HamidCognition` | Archived | Not modified; repository is read-only while archived | BLOCKED: needs owner-approved unarchive or separate external evidence archive |
| `HamidCognitionEngine` | Archived | Not modified; repository is read-only while archived | BLOCKED: needs owner-approved unarchive or separate external evidence archive |
| `hamidcognition-web` | Archived | Not modified; repository is read-only while archived | BLOCKED: needs owner-approved unarchive or separate external evidence archive |
| `hamidcognition-realtime` | Archived | Not modified; repository is read-only while archived | BLOCKED: needs owner-approved unarchive or separate external evidence archive |
| `hamidcognition-v0-max` | Archived | Not modified; repository is read-only while archived | BLOCKED: needs owner-approved unarchive or separate external evidence archive |
| `hamidcognition-complete` | Archived | Not modified; repository is read-only while archived | BLOCKED: needs owner-approved unarchive or separate external evidence archive |
| `ki-is-koni` | Private, archived | Not modified; repository is read-only while archived | BLOCKED: needs owner-approved unarchive or separate external evidence archive |
| `epistemic-filterr` | Private, archived | Not modified; repository is read-only while archived | BLOCKED: needs owner-approved unarchive or separate external evidence archive |

## Completed technical attestation

Eight active repositories were updated through pull requests, then merged. The path-limited GitHub Actions workflow ran against each resulting default-branch commit. All eight jobs completed successfully. Each run:
1. generated a manifest containing the repository, commit SHA, ref, UTC capture time, and SHA-256 hashes of tracked files after excluding common secret/private-key/data-dump patterns;
2. signed the manifest using Cosign with GitHub OIDC identity;
3. created a Sigstore transparency-log entry (Rekor);
4. verified the signature with `cosign verify-blob` (`Verified OK` in the job log); and
5. uploaded a bundle artifact with 90-day retention.

The artifacts include the manifest, its SHA-256 digest, commit metadata, and Sigstore bundle. Open each linked Actions run and its **Artifacts** section to retrieve the bundle. The run log contains the transparency-log index listed above.

## Remaining evidence and legal gaps

- **Source provenance:** commit authorship and the chain of title have not been exhaustively audited.
- **Third-party rights:** dependency/SBOM and licence audit remains pending.
- **Contributor and assignment records:** no complete set of signed contributor, employment, or assignment agreements has been reviewed.
- **Archived repositories:** eight repositories remain unmodified because they are archived/read-only. Do not unarchive them without explicit owner authorization.
- **Formal IP registrations:** no trademark, patent, or other government registration has been submitted or confirmed.
- **Exclusive ownership:** remains **UNVERIFIED** until provenance and third-party rights are reviewed.

## Next steps

1. Obtain explicit authorization before unarchiving any of the eight archived repositories, or preserve their snapshots and manifests in an external archive that does not require changing their settings.
2. Audit authorship, dependencies, licences, datasets, generated files, and assignments in the eight attested repositories.
3. Independently download and retain each artifact in at least one owner-controlled location beyond GitHub's 90-day artifact retention.
4. Search proposed brand names in WIPO and relevant national/regional trademark databases.
5. Assess patentability and disclosure risk before publishing potentially novel technical details; pursue formal filing only after confirming jurisdiction, eligibility, and costs or an applicable support scheme.

## Current conclusion

**Technical integrity evidence:** PASS for eight repositories, based on successful signature verification and logged transparency entries.  
**Legal ownership / exclusive rights:** **UNVERIFIED**. The technical attestations support integrity and chronology but do not themselves grant or prove intellectual-property rights.
