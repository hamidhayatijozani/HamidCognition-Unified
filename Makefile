#!/usr/bin/make -f
.NOTPARALLEL: gates-local

.PHONY: gates-local document-sync version-source security-acceptance state-bound product-gates clean-room gates-timed

PYTHON ?= python3
PYTEST ?= $(PYTHON) -m pytest

# Evidence rule: a target whose output is not recorded is not evidence.
# gates-local is the canonical gate chain for both local and CI execution.
gates-local: document-sync version-source state-bound product-gates security-acceptance clean-room

document-sync:
	$(PYTHON) tools/document_sync.py --check
	$(PYTEST) -q tests/test_document_sync.py

version-source:
	$(PYTHON) tools/version_source_gate.py
	$(PYTEST) -q tests/test_version_source_gate.py

state-bound:
	$(PYTEST) -q tests/test_state_bound.py tests/test_ta001_benchmark.py tests/test_trajectory_reality.py

product-gates:
	cd action_gate && $(PYTEST) -q

security-acceptance:
	$(PYTHON) scripts/check_enforcement_coverage.py
	$(PYTEST) -q tests

clean-room:
	$(PYTHON) -m compileall -q action_gate state_bound
	$(PYTEST) -q action_gate tests

gates-timed:
	@for g in document-sync version-source state-bound product-gates security-acceptance clean-room; do \
		start=$$(date +%s%N); \
		$(MAKE) $$g >/tmp/gate-$$g.log 2>&1 || { rc=$$?; end=$$(date +%s%N); echo "$$g $$(( (end-start)/1000000 )) ms FAIL"; tail -20 /tmp/gate-$$g.log; exit $$rc; }; \
		end=$$(date +%s%N); echo "$$g $$(( (end-start)/1000000 )) ms PASS"; \
done
