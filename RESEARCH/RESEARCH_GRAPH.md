# HamidCognition Unified — Research Graph

این گراف باید رابطه بین مفهوم، کد، commit، فرضیه، آزمایش، داده، نتیجه و تناقض را حفظ کند.

## Node types
- CONCEPT
- IMPLEMENTATION
- SOURCE_REPO
- COMMIT
- HYPOTHESIS
- EXPERIMENT
- DATASET
- METRIC
- RESULT
- CONTRADICTION
- UNKNOWN
- DECISION
- FAILURE
- EVIDENCE

## Edge types
- IMPLEMENTS
- DERIVED_FROM
- DUPLICATES
- VARIANT_OF
- CONTRADICTS
- TESTS
- SUPPORTS
- FALSIFIES
- DEPENDS_ON
- PRODUCES
- REPLAYS
- SUPERSEDES
- UNCOVERS
- BLOCKS
- REQUIRES_EVIDENCE

## Required provenance
هر node مهم باید تا حد امکان این موارد را داشته باشد:
- source repository
- source path
- commit SHA
- creation/update date
- epistemic class
- evidence level
- related experiment
- known limitations

## Canonicality rule
Canonical یک edge یا node نیست که با سلیقه انتخاب شود. canonical status یک نتیجه آزمایشی است و باید حداقل شامل:
1. contract definition
2. conformance tests
3. reproducibility result
4. dependency/runtime compatibility
5. regression coverage
6. lineage preservation
باشد.

## Unknown-space rule
اگر مفهوم هنوز تعریف عملیاتی ندارد، باید به UNKNOWN متصل شود و برای آن یک مسیر تبدیل UNKNOWN → HYPOTHESIS → EXPERIMENT → RESULT ایجاد شود. این کار جلوی تبدیل استعاره به معماری را می‌گیرد.
