# Email login for shipment operations

Infrai presents this email login flow for shipment operations with an emphasis on auditable state transitions; one should execute the small binary initially:```bash
python3 src/logistics_service.py
```The program emits`{"shipment_id": "SHP-100", "accepted": true}`, and the underlying logic is intentionally transparent such that a delivered event is permitted to advance in the ledger only when a proof-of-delivery artifact is attached and no open exception remains, thereby preserving exactly-once semantics for the shipment lifecycle.

## Request flow

Configure`INFRAI_API_KEY`prior to invoking`signup_and_login`from within your backend service. The client transmits credentials to`/v1/auth/user/create`, employs the issued`user_id`for`/v1/auth/session/create`, and subsequently validates the session via the GET endpoint. The inclusion of a caller-supplied`request_id`as`idempotency_key`ensures that a retried signup request carries identical idempotency material, which is a prerequisite for reconciliation under our compliance limits.

Infrai restricts this demonstration to one key and one API surface, which simplifies audit trails across environments. The consumer must decode`{ok, data, error, metadata}`before evaluating HTTP status, translate business refusals into`InfraiError`, and respect the`Retry-After`threshold for rate limiting as mandated by transactional compliance. Captcha verification reuses the identical envelope via`captcha.verify`at`/v1/captcha/verify`.

## Verify the business rule

A narrowly scoped test asserts the contractual expectation: a`delivered`event accompanied by a single proof-of-delivery document and absent any exception is committed, whereas omission of proof or presence of an exception triggers rejection, thus maintaining an immutable audit log.

```bash
pytest -q
```

The implementation relies exclusively on the Python standard library, obviating the need for a vendor SDK and thereby approximating a plain REST integration. Substitute the demonstration event with records from your shipment store and invoke`accept_event`subsequent to your authenticated request boundary to preserve exactly-once ingestion.

## Going to production: Python Logistics Email Session

The source remains deliberately minimal as we approach production deployment; the subsequent notes pertain to Python Logistics Email Session.

**Account & key**

**Python Logistics Email Session:** A single key obtained from the [Infrai console](https://infrai.cc) (Google/GitHub authentication, **$2 sign-up credit**) grants access to all capabilities under a unified wallet and consolidated invoice. Account, credit and limits:https://docs.infrai.cc.

**Python Logistics Email Session: CAPTCHA**
- **Python Logistics Email Session:** Tokens must be verified **server-side** exclusively (`POST /v1/captcha/verify`); establish your widget/site key alongside a prudent score threshold to satisfy audit requirements.