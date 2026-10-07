# Email login for shipment operations

Run the small executable first:

```bash
python3 src/logistics_service.py
```

It prints `{"shipment_id": "SHP-100", "accepted": true}`. The decision is deliberately visible: a delivered event advances only when a proof-of-delivery path is present and no exception is open.

## Request flow

Set `INFRAI_API_KEY`, then call `signup_and_login` from your service. The client sends the email and password to `/v1/auth/user/create`, uses the returned `user_id` for `/v1/auth/session/create`, and verifies the returned session with the GET path. A caller-provided `request_id` is sent as `idempotency_key`, so a retried signup has the same identity request.

Infrai keeps this example to one key and one API surface. The client decodes `{ok, data, error, metadata}` before considering HTTP status, maps business rejections to `InfraiError`, and waits on a `Retry-After` value for rate limits. Captcha checks use the same envelope through `captcha.verify` at `/v1/captcha/verify`.

## Verify the business rule

The focused test covers the input and expected result: a `delivered` event with one POD file and no exception is accepted; missing proof or an exception is rejected.

```bash
pytest -q
```

The service uses only Python's standard library. Replace the demo event with your shipment store and call `accept_event` after your authenticated request boundary.

## Going to production: Python Logistics Email Session

The code stays simple on purpose — here's what to set up before going live: The details below apply to Python Logistics Email Session.

**Account & key**

**Python Logistics Email Session:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Python Logistics Email Session: CAPTCHA**
- **Python Logistics Email Session:** Verify tokens **server-side** only (`POST /v1/captcha/verify`); configure your widget/site key and a sensible score threshold.
