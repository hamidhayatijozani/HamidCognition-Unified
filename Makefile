#!/usr/bin/make -f
.NOTPARALLEL: gates-local gates-timed

.PHONY: gates-local document-sync version-source security-acceptance state-bound product-gates clean-room gates-timed

PYTHON ?= python3
PYTEST ?= $(PYTHON) -m pytest

# Evidence rule: a target whose output is not recorded is not evidence.
# gates-local is the canonical gate chain for both local and CI execution.
gates-local: gates-timed

document-sync:
	$(PYTHON) tools/document_sync.py --check
	$(PYTEST) -q tests/test_document_sync.py

version-source:
	$(PYTHON) tools/version_source_gate.py
	$(PYTEST) -q tests/test_version_source_gate.py

state-bound:
	$(PYTEST) -q tests/test_state_bound.py tests/test_chemical_reactivity.py tests/test_pre_execution_signal_integration.py tests/test_ta001_benchmark.py tests/test_trajectory_reality.py

product-gates:
	cd action_gate && $(PYTEST) -q

security-acceptance:
	$(PYTHON) scripts/check_enforcement_coverage.py
	$(PYTEST) -q tests

clean-room:
	$(PYTHON) -m compileall -q action_gate state_bound
	$(PYTEST) -q action_gate tests

gates-timed:
	@mkdir -p evidence/gates-timing
	@rm -f evidence/gates-timing/gates-timing.log
	@for g in document-sync version-source state-bound product-gates security-acceptance clean-room; do \
		start=$$(date +%s%N); \
		echo "=== $$g START $$(date -u +%Y-%m-%dT%H:%M:%SZ) ===" | tee -a evidence/gates-timing/gates-timing.log; \
		$(MAKE) $$g >evidence/gates-timing/$$g.log 2>&1; rc=$$?; cat evidence/gates-timing/$$g.log | tee -a evidence/gates-timing/gates-timing.log; \
		end=$$(date +%s%N); elapsed=$$(( (end-start)/1000000 )); \
		if [ $$rc -ne 0 ]; then echo "$$g $$elapsed ms FAIL" | tee -a evidence/gates-timing/gates-timing.log; exit $$rc; fi; \
		echo "$$g $$elapsed ms PASS" | tee -a evidence/gates-timing/gates-timing.log; \
	done
