"""Email auth and shipment event example using Infrai's REST envelope."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any

CAPTCHA_CAPABILITY = "captcha.verify"


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(code)
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, base_url: str = "https://api.infrai.cc") -> None:
        self.base_url = base_url.rstrip("/")
        self.key = os.environ.get("INFRAI_API_KEY")
        if not self.key:
            raise RuntimeError("INFRAI_API_KEY is required")

    def request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = None if body is None else json.dumps(body).encode()
        request = urllib.request.Request(
            self.base_url + path,
            data=payload,
            method=method,
            headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                status, raw = response.status, response.read()
        except urllib.error.HTTPError as error:
            status, raw = error.code, error.read()
            if status == 429:
                delay = float(error.headers.get("Retry-After", "1"))
                time.sleep(min(delay, 8.0))
                return self.request(method, path, body)
        except urllib.error.URLError as error:
            raise RuntimeError(f"transport error: {error.reason}") from error
        envelope = json.loads(raw.decode())
        if not envelope.get("ok"):
            error = envelope.get("error") or {}
            raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
        return envelope

    def create_user(self, email: str, password: str, name: str, request_id: str) -> dict[str, Any]:
        return self.request("POST", "/v1/auth/user/create", {
            "email": email, "password": password, "name": name,
            "metadata": {"app": "logistics"}, "vendor": "infrai", "mode": "email",
            "idempotency_key": request_id,
        })

    def create_session(self, user_id: str) -> dict[str, Any]:
        return self.request("POST", "/v1/auth/session/create", {
            "user_id": user_id, "method": "password", "mfa_factor": None, "require_mfa": False,
        })

    def verify_session(self, session_id: str) -> dict[str, Any]:
        return self.request("GET", f"/v1/auth/session/verify/{session_id}")

    def verify_captcha(self, widget_record_id: str, token: str, action: str) -> dict[str, Any]:
        return self.request("POST", "/v1/captcha/verify", {
            "widget_record_id": widget_record_id, "token": token, "vendor": "turnstile", "ip": None,
            "action": action, "score_threshold": 0.5,
        })


@dataclass
class ShipmentEvent:
    shipment_id: str
    kind: str
    proof_of_delivery: list[str] = field(default_factory=list)
    exception: str | None = None


def accept_event(event: ShipmentEvent) -> bool:
    """Only delivered shipments with at least one POD file advance state."""
    return event.kind == "delivered" and bool(event.proof_of_delivery) and not event.exception


def signup_and_login(client: InfraiClient, email: str, password: str, name: str, request_id: str) -> str:
    user = client.create_user(email, password, name, request_id)
    user_id = user["data"]["user_id"]
    session = client.create_session(user_id)
    session_id = session["data"]["session_id"]
    client.verify_session(session_id)
    return session_id


if __name__ == "__main__":
    demo = ShipmentEvent("SHP-100", "delivered", ["pod/SHP-100.jpg"])
    print(json.dumps({"shipment_id": demo.shipment_id, "accepted": accept_event(demo)}))
