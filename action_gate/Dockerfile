ARG PYTHON_BASE_IMAGE=python:3.12-slim
FROM ${PYTHON_BASE_IMAGE}
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY action_gate/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY action_gate/VERSION action_gate/app.py action_gate/storage.py action_gate/self_audit.py action_gate/rate_limit.py action_gate/canonicalization.py action_gate/keyring.py action_gate/policy_store.py action_gate/action_gate_sdk.py action_gate/csg_contract.py action_gate/csg_ingress.py action_gate/csg_routes.py action_gate/decision_authority.py action_gate/security_authority.py action_gate/state_oracle.py action_gate/csg_acceptance.py action_gate/csg_persistence_replay.py action_gate/agentrq_simulator.py action_gate/production_e2e_smoke.py PRODUCT/customer_acceptance_smoke.py action_gate/entrypoint.sh ./
RUN useradd --create-home --uid 10001 appuser && mkdir -p /data && chown -R appuser:appuser /data entrypoint.sh customer_acceptance_smoke.py
RUN chmod +x /app/entrypoint.sh /app/customer_acceptance_smoke.py
ENV ACTION_GATE_DB=/data/action_gate.db
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=5s --retries=12 --start-period=60s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).read()"
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
