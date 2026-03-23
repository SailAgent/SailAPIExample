# Sail API JavaScript Guide

This guide uses [`example.js`](example.js), which exposes a `SailAPIClient` with current direct-auth, custom SIWE, and metrics helpers.

## Setup

```bash
npm install
cp example.env .env
node example.js
```

Or with yarn:

```bash
yarn install
yarn start
```

## Configuration

Set these values in `.env` or directly in `example.js`:

```env
SAIL_API_URL=https://app.sail.money/prod
SAIL_PROJECT_ID=sail
SAIL_PAGE_ID=home
SAIL_PRIVATE_KEY=0x...
```

## Direct Auth Example

Direct auth is a two-step flow.

```javascript
const { SailAPIClient, signMessage, getWalletAddress } = require("./example");

const client = new SailAPIClient(BASE_URL, PROJECT_ID, PAGE_ID);
const walletAddress = getWalletAddress(PRIVATE_KEY);

const directAuth = await client.requestDirectAuthPayload(walletAddress);
const signature = await signMessage(directAuth.payload, PRIVATE_KEY);

const auth = await client.completeDirectAuth(
  walletAddress,
  signature,
  directAuth.payload
);

console.log(auth.token);
console.log(auth.user_id);
console.log(auth.authFlow); // direct
```

The first call returns `payload` and optional `instructionMessage`. The second call returns `token`, `user_id`, `statusMessage`, `is_new_user`, and `authFlow`.

## Custom SIWE Example

```javascript
const { SailAPIClient, signMessage, getWalletAddress } = require("./example");

const client = new SailAPIClient(BASE_URL, PROJECT_ID, PAGE_ID);
const walletAddress = getWalletAddress(PRIVATE_KEY);

const session = await client.initiateSiweAuth(
  walletAddress,
  8453,
  null,
  "byWallet"
);

const signature = await signMessage(session.message, PRIVATE_KEY);

const auth = await client.completeSiweAuth(
  session.sessionId,
  signature,
  walletAddress,
  "byWallet"
);

console.log(auth.identityMode); // byWallet
console.log(auth.walletAddress); // issued wallet from Sail/Thirdweb flow
console.log(auth.accountToken);
```

## Legacy `byUser` Recovery

Use `byUser` only if the signer wallet already has a legacy mapping on the backend:

```javascript
const session = await client.initiateSiweAuth(walletAddress, 8453, null, "byUser");
const signature = await signMessage(session.message, PRIVATE_KEY);
const auth = await client.completeSiweAuth(
  session.sessionId,
  signature,
  walletAddress,
  "byUser"
);
```

If no legacy mapping exists, Sail rejects the request. `byUser` does not create a new legacy identity.

## Metrics Examples

All metrics endpoints return `{ message, result }`.

```javascript
const balanceMetrics = await client.getMetricsBalance();
console.log(balanceMetrics.message);
console.log(balanceMetrics.result);

const historyMetrics = await client.getMetricsHistory({ limit: 20 });
console.log(historyMetrics.result);
```

Available metrics helpers:

```javascript
await client.getMetricsBalance();
await client.getMetricsEarnings();
await client.getMetricsHistory({ limit: 20 });
await client.getMetricsPortfolio();
await client.getMetricsUserMetrics();
await client.getMetricsYield();
```

You can also use the generic helper:

```javascript
await client.getMetrics("yield");
await client.getMetrics("history", { metadata: 1 });
```

## Common API Calls

After authentication, the client supports:

```javascript
await client.getBalance();
await client.getDepositInfo();
await client.getWithdrawInfo();
await client.getPortfolioTotalBalance();
await client.getPortfolioTokens();
await client.getTierInfo();
await client.getPage();
await client.getAutomationStatus();
await client.getChatbots();
await client.getMetricsBalance();
await client.getMetricsYield();
```

Custom APIs are still available:

```javascript
await client.getCustomAPI("api_id", { foo: "bar" });
await client.postCustomAPI("api_id", { foo: "bar" });
```
