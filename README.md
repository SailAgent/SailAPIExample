# Sail API Example Repo

This repo contains low-level JavaScript and Python examples for calling the Sail API directly. It tracks the current SailUI API reference for authentication, metrics, and core SDK endpoints.

## Included Guides

- [JavaScript Guide](README_JAVASCRIPT.md)
- [Python Guide](README_PYTHON.md)
- [Security Notes](SECURITY.md)

## Quick Start

1. Copy `example.env` to `.env`
2. Fill in your backend URL, project ID, page ID, and wallet private key
3. Run either the JavaScript or Python example client

```bash
cp example.env .env
```

## Authentication Options

This repo documents both current Sail authentication styles:

- Direct auth via `POST /authenticate`
- Custom SIWE auth via `POST /auth/initiate` and `POST /auth/complete`

### Direct Auth

Direct auth is a two-step flow for smart account wallets:

1. Request a unique payload:

```json
{
  "walletAddress": "0x..."
}
```

Response:

```json
{
  "payload": "sail.money wants you to sign in with your Ethereum account...",
  "instructionMessage": "Sign the payload and submit it back with your wallet address."
}
```

2. Sign the returned `payload`
3. Complete auth:

```json
{
  "walletAddress": "0x...",
  "signature": "0x...",
  "payload": "sail.money wants you to sign in with your Ethereum account..."
}
```

Completion response:

```json
{
  "token": "jwt...",
  "user_id": "user_id_here",
  "statusMessage": "Authentication successful",
  "is_new_user": false,
  "authFlow": "direct"
}
```

### Custom SIWE Auth

Custom SIWE is the current flow for integrations that want explicit identity binding and Thirdweb-issued wallets.

1. Initiate:

```json
{
  "method": "siwe",
  "address": "0x...",
  "chainId": 8453,
  "identityMode": "byWallet"
}
```

Response:

```json
{
  "sessionId": "session_...",
  "message": "service.org wants you to sign in with your Ethereum account..."
}
```

2. Sign the returned `message`
3. Complete:

```json
{
  "method": "siwe",
  "sessionId": "session_...",
  "signature": "0x...",
  "walletAddress": "0x...",
  "identityMode": "byWallet"
}
```

Completion response includes:

- `token`
- `accountToken`
- `walletAddress`
- `user_id`
- `is_new_user`
- `authFlow`
- `identityMode`

### `identityMode`

- `byWallet`
  - Default and recommended
  - The normalized signer wallet becomes the stable identity subject
- `byUser`
  - Legacy recovery only
  - Only works when Sail already has a legacy wallet-to-subject mapping
  - If no legacy mapping exists, Sail rejects the request instead of creating a new legacy identity

## Metrics Endpoints

This repo now covers the configurable metrics route family:

- `GET /metrics/balance`
- `GET /metrics/earnings`
- `GET /metrics/history`
- `GET /metrics/portfolio`
- `GET /metrics/user-metrics`
- `GET /metrics/yield`

These endpoints are page-backed metrics surfaces. Each one executes the configured tool or graph for that metrics slot and returns:

```json
{
  "message": "Balance endpoint executed successfully",
  "result": {}
}
```

Notes:

- `result` depends on the configured tool or graph
- query params are passed through to the configured tool or graph
- `?metadata=1` is supported on the backend for param discovery, but the example clients focus on normal execution

## Main Endpoint Groups

- `/authenticate`
- `/auth/initiate`, `/auth/complete`
- `/balance`
- `/metrics/balance`, `/metrics/earnings`, `/metrics/history`, `/metrics/portfolio`, `/metrics/user-metrics`, `/metrics/yield`
- `/deposit-info`, `/deposit`, `/deposit/pre-hooks`, `/deposit/post-hooks`
- `/withdraw-info`, `/withdraw`, `/withdraw/pre-hooks`, `/withdraw/post-hooks`
- `/portfolio/total-balance`, `/portfolio/tokens`
- `/tier`
- `/page`
- `/automation/status`, `/automation/start`, `/automation/pause`, `/automation/resume`, `/automation/stop`
- `/chatbots`, `/chatbot-memories`
- `/custom/{api_id}`

## Notes

- The example clients include helper methods for both direct auth and custom SIWE auth.
- The metrics helpers are generic wrappers around `/metrics/{endpoint_id}` plus convenience methods for the six supported endpoint IDs.
- Many endpoints depend on project and page configuration, so some calls may return configuration-related errors in a clean local test.
