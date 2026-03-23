# Security Notes

This repo documents the current public auth patterns used by the Sail API examples. It is intentionally high level and avoids claims that depend on older implementation details.

## Current Auth Models

The example repo covers two current auth styles:

- Direct auth for smart account wallets via the two-step `/authenticate` flow
- Custom SIWE auth for signer-driven integrations via `/auth/initiate` and `/auth/complete`

Both flows rely on wallet signatures. Private keys remain client-side.

## Direct Auth

Direct auth works in two requests:

1. Request a unique payload from `/authenticate`
2. Sign that payload
3. Submit `walletAddress`, `signature`, and `payload` back to `/authenticate`

This means the example repo should not describe direct auth as a single fixed-message signature flow.

## Custom SIWE

Custom SIWE works in two requests:

1. Request a SIWE session from `/auth/initiate`
2. Sign the returned SIWE message
3. Submit `sessionId`, `signature`, `walletAddress`, and optional `identityMode` to `/auth/complete`

`identityMode` behaves like this:

- `byWallet`: default and recommended for new integrations
- `byUser`: legacy recovery only for previously issued legacy identities

## Tokens And Access

Successful authentication can return:

- `token`: Sail JWT for authenticated API requests
- `accountToken`: account-service token for SIWE/account-service flows
- `walletAddress`: issued smart account or account-service wallet, depending on flow

Which fields are present depends on the flow you use.

## Wallet And Identity Notes

- Do not assume every endpoint removes `walletAddress` from request bodies. Some current endpoints still require explicit wallet inputs.
- Do not assume every auth flow derives identity from the same backend field. Direct auth and custom SIWE have different request shapes and different downstream behavior.
- For custom SIWE, `byWallet` and legacy `byUser` represent different identity-binding modes and should be documented as such.

## Metrics Endpoints

The metrics endpoints are configurable page-backed surfaces:

- `/metrics/balance`
- `/metrics/earnings`
- `/metrics/history`
- `/metrics/portfolio`
- `/metrics/user-metrics`
- `/metrics/yield`

They return a wrapper shaped like:

```json
{
  "message": "Metrics endpoint executed successfully",
  "result": {}
}
```

The exact `result` payload depends on the configured tool or graph.

## Best Practices

- Keep private keys out of source control
- Use HTTPS in production
- Validate responses before acting on them
- Treat `byUser` as legacy recovery only
- Prefer `byWallet` for new SIWE integrations
