ARG BASE_IMAGE_DIGEST
FROM python:3.12-slim@${BASE_IMAGE_DIGEST}
ARG POSTGRESQL_CLIENT_VERSION
WORKDIR /app
RUN test -n "$POSTGRESQL_CLIENT_VERSION"
RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client="$POSTGRESQL_CLIENT_VERSION" \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
COPY requirements.lock .
RUN python -m pip install --no-cache-dir --require-hashes -r requirements.lock
COPY VERSION app.py storage.py self_audit.py rate_limit.py canonicalization.py keyring.py policy_store.py action_gate_sdk.py csg_contract.py csg_ingress.py csg_routes.py decision_authority.py security_authority.py csg_acceptance.py csg_persistence_replay.py agentrq_simulator.py production_e2e_smoke.py entrypoint.sh ./
RUN useradd --create-home --uid 10001 appuser && mkdir -p /data && chown -R appuser:appuser /data entrypoint.sh
RUN chmod +x /app/entrypoint.sh
ENV ACTION_GATE_DB=/data/action_gate.db
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=5s --retries=12 --start-period=60s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).read()"
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
