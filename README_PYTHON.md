# Sail API Python Guide

This guide uses [`example.py`](example.py), which exposes a `SailAPIClient` with current direct-auth, custom SIWE, and metrics helpers.

## Setup

```bash
pip install -r requirements.txt
cp example.env .env
python example.py
```

## Configuration

Set these values in `.env` or directly in `example.py`:

```env
SAIL_API_URL=https://app.sail.money/prod
SAIL_PROJECT_ID=sail
SAIL_PAGE_ID=home
SAIL_PRIVATE_KEY=0x...
```

## Direct Auth Example

Direct auth is a two-step flow.

```python
from example import SailAPIClient, sign_message, get_wallet_address

client = SailAPIClient(BASE_URL, PROJECT_ID, PAGE_ID)
wallet_address = get_wallet_address(PRIVATE_KEY)

direct_auth = client.request_direct_auth_payload(wallet_address)
signature = sign_message(direct_auth["payload"], PRIVATE_KEY)

auth = client.complete_direct_auth(
    wallet_address=wallet_address,
    signature=signature,
    auth_payload=direct_auth["payload"],
)

print(auth["token"])
print(auth["user_id"])
print(auth["authFlow"])  # direct
```

The first call returns `payload` and optional `instructionMessage`. The second call returns `token`, `user_id`, `statusMessage`, `is_new_user`, and `authFlow`.

## Custom SIWE Example

```python
from example import SailAPIClient, sign_message, get_wallet_address

client = SailAPIClient(BASE_URL, PROJECT_ID, PAGE_ID)
wallet_address = get_wallet_address(PRIVATE_KEY)

session = client.initiate_siwe_auth(
    address=wallet_address,
    chain_id=8453,
    identity_mode="byWallet",
)

signature = sign_message(session["message"], PRIVATE_KEY)

auth = client.complete_siwe_auth(
    session_id=session["sessionId"],
    signature=signature,
    wallet_address=wallet_address,
    identity_mode="byWallet",
)

print(auth.get("identityMode"))
print(auth.get("walletAddress"))
print(auth.get("accountToken"))
```

## Legacy `byUser` Recovery

Use `byUser` only if the signer wallet already has a legacy mapping on the backend:

```python
session = client.initiate_siwe_auth(
    address=wallet_address,
    chain_id=8453,
    identity_mode="byUser",
)
signature = sign_message(session["message"], PRIVATE_KEY)
auth = client.complete_siwe_auth(
    session_id=session["sessionId"],
    signature=signature,
    wallet_address=wallet_address,
    identity_mode="byUser",
)
```

If no legacy mapping exists, Sail rejects the request. `byUser` does not create a new legacy identity.

## Metrics Examples

All metrics endpoints return `{"message": str, "result": object}`.

```python
balance_metrics = client.get_metrics_balance()
print(balance_metrics["message"])
print(balance_metrics["result"])

history_metrics = client.get_metrics_history({"limit": 20})
print(history_metrics["result"])
```

Available metrics helpers:

```python
client.get_metrics_balance()
client.get_metrics_earnings()
client.get_metrics_history({"limit": 20})
client.get_metrics_portfolio()
client.get_metrics_user_metrics()
client.get_metrics_yield()
```

You can also use the generic helper:

```python
client.get_metrics("yield")
client.get_metrics("history", {"metadata": 1})
```

## Common API Calls

After authentication, the client supports:

```python
client.get_balance()
client.get_deposit_info()
client.get_withdraw_info()
client.get_portfolio_total_balance()
client.get_portfolio_tokens()
client.get_tier_info()
client.get_page()
client.get_automation_status()
client.get_chatbots()
client.get_metrics_balance()
client.get_metrics_yield()
```

Custom APIs are still available:

```python
client.get_custom_api("api_id", {"foo": "bar"})
client.post_custom_api("api_id", {"foo": "bar"})
```
