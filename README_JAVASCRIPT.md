# Sail API - JavaScript/Node.js Guide

This guide provides detailed instructions for using the Sail API with JavaScript/Node.js.

> **📖 New to the Sail API?** Start with the [main README](README.md) for an overview of authentication and getting started.

## Installation

### Requirements

- Node.js 14.x or higher
- npm or yarn package manager

### Install Dependencies

#### Option 1: Using package.json (Recommended)

Using npm:

```bash
npm install
```

Using yarn:

```bash
yarn install
```

#### Option 2: Install manually

Using npm:

```bash
npm install ethers axios form-data dotenv
```

Using yarn:

```bash
yarn add ethers axios form-data dotenv
```

### Dependencies Explained

- **ethers**: Ethereum library for wallet management and message signing
- **axios**: HTTP client for making API requests
- **form-data**: Form data handling for file uploads in Node.js
- **dotenv**: Environment variable management (for loading `.env` files)

## Configuration

### Using Environment Variables (Recommended)

For better security, use environment variables. Copy `example.env` to `.env` and fill in your values:

```bash
cp example.env .env
# Then edit .env and add your private key
```

Then in your JavaScript code:

```javascript
require('dotenv').config(); // Loads environment variables from .env file

const BASE_URL = process.env.SAIL_API_URL || 'https://app.sail.money/prod';
const PROJECT_ID = process.env.SAIL_PROJECT_ID || 'sail';
const PAGE_ID = process.env.SAIL_PAGE_ID || 'home';
const PRIVATE_KEY = process.env.SAIL_PRIVATE_KEY || '';
```

### Direct Configuration

You can also configure directly in `example.js`:

```javascript
// Base URL of the Sail API server
const BASE_URL = 'https://app.sail.money/prod';

// Project and Page IDs
const PROJECT_ID = 'sail';
const PAGE_ID = 'home';

// Wallet configuration
// IMPORTANT: Never commit private keys to version control!
// Get your private key from: https://sail.money/manage-wallet/7702
const PRIVATE_KEY = '0x...'; // Replace with your private key
```

## Authentication

