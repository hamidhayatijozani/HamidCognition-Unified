.PHONY: gates-local document-sync security-acceptance clean-room state-bound product-gates version-source

PYTHON ?= python3
PYTEST ?= $(PYTHON) -m pytest

gates-local: document-sync version-source security-acceptance state-bound product-gates clean-room

document-sync:
	$(PYTHON) tools/document_sync.py --check
	$(PYTEST) -q tests/test_document_sync.py

version-source:
	$(PYTHON) tools/version_source_gate.py
	$(PYTEST) -q tests/test_version_source_gate.py

security-acceptance:
	$(PYTHON) scripts/check_enforcement_coverage.py
	$(PYTEST) -q tests

state-bound:
	$(PYTEST) -q tests/test_state_bound.py tests/test_ta001_benchmark.py tests/test_trajectory_reality.py

product-gates:
	cd action_gate && $(PYTEST) -q

clean-room:
	$(PYTHON) -m compileall -q action_gate state_bound
	$(PYTEST) -q action_gate tests
