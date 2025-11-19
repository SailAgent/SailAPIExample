# Sail API - Getting Started Guide

Welcome to the Sail API! This guide will help you get started with the Sail API using your exported Sail wallet private key.

## Quick Start

Get started with the Sail API in 3 simple steps:

1. **Install dependencies** for your chosen language (Python or JavaScript)
2. **Export your private key** from your Sail wallet at [https://sail.money/manage-wallet/7702](https://sail.money/manage-wallet/7702)
3. **Configure your environment** and follow the language-specific guide:
   - [Python Guide](README_PYTHON.md)
   - [JavaScript Guide](README_JAVASCRIPT.md)

## Installation

### Python

1. **Install Python 3.7 or higher** (if not already installed)

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

   Or install manually:

   ```bash
   pip install eth-account requests python-dotenv
   ```

3. **Set up your environment**:

   ```bash
   cp example.env .env
   # Edit .env and add your private key
   ```

4. **Run the example**:

   ```bash
   python example.py
   ```

### JavaScript/Node.js

1. **Install Node.js 14.x or higher** (if not already installed)

2. **Install dependencies**:

   ```bash
   npm install
   ```

   Or using yarn:

   ```bash
   yarn install
   ```

3. **Set up your environment**:

   ```bash
   cp example.env .env
   # Edit .env and add your private key
   ```

4. **Run the example**:

   ```bash
   node example.js
   ```

   Or using npm:

   ```bash
   npm start
   ```

## Configuration

Before you begin, you'll need to configure the following:

- **API URL**: `https://app.sail.money/prod`
- **Project ID**: `sail`
- **Page ID**: `home`
- **Private Key**: Export from [https://sail.money/manage-wallet/7702](https://sail.money/manage-wallet/7702)

Copy `example.env` to `.env` and fill in your private key:

```bash
cp example.env .env
# Then edit .env and add your private key
```

## Authentication

All Sail API requests require authentication using your wallet's private key. Here's how it works:

### Step 1: Export Your Private Key

1. Go to [https://sail.money/manage-wallet/7702](https://sail.money/manage-wallet/7702)
2. Export your wallet's private key
3. **Keep this private key secure** - never commit it to version control or share it publicly

### Step 2: Sign the Authentication Message

Sign the message `"Authenticate SDK agent for Sail API"` with your wallet's private key. The language-specific guides show you exactly how to do this:

- [Python Authentication](README_PYTHON.md#authentication)
- [JavaScript Authentication](README_JAVASCRIPT.md#authentication)

### Step 3: Get Your JWT Token

Send a POST request to the authenticate endpoint:

```http
POST https://app.sail.money/prod/api/v1/projects/sail/pages/home/authenticate
Content-Type: application/json

{
  "walletAddress": "0x...",
  "signature": "0x..."
}
```

You'll receive a JWT token in the response:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": "507f1f77bcf86cd799439011",
  "message": "SDK agent authenticated successfully",
  "is_new_user": false
}
```

### Step 4: Use Your Token

Include the token in the `Authorization` header for all subsequent API requests:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## API Operations

Once authenticated, you can use the Sail API to interact with your agent. Here are the main operations:

### 💰 Deposits

Deposit funds into your agent's wallet:

- **Get deposit information**: See your current balance, permitted tokens, and tier information
- **Execute deposit**: Deposit funds (with optional pre/post hooks)
- **Pre-deposit hooks**: Run before deposit transaction
- **Post-deposit hooks**: Run after deposit transaction completes

📖 **Examples**: [Python](README_PYTHON.md#deposits) | [JavaScript](README_JAVASCRIPT.md#deposits)

**Endpoints:**
- `GET /api/v1/projects/sail/pages/home/deposit-info` - Get deposit information
- `POST /api/v1/projects/sail/pages/home/deposit` - Execute deposit
- `POST /api/v1/projects/sail/pages/home/deposit/pre-hooks` - Pre-deposit hooks
- `POST /api/v1/projects/sail/pages/home/deposit/post-hooks` - Post-deposit hooks

### 💸 Withdrawals

Withdraw funds from your agent's wallet:

- **Get withdraw information**: See your current balance, permitted tokens, and tier information
- **Execute withdrawal**: Withdraw funds (with optional pre/post hooks)
- **Pre-withdraw hooks**: Run before withdraw transaction
- **Post-withdraw hooks**: Run after withdraw transaction completes

📖 **Examples**: [Python](README_PYTHON.md#withdrawals) | [JavaScript](README_JAVASCRIPT.md#withdrawals)

**Endpoints:**
- `GET /api/v1/projects/sail/pages/home/withdraw-info` - Get withdraw information
- `POST /api/v1/projects/sail/pages/home/withdraw` - Execute withdrawal
- `POST /api/v1/projects/sail/pages/home/withdraw/pre-hooks` - Pre-withdraw hooks
- `POST /api/v1/projects/sail/pages/home/withdraw/post-hooks` - Post-withdraw hooks

### 🎮 Agent Control (Automation)

Control your agent's automation:

- **Check status**: See if your agent is running, paused, or stopped
- **Start automation**: Start your agent's automation job
- **Pause automation**: Pause your agent (can be resumed later)
- **Resume automation**: Resume a paused agent
- **Stop automation**: Stop your agent completely

📖 **Examples**: [Python](README_PYTHON.md#automation-control) | [JavaScript](README_JAVASCRIPT.md#automation-control)

**Endpoints:**
- `GET /api/v1/projects/sail/pages/home/automation/status` - Get automation status
- `POST /api/v1/projects/sail/pages/home/automation/start` - Start automation
- `POST /api/v1/projects/sail/pages/home/automation/pause` - Pause automation
- `POST /api/v1/projects/sail/pages/home/automation/resume` - Resume automation
- `POST /api/v1/projects/sail/pages/home/automation/stop` - Stop automation

### 💼 Balance & Portfolio

Get your agent's balance and portfolio information:

- **Get balance**: Query wallet balance for a specific token and chain
- **Get total portfolio balance**: Get your total portfolio balance across all tokens
- **Get portfolio tokens**: Get balances for all configured tokens in your portfolio

📖 **Examples**: [Python](README_PYTHON.md#balance--portfolio) | [JavaScript](README_JAVASCRIPT.md#balance--portfolio)

**Endpoints:**
- `GET /api/v1/projects/sail/pages/home/balance` - Get wallet balance (optional: `?tokenAddress=0x...&chainId=8453`)
- `GET /api/v1/projects/sail/pages/home/portfolio/total-balance` - Get total portfolio balance
- `GET /api/v1/projects/sail/pages/home/portfolio/tokens` - Get portfolio token balances

### 🔐 Authorization & Approvals Status

Check your agent's authorization and approval status:

- **Check remaining authorizations**: See how many authorizations you have remaining for session keys
- **Get permitted keys**: Get session keys that are available for signing

📖 **Examples**: [Python](README_PYTHON.md#authorization--approvals) | [JavaScript](README_JAVASCRIPT.md#authorization--approvals)

**Endpoints:**
- `GET /api/v1/projects/sail/pages/home/check-remaining-authorizations` - Check remaining authorizations
- `GET /api/v1/projects/sail/pages/home/get-permitted-keys-for-signing` - Get permitted keys for signing

### 🏆 Tier Information

Get your agent's active tier and information about all tiers:

- **Get tier info**: See your current tier, balance, and information about all available tiers
- **Balance until next tier**: See how much balance you need to reach the next tier

📖 **Examples**: [Python](README_PYTHON.md#tier-information) | [JavaScript](README_JAVASCRIPT.md#tier-information)

**Endpoints:**
- `GET /api/v1/projects/sail/pages/home/tier` - Get tier information

### 💬 Chatbot & Memories

Interact with your agent's chatbot and search through memories:

- **Get chatbots**: List all configured chatbots
- **Get chatbot memories**: Search through your chatbot's interaction memories (paginated)

📖 **Examples**: [Python](README_PYTHON.md#chatbot--memories) | [JavaScript](README_JAVASCRIPT.md#chatbot--memories)

**Endpoints:**
- `GET /api/v1/projects/sail/pages/home/chatbots` - Get list of chatbots
- `GET /api/v1/projects/sail/pages/home/chatbot-memories?graphId={id}&page=1&limit=10` - Get chatbot memories

## Language-Specific Guides

Choose your preferred language for detailed examples and implementation guides:

- **[Python Guide](README_PYTHON.md)** - Complete Python examples and usage guide
- **[JavaScript Guide](README_JAVASCRIPT.md)** - Complete JavaScript/Node.js examples and usage guide

## Error Handling

All endpoints may return standard HTTP error codes:

- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Missing or invalid authentication token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

Error responses typically include a `detail` field with more information:

```json
{
  "detail": "Project not found"
}
```

## Security Best Practices

1. **Never commit private keys**: Always use environment variables or secure key management
2. **Use HTTPS in production**: Always use HTTPS when connecting to production servers
3. **Validate responses**: Always validate API responses before using data
4. **Handle errors gracefully**: Implement proper error handling and retry logic
5. **Token expiration**: JWT tokens may expire; implement token refresh logic if needed

## Support

For issues, questions, or contributions, please refer to the main Sail repository documentation.