> **📖 For detailed authentication instructions, see the [main README](README.md#authentication).**

### Step 1: Export Your Private Key

1. Go to [https://sail.money/manage-wallet/7702](https://sail.money/manage-wallet/7702)
2. Export your wallet's private key
3. **Keep this private key secure** - never commit it to version control

### Step 2: Authenticate

```javascript
const { SailAPIClient, signMessage, getWalletAddress } = require('./example');
require('dotenv').config();

// Configuration
const BASE_URL = process.env.SAIL_API_URL || 'https://app.sail.money/prod';
const PROJECT_ID = process.env.SAIL_PROJECT_ID || 'sail';
const PAGE_ID = process.env.SAIL_PAGE_ID || 'home';
const PRIVATE_KEY = process.env.SAIL_PRIVATE_KEY || '';

// Get wallet address from private key
const walletAddress = getWalletAddress(PRIVATE_KEY);

// Initialize API client
const client = new SailAPIClient(BASE_URL, PROJECT_ID, PAGE_ID);

// Sign the authentication message
const authMessage = 'Authenticate SDK agent for Sail API';
const signature = await signMessage(authMessage, PRIVATE_KEY);

// Authenticate
const authResponse = await client.authenticate(walletAddress, signature);
console.log(`Token: ${authResponse.token}`);
console.log(`User ID: ${authResponse.user_id}`);
```

The client automatically stores the token for subsequent requests.

## API Operations

### Deposits

#### Get Deposit Information

Get your current balance, permitted tokens, and tier information:

```javascript
// Get deposit info
const depositInfo = await client.getDepositInfo();
console.log(`Current Balance: ${depositInfo.currentBalance}`);
console.log(`Permitted Tokens:`, depositInfo.permittedTokens || []);
```

#### Execute Deposit with Hooks

```javascript
// Get deposit info first
const depositInfo = await client.getDepositInfo();
console.log(`Current Balance: ${depositInfo.currentBalance}`);

// Run pre-deposit hooks (before deposit transaction)
const preHooksResult = await client.preDepositHooks(
    '1',  // amount (1 ETH)
    null,                    // tokenAddress (null for native)
    8453                     // chainId (Base chain)
);
console.log('Pre-deposit hooks:', preHooksResult);

// After deposit transaction completes, run post-deposit hooks
const postHooksResult = await client.postDepositHooks(
    '1',  // amount (1 ETH)
    '0x...',                // txHash (transaction hash from your deposit)
    null,                    // tokenAddress
    8453,                    // chainId
    'success'                // status
);
console.log('Post-deposit hooks:', postHooksResult);
```

#### Execute Deposit

```javascript
// Execute deposit directly (includes pre/post hooks)
const depositResult = await client.deposit(
    '1',  // amount (1 ETH)
    null,                    // tokenAddress (null for native)
    8453                     // chainId (Base chain)
);
console.log('Deposit result:', depositResult);
```

### Withdrawals

#### Get Withdraw Information

Get your current balance, permitted tokens, and tier information:

```javascript
// Get withdraw info
const withdrawInfo = await client.getWithdrawInfo();
console.log(`Current Balance: ${withdrawInfo.currentBalance}`);
console.log(`Permitted Tokens:`, withdrawInfo.permittedTokens || []);
```

#### Execute Withdrawal with Hooks

```javascript
// Get withdraw info first
const withdrawInfo = await client.getWithdrawInfo();
console.log(`Current Balance: ${withdrawInfo.currentBalance}`);

// Run pre-withdraw hooks (before withdraw transaction)
const preHooksResult = await client.preWithdrawHooks(
    '1',  // amount (1 ETH)
    '0x...',                // recipient address
    null,                    // tokenAddress (null for native)
    8453                     // chainId (Base chain)
);
console.log('Pre-withdraw hooks:', preHooksResult);

// After withdraw transaction completes, run post-withdraw hooks
const postHooksResult = await client.postWithdrawHooks(
    '1',  // amount (1 ETH)
    '0x...',                // txHash (transaction hash from your withdrawal)
    '0x...',                // recipient address
    null,                    // tokenAddress
    8453,                    // chainId
    'success'                // status
);
console.log('Post-withdraw hooks:', postHooksResult);
```

#### Execute Withdrawal

```javascript
// Execute withdrawal directly (includes pre/post hooks)
const withdrawResult = await client.withdraw(
    '1',  // amount (1 ETH)
    '0x...',                // recipient address
    null,                    // tokenAddress (null for native)
    8453                     // chainId (Base chain)
);
console.log('Withdraw result:', withdrawResult);
```

### Automation Control

Control your agent's automation (pause, play, start, stop):

#### Check Automation Status

```javascript
// Check automation status
const status = await client.getAutomationStatus();
console.log(`Status: ${status.status}`);
console.log(`Has Job: ${status.hasJob}`);
console.log(`Job ID: ${status.jobId || 'N/A'}`);
```

#### Start Automation

```javascript
// Check status first
const status = await client.getAutomationStatus();

// Start automation if not already running
if (!status.hasJob) {
    const result = await client.startAutomation(
        'your-graph-id',      // graphId
        'Automation prompt',  // prompt
        { param1: 'value1' }, // paramValues (optional)
        1                      // iterations (optional)
    );
    console.log(`Job ID: ${result.jobId}`);
    console.log(`Status: ${result.status}`);
}
```

#### Pause Automation

```javascript
// Pause automation (can be resumed later)
const result = await client.pauseAutomation();
console.log(`Status: ${result.status}`);
```

#### Resume Automation

```javascript
// Resume a paused automation
const result = await client.resumeAutomation();
console.log(`Status: ${result.status}`);
```

#### Stop Automation

```javascript
// Stop automation completely
const result = await client.stopAutomation();
console.log(`Status: ${result.status}`);
```

### Balance & Portfolio

#### Get Wallet Balance

Get balance for a specific token and chain:

```javascript
// Get balance for native token on Base
const balance = await client.getBalance(
    null,   // tokenAddress (null for native token)
    8453    // chainId (Base chain)
);
console.log(`Balance: ${balance.balance}`);
console.log(`Balance Formatted: ${balance.balanceFormatted}`);

// Get balance for a specific ERC20 token
const tokenBalance = await client.getBalance(
    '0x...',  // tokenAddress
    8453      // chainId
);
console.log(`Token Balance: ${tokenBalance.balance}`);
```

#### Get Total Portfolio Balance

Get your total portfolio balance across all tokens:

```javascript
// Get total portfolio balance
const totalBalance = await client.getPortfolioTotalBalance();
console.log(`Total Balance: ${totalBalance.balance}`);
console.log(`Total Balance Formatted: ${totalBalance.balanceFormatted}`);
```

#### Get Portfolio Token Balances

Get balances for all configured tokens in your portfolio:

```javascript
// Get all portfolio token balances
const portfolio = await client.getPortfolioTokens();
console.log(`Found ${portfolio.tokens.length} tokens`);

portfolio.tokens.forEach(token => {
    console.log(`${token.symbol}: ${token.balance} (Chain: ${token.chainName || token.chain})`);
});
```

### Authorization & Approvals

Check your agent's authorization and approval status:

#### Check Remaining Authorizations

```javascript
// Check remaining authorizations for session keys
const authStatus = await client.checkRemainingAuthorizations();
console.log(`Remaining Authorizations: ${authStatus.remainingAuthorizations || 0}`);
console.log(`Total Authorizations: ${authStatus.totalAuthorizations || 0}`);
```

#### Get Permitted Keys for Signing

```javascript
// Get session keys that are available for signing
const permittedKeys = await client.getPermittedKeysForSigning();
console.log(`Found ${permittedKeys.permittedKeys?.length || 0} permitted keys`);

permittedKeys.permittedKeys?.forEach(key => {
    console.log(`Key ID: ${key.id}`);
    console.log(`Key Address: ${key.address}`);
});
```

### Tier Information

Get your agent's active tier and information about all tiers:

```javascript
// Get tier information
const tierInfo = await client.getTierInfo();
console.log(`Current Tier: ${tierInfo.userTier.name}`);
console.log(`Tier Color: ${tierInfo.userTier.color}`);
console.log(`User Balance: ${tierInfo.userBalance}`);

// Get all tiers configuration
const tiersConfig = tierInfo.tiersConfig || {};
const tiers = tiersConfig.tiers || [];

tiers.forEach(tier => {
    console.log(`Tier: ${tier.name}, Min Balance: ${tier.minBalance}`);
});
```

### Chatbot & Memories

Interact with your agent's chatbot and search through memories:

#### Get Chatbots

```javascript
// Get list of configured chatbots
const chatbots = await client.getChatbots();
console.log(`Found ${chatbots.chatbots.length} chatbot(s)`);

chatbots.chatbots.forEach(bot => {
    console.log(`Chatbot: ${bot.name} (ID: ${bot.id}, Graph ID: ${bot.graphId})`);
});
```

#### Get Chatbot Memories

```javascript
// Get chatbots first
const chatbots = await client.getChatbots();

// Get memories for a specific chatbot
if (chatbots.chatbots.length > 0) {
    const chatbot = chatbots.chatbots[0];
    const graphId = chatbot.graphId;
    
    // Get memories (paginated)
    const memories = await client.getChatbotMemories(
        graphId,  // graphId
        1,        // page (1-indexed)
        20        // limit (items per page)
    );
    
    console.log(`Found ${memories.memories.length} memories`);
    console.log(`Total: ${memories.pagination.total}`);
    console.log(`Page: ${memories.pagination.page} of ${memories.pagination.totalPages}`);
    
    // Display memories
    memories.memories.forEach(memory => {
        console.log(`Memory ID: ${memory.id}`);
        console.log(`Question: ${memory.question || 'N/A'}`);
        console.log(`Result: ${(memory.result || 'N/A').substring(0, 100)}...`); // First 100 chars
        console.log(`Timestamp: ${memory.timestamp}`);
        console.log('---');
    });
}
```

### Vault Operations

Interact with vault information and share price history:

#### Get Vault Info

```javascript
// Get vault info with datetime strings (ISO 8601 format)
const vaultInfo = await client.getVaultInfo(
    '0x...',                    // Optional wallet address
    '2024-01-01T00:00:00Z',     // ISO 8601 datetime string
    '2024-12-31T23:59:59Z'      // ISO 8601 datetime string
);
console.log(`Vault Info: ${vaultInfo}`);

// Or use Unix timestamps
const startTimestamp = Math.floor(new Date('2024-01-01').getTime() / 1000);
const endTimestamp = Math.floor(new Date('2024-12-31').getTime() / 1000);

const vaultInfo2 = await client.getVaultInfo(
    '0x...',
    startTimestamp,  // Unix timestamp in seconds
    endTimestamp     // Unix timestamp in seconds
);
console.log(`Vault Info: ${vaultInfo2}`);
```

#### Get Share Price History

```javascript
// Get share price history with datetime strings (ISO 8601 format)
const priceHistory = await client.getSharePriceHistory(
    '0x1234...,0x5678...',      // Comma-separated vault addresses
    8453,                        // Base chain
    90,                          // Number of days (default: 90)
    '2024-01-01T00:00:00Z',     // ISO 8601 datetime string
    '2024-12-31T23:59:59Z'      // ISO 8601 datetime string
);
console.log('Share Price History:', priceHistory);

// Or use Unix timestamps
const startTimestamp = Math.floor(new Date('2024-01-01').getTime() / 1000);
const endTimestamp = Math.floor(new Date('2024-12-31').getTime() / 1000);

const priceHistory2 = await client.getSharePriceHistory(
    '0x1234...,0x5678...',
    8453,
    90,
    startTimestamp,  // Unix timestamp in seconds
    endTimestamp     // Unix timestamp in seconds
);
console.log('Share Price History:', priceHistory2);
```

## Error Handling

Always handle errors gracefully:

```javascript
try {
    const balance = await client.getBalance();
    console.log(`Balance: ${balance.balance}`);
} catch (error) {
    if (error.response) {
        // Server responded with error status
        const status = error.response.status;
        const data = error.response.data;
        
        if (status === 401) {
            console.error('Authentication failed. Please re-authenticate.');
            // Re-authenticate here
        } else if (status === 404) {
            console.error('Resource not found.');
        } else {
            console.error(`Error ${status}:`, data);
        }
    } else if (error.request) {
        // Request made but no response received
        console.error('No response received:', error.message);
    } else {
        // Error setting up request
        console.error('Error:', error.message);
    }
}
```

## Complete Example

Here's a complete example that demonstrates the full workflow:

```javascript
const { SailAPIClient, signMessage, getWalletAddress } = require('./example');
require('dotenv').config();

async function main() {
    // Configuration
    const BASE_URL = process.env.SAIL_API_URL || 'https://app.sail.money/prod';
    const PROJECT_ID = process.env.SAIL_PROJECT_ID || 'sail';
    const PAGE_ID = process.env.SAIL_PAGE_ID || 'home';
    const PRIVATE_KEY = process.env.SAIL_PRIVATE_KEY || '';
    
    // Initialize
    const walletAddress = getWalletAddress(PRIVATE_KEY);
    const client = new SailAPIClient(BASE_URL, PROJECT_ID, PAGE_ID);
    
    // Authenticate
    const authMessage = 'Authenticate SDK agent for Sail API';
    const signature = await signMessage(authMessage, PRIVATE_KEY);
    const authResponse = await client.authenticate(walletAddress, signature);
    console.log(`Authenticated as user: ${authResponse.user_id}`);
    
    // Get balance
    try {
        const balance = await client.getBalance();
        console.log(`Balance: ${balance.balance}`);
    } catch (error) {
        console.error(`Error getting balance: ${error.message}`);
    }
    
    // Get automation status
    try {
        const status = await client.getAutomationStatus();
        console.log(`Automation Status: ${status.status}`);
    } catch (error) {
        console.error(`Error getting automation status: ${error.message}`);
    }
    
    // Get tier info
    try {
        const tierInfo = await client.getTierInfo();
        console.log(`Current Tier: ${tierInfo.userTier.name}`);
    } catch (error) {
        console.error(`Error getting tier info: ${error.message}`);
    }
}

main().catch(console.error);
```

## ES6 Modules

If you're using ES6 modules, you can convert the example:

```javascript
// example.mjs
import { ethers } from 'ethers';
import axios from 'axios';
// ... rest of the code

export { SailAPIClient, signMessage, getWalletAddress };
```

Then import it:

```javascript
// main.mjs
import { SailAPIClient, signMessage, getWalletAddress } from './example.mjs';
// ... rest of the code
```

## TypeScript Support

You can add TypeScript types for better type safety:

```typescript
interface AuthResponse {
    token: string;
    user_id: string;
    message: string;
    is_new_user: boolean;
}

interface BalanceResponse {
    balance: string;
    balanceFormatted?: number;
    tokenAddress?: string;
    chainId?: number;
    timestamp: number;
}

// Use with type assertions
const authResponse = await client.authenticate(walletAddress, signature) as AuthResponse;
const balance = await client.getBalance() as BalanceResponse;
```

## Troubleshooting

### Common Issues

1. **Cannot find module 'ethers'**
   - Solution: Install dependencies with `npm install ethers axios form-data` or `yarn add ethers axios form-data`

2. **401 Unauthorized errors**
   - Solution: Make sure you've authenticated and the token is valid
   - Re-authenticate if the token has expired

3. **404 Not Found errors**
   - Solution: Verify your PROJECT_ID and PAGE_ID are correct (should be "sail" and "home")
   - Ensure the project and page exist on the server

4. **Connection errors**
   - Solution: Check that BASE_URL is correct (`https://app.sail.money/prod`)
   - Verify network connectivity

5. **Invalid signature errors**
   - Solution: Ensure you're signing the exact message: `"Authenticate SDK agent for Sail API"`
   - Verify your private key is correct (exported from https://sail.money/manage-wallet/7702)

6. **FormData is not defined (Node.js)**
   - Solution: The `form-data` package is already included in the dependencies. Make sure you've installed all dependencies: `npm install ethers axios form-data`

### Debugging

Enable verbose logging to see request/response details:

```javascript
// Enable axios request/response logging
axios.interceptors.request.use(request => {
    console.log('Request:', request.method, request.url, request.data);
    return request;
});

axios.interceptors.response.use(
    response => {
        console.log('Response:', response.status, response.data);
        return response;
    },
    error => {
        console.error('Error:', error.response?.status, error.response?.data);
        return Promise.reject(error);
    }
);
```

## Best Practices

1. **Use environment variables** for sensitive data like private keys
2. **Implement retry logic** for transient network errors
3. **Cache tokens** when possible to avoid re-authentication
4. **Validate responses** before using data
5. **Handle errors gracefully** with try/catch blocks
6. **Use async/await** for cleaner asynchronous code
7. **Add TypeScript types** for better type safety
8. **Write unit tests** for your API integration code

## Additional Resources

- [ethers.js documentation](https://docs.ethers.io/)
- [axios documentation](https://axios-http.com/)
- [Main Sail API Documentation](README.md)
