from __future__ import annotations

import os
from typing import Any, Protocol

import httpx

from .models import BrokerEnvironment, BrokerExecutionState, BrokerResult, MarketOrder
from .risk import BrokerPolicy


class HttpTransport(Protocol):
    def get(self, url: str, **kwargs: Any) -> httpx.Response: ...
    def post(self, url: str, **kwargs: Any) -> httpx.Response: ...


class OandaBroker:
    """OANDA v20 adapter with practice-by-default and fail-closed live controls."""

    PRACTICE_URL = "https://api-fxpractice.oanda.com"
    LIVE_URL = "https://api-fxtrade.oanda.com"

    def __init__(
        self,
        *,
        token: str | None = None,
        account_id: str | None = None,
        environment: BrokerEnvironment | None = None,
        live_trading_enabled: bool | None = None,
        live_confirmation: str | None = None,
        policy: BrokerPolicy | None = None,
        transport: HttpTransport | None = None,
    ) -> None:
        self.token = token or os.getenv("OANDA_API_TOKEN", "")
        self.account_id = account_id or os.getenv("OANDA_ACCOUNT_ID", "")
        self.environment = environment or BrokerEnvironment(
            os.getenv("OANDA_ENVIRONMENT", BrokerEnvironment.PRACTICE.value)
        )
        self.live_trading_enabled = (
            live_trading_enabled
            if live_trading_enabled is not None
            else os.getenv("LIVE_TRADING_ENABLED", "false").lower() == "true"
        )
        self.live_confirmation = live_confirmation or os.getenv("LIVE_TRADING_CONFIRMATION", "")
        self.policy = policy or BrokerPolicy()
        self.transport = transport or httpx.Client(timeout=10.0)

    @property
    def base_url(self) -> str:
        return self.LIVE_URL if self.environment is BrokerEnvironment.LIVE else self.PRACTICE_URL

    def _headers(self) -> dict[str, str]:
        if not self.token:
            raise RuntimeError("OANDA_API_TOKEN is not configured")
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _require_account(self) -> None:
        if not self.account_id:
            raise RuntimeError("OANDA_ACCOUNT_ID is not configured")

    def account(self) -> dict[str, Any]:
        self._require_account()
        response = self.transport.get(
            f"{self.base_url}/v3/accounts/{self.account_id}",
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()

    def pricing(self, instrument: str) -> dict[str, Any]:
        self._require_account()
        response = self.transport.get(
            f"{self.base_url}/v3/accounts/{self.account_id}/pricing",
            headers=self._headers(),
            params={"instruments": instrument},
        )
        response.raise_for_status()
        return response.json()

    def submit_market_order(
        self,
        order: MarketOrder,
        *,
        gate_authorized: bool,
    ) -> BrokerResult:
        self.policy.validate(order)

        if not gate_authorized:
            return BrokerResult(
                BrokerExecutionState.BLOCKED, None, None, None, {},
                "action_gate_authorization_required",
            )

        if self.environment is BrokerEnvironment.LIVE:
            if not self.live_trading_enabled or self.live_confirmation != "LIVE":
                return BrokerResult(
                    BrokerExecutionState.BLOCKED, None, None, None, {},
                    "live_trading_disabled",
                )

        self._require_account()
        payload: dict[str, Any] = {
            "order": {
                "type": "MARKET",
                "instrument": order.instrument,
                "units": str(order.units),
                "timeInForce": "FOK",
                "positionFill": "DEFAULT",
                "clientExtensions": {
                    "id": order.operation_id,
                    "tag": "hamidcognition-action-gate",
                },
            }
        }
        if order.stop_loss is not None:
            payload["order"]["stopLossOnFill"] = {
                "price": str(order.stop_loss),
                "timeInForce": "GTC",
            }
        if order.take_profit is not None:
            payload["order"]["takeProfitOnFill"] = {
                "price": str(order.take_profit),
                "timeInForce": "GTC",
            }

        try:
            response = self.transport.post(
                f"{self.base_url}/v3/accounts/{self.account_id}/orders",
                headers=self._headers(),
                json=payload,
            )
            response.raise_for_status()
        except Exception as exc:
            return BrokerResult(
                BrokerExecutionState.UNKNOWN, None, None, None, {},
                f"broker_transport_uncertain:{type(exc).__name__}",
            )

        body = response.json()
        create_tx = body.get("orderCreateTransaction") or {}
        fill_tx = body.get("orderFillTransaction") or {}
        state = BrokerExecutionState.FILLED if fill_tx else BrokerExecutionState.SUBMITTED
        return BrokerResult(
            state=state,
            broker_order_id=str(create_tx.get("id")) if create_tx.get("id") else None,
            broker_trade_id=(
                str((fill_tx.get("tradeOpened") or {}).get("tradeID"))
                if (fill_tx.get("tradeOpened") or {}).get("tradeID")
                else None
            ),
            request_id=response.headers.get("RequestID"),
            raw=body,
        )
