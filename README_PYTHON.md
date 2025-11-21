# Sail API - Python Guide

This guide provides detailed instructions for using the Sail API with Python.

> **📖 New to the Sail API?** Start with the [main README](README.md) for an overview of authentication and getting started.

## Installation

### Requirements

- Python 3.7 or higher
- pip (Python package manager)

### Install Dependencies

#### Option 1: Using requirements.txt (Recommended)

```bash
pip install -r requirements.txt
```

#### Option 2: Install manually

```bash
pip install eth-account requests python-dotenv
```

#### Option 3: Using a virtual environment (Recommended for isolation)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Dependencies Explained

- **eth-account**: Ethereum account management and message signing
- **requests**: HTTP library for making API requests
- **python-dotenv**: Environment variable management (for loading `.env` files)

## Configuration

### Using Environment Variables (Recommended)

For better security, use environment variables. Copy `example.env` to `.env` and fill in your values:

```bash
cp example.env .env
# Then edit .env and add your private key
```

Then in your Python code:

```python
import os

BASE_URL = os.getenv("SAIL_API_URL", "https://app.sail.money/prod")
PROJECT_ID = os.getenv("SAIL_PROJECT_ID", "sail")
PAGE_ID = os.getenv("SAIL_PAGE_ID", "home")
PRIVATE_KEY = os.getenv("SAIL_PRIVATE_KEY", "")
```

### Direct Configuration

You can also configure directly in `example.py`:

```python
# Base URL of the Sail API server
BASE_URL = "https://app.sail.money/prod"

# Project and Page IDs
PROJECT_ID = "sail"
PAGE_ID = "home"

# Wallet configuration
# IMPORTANT: Never commit private keys to version control!
# Get your private key from: https://sail.money/manage-wallet/7702
PRIVATE_KEY = "0x..."  # Replace with your private key
```

## Authentication

> **📖 For detailed authentication instructions, see the [main README](README.md#authentication).**

### Step 1: Export Your Private Key

1. Go to [https://sail.money/manage-wallet/7702](https://sail.money/manage-wallet/7702)
2. Export your wallet's private key
3. **Keep this private key secure** - never commit it to version control

### Step 2: Authenticate

```python
from example import SailAPIClient, sign_message, get_wallet_address
import os

# Configuration
BASE_URL = os.getenv("SAIL_API_URL", "https://app.sail.money/prod")
PROJECT_ID = os.getenv("SAIL_PROJECT_ID", "sail")
PAGE_ID = os.getenv("SAIL_PAGE_ID", "home")
PRIVATE_KEY = os.getenv("SAIL_PRIVATE_KEY", "")

# Get wallet address from private key
wallet_address = get_wallet_address(PRIVATE_KEY)

# Initialize API client
client = SailAPIClient(BASE_URL, PROJECT_ID, PAGE_ID)

# Sign the authentication message
auth_message = "Authenticate SDK agent for Sail API"
signature = sign_message(auth_message, PRIVATE_KEY)

# Authenticate
auth_response = client.authenticate(wallet_address, signature)
print(f"Token: {auth_response['token']}")
print(f"User ID: {auth_response['user_id']}")
```

The client automatically stores the token for subsequent requests.

## API Operations

### Deposits

#### Get Deposit Information

Get your current balance, permitted tokens, and tier information:

```python
# Get deposit info
deposit_info = client.get_deposit_info()
print(f"Current Balance: {deposit_info['currentBalance']}")
print(f"Permitted Tokens: {deposit_info.get('permittedTokens', [])}")
```

#### Execute Deposit with Hooks

```python
# Get deposit info first
deposit_info = client.get_deposit_info()
print(f"Current Balance: {deposit_info['currentBalance']}")

# Run pre-deposit hooks (before deposit transaction)
pre_hooks_result = client.pre_deposit_hooks(
    amount="1",  # 1 ETH
    token_address=None,             # None for native token
    chain_id=8453                   # Base chain
)
print(f"Pre-deposit hooks: {pre_hooks_result}")

# After deposit transaction completes, run post-deposit hooks
post_hooks_result = client.post_deposit_hooks(
    amount="1",  # 1 ETH
    tx_hash="0x...",                # Transaction hash from your deposit
    token_address=None,
    chain_id=8453,
    status="success"
)
print(f"Post-deposit hooks: {post_hooks_result}")
```

#### Execute Deposit

```python
# Execute deposit directly (includes pre/post hooks)
deposit_result = client.deposit(
    amount="1",  # 1 ETH
    token_address=None,             # None for native token
    chain_id=8453                   # Base chain
)
print(f"Deposit result: {deposit_result}")
```

### Withdrawals

#### Get Withdraw Information

Get your current balance, permitted tokens, and tier information:

```python
# Get withdraw info
withdraw_info = client.get_withdraw_info()
print(f"Current Balance: {withdraw_info['currentBalance']}")
print(f"Permitted Tokens: {withdraw_info.get('permittedTokens', [])}")
```

#### Execute Withdrawal with Hooks

```python
# Get withdraw info first
withdraw_info = client.get_withdraw_info()
print(f"Current Balance: {withdraw_info['currentBalance']}")

# Run pre-withdraw hooks (before withdraw transaction)
pre_hooks_result = client.pre_withdraw_hooks(
    amount="1",  # 1 ETH
    recipient="0x...",              # Recipient address
    token_address=None,             # None for native token
    chain_id=8453                   # Base chain
)
print(f"Pre-withdraw hooks: {pre_hooks_result}")

# After withdraw transaction completes, run post-withdraw hooks
post_hooks_result = client.post_withdraw_hooks(
    amount="1",  # 1 ETH
    tx_hash="0x...",                # Transaction hash from your withdrawal
    recipient="0x...",              # Recipient address
    token_address=None,
    chain_id=8453,
    status="success"
)
print(f"Post-withdraw hooks: {post_hooks_result}")
```

#### Execute Withdrawal

```python
# Execute withdrawal directly (includes pre/post hooks)
withdraw_result = client.withdraw(
    amount="1",  # 1 ETH
    recipient="0x...",              # Recipient address
    token_address=None,             # None for native token
    chain_id=8453                   # Base chain
)
print(f"Withdraw result: {withdraw_result}")
```

### Automation Control

Control your agent's automation (pause, play, start, stop):

#### Check Automation Status

```python
# Check automation status
status = client.get_automation_status()
print(f"Status: {status['status']}")
print(f"Has Job: {status['hasJob']}")
print(f"Job ID: {status.get('jobId')}")
```

#### Start Automation

```python
# Check status first
status = client.get_automation_status()

# Start automation if not already running
if not status['hasJob']:
    result = client.start_automation(
        graph_id="your-graph-id",
        prompt="Automation prompt",
        param_values={"param1": "value1"},  # Optional
        iterations=1                         # Optional
    )
    print(f"Job ID: {result['jobId']}")
    print(f"Status: {result['status']}")
```

#### Pause Automation

```python
# Pause automation (can be resumed later)
result = client.pause_automation()
print(f"Status: {result['status']}")
```

#### Resume Automation

```python
# Resume a paused automation
result = client.resume_automation()
print(f"Status: {result['status']}")
```

#### Stop Automation

```python
# Stop automation completely
result = client.stop_automation()
print(f"Status: {result['status']}")
```

### Balance & Portfolio

#### Get Wallet Balance

Get balance for a specific token and chain:

```python
# Get balance for native token on Base
balance = client.get_balance(
    token_address=None,  # None for native token
    chain_id=8453        # Base chain
)
print(f"Balance: {balance['balance']}")
print(f"Balance Formatted: {balance.get('balanceFormatted')}")

# Get balance for a specific ERC20 token
balance = client.get_balance(
    token_address="0x...",  # Token address
    chain_id=8453           # Chain ID
)
print(f"Token Balance: {balance['balance']}")
```

#### Get Total Portfolio Balance

Get your total portfolio balance across all tokens:

```python
# Get total portfolio balance
total_balance = client.get_portfolio_total_balance()
print(f"Total Balance: {total_balance['balance']}")
print(f"Total Balance Formatted: {total_balance.get('balanceFormatted')}")
```

#### Get Portfolio Token Balances

Get balances for all configured tokens in your portfolio:

```python
# Get all portfolio token balances
portfolio = client.get_portfolio_tokens()
print(f"Found {len(portfolio['tokens'])} tokens")

for token in portfolio['tokens']:
    print(f"{token['symbol']}: {token['balance']} (Chain: {token.get('chainName', token['chain'])})")
```

### Authorization & Approvals

Check your agent's authorization and approval status:

#### Check Remaining Authorizations

```python
# Check remaining authorizations for session keys
auth_status = client.check_remaining_authorizations()
print(f"Remaining Authorizations: {auth_status.get('remainingAuthorizations', 0)}")
print(f"Total Authorizations: {auth_status.get('totalAuthorizations', 0)}")
```

#### Get Permitted Keys for Signing

```python
# Get session keys that are available for signing
permitted_keys = client.get_permitted_keys_for_signing()
print(f"Found {len(permitted_keys.get('permittedKeys', []))} permitted keys")

for key in permitted_keys.get('permittedKeys', []):
    print(f"Key ID: {key.get('id')}")
    print(f"Key Address: {key.get('address')}")
```

### Tier Information

Get your agent's active tier and information about all tiers:

```python
# Get tier information
tier_info = client.get_tier_info()
print(f"Current Tier: {tier_info['userTier']['name']}")
print(f"Tier Color: {tier_info['userTier']['color']}")
print(f"User Balance: {tier_info['userBalance']}")

# Get all tiers configuration
tiers_config = tier_info.get('tiersConfig', {})
tiers = tiers_config.get('tiers', [])

for tier in tiers:
    print(f"Tier: {tier.get('name')}, Min Balance: {tier.get('minBalance')}")
```

### Chatbot & Memories

Interact with your agent's chatbot and search through memories:

#### Get Chatbots

```python
# Get list of configured chatbots
chatbots = client.get_chatbots()
print(f"Found {len(chatbots['chatbots'])} chatbot(s)")

for bot in chatbots['chatbots']:
    print(f"Chatbot: {bot['name']} (ID: {bot['id']}, Graph ID: {bot['graphId']})")
```

#### Get Chatbot Memories

```python
# Get chatbots first
chatbots = client.get_chatbots()

# Get memories for a specific chatbot
if chatbots['chatbots']:
    chatbot = chatbots['chatbots'][0]
    graph_id = chatbot['graphId']
    
    # Get memories (paginated)
    memories = client.get_chatbot_memories(
        graph_id=graph_id,
        page=1,      # Page number (1-indexed)
        limit=20     # Items per page
    )
    
    print(f"Found {len(memories['memories'])} memories")
    print(f"Total: {memories['pagination']['total']}")
    print(f"Page: {memories['pagination']['page']} of {memories['pagination']['totalPages']}")
    
    # Display memories
    for memory in memories['memories']:
        print(f"Memory ID: {memory.get('id')}")
        print(f"Question: {memory.get('question', 'N/A')}")
        print(f"Result: {memory.get('result', 'N/A')[:100]}...")  # First 100 chars
        print(f"Timestamp: {memory.get('timestamp')}")
        print("---")
```

### Vault Operations

Interact with vault information and share price history:

#### Get Vault Info

```python
from datetime import datetime

# Get vault info with datetime strings (ISO 8601 format)
vault_info = client.get_vault_info(
    wallet_address="0x...",  # Optional wallet address
    start_time="2024-01-01T00:00:00Z",  # ISO 8601 datetime string
    end_time="2024-12-31T23:59:59Z"     # ISO 8601 datetime string
)
print(f"Vault Info: {vault_info}")

# Or use Unix timestamps
import time
start_timestamp = int(time.mktime(datetime(2024, 1, 1).timetuple()))
end_timestamp = int(time.mktime(datetime(2024, 12, 31).timetuple()))

vault_info = client.get_vault_info(
    wallet_address="0x...",
    start_time=start_timestamp,  # Unix timestamp in seconds
    end_time=end_timestamp        # Unix timestamp in seconds
)
print(f"Vault Info: {vault_info}")
```

#### Get Share Price History

```python
from datetime import datetime

# Get share price history with datetime strings (ISO 8601 format)
price_history = client.get_share_price_history(
    vault_addresses="0x1234...,0x5678...",  # Comma-separated vault addresses
    chain_id=8453,                           # Base chain
    days=90,                                 # Number of days (default: 90)
    start_timestamp="2024-01-01T00:00:00Z",  # ISO 8601 datetime string
    end_timestamp="2024-12-31T23:59:59Z"     # ISO 8601 datetime string
)
print(f"Share Price History: {price_history}")

# Or use Unix timestamps
import time
start_timestamp = int(time.mktime(datetime(2024, 1, 1).timetuple()))
end_timestamp = int(time.mktime(datetime(2024, 12, 31).timetuple()))

price_history = client.get_share_price_history(
    vault_addresses="0x1234...,0x5678...",
    chain_id=8453,
    days=90,
    start_timestamp=start_timestamp,  # Unix timestamp in seconds
    end_timestamp=end_timestamp        # Unix timestamp in seconds
)
print(f"Share Price History: {price_history}")
```

## Error Handling

Always handle errors gracefully:

```python
try:
    balance = client.get_balance()
    print(f"Balance: {balance['balance']}")
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print("Authentication failed. Please re-authenticate.")
        # Re-authenticate here
    elif e.response.status_code == 404:
        print("Resource not found.")
    else:
        print(f"Error {e.response.status_code}: {e.response.text}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Complete Example

Here's a complete example that demonstrates the full workflow:

```python
from example import SailAPIClient, sign_message, get_wallet_address
import os

# Configuration
BASE_URL = os.getenv("SAIL_API_URL", "https://app.sail.money/prod")
PROJECT_ID = os.getenv("SAIL_PROJECT_ID", "sail")
PAGE_ID = os.getenv("SAIL_PAGE_ID", "home")
PRIVATE_KEY = os.getenv("SAIL_PRIVATE_KEY", "")

# Initialize
wallet_address = get_wallet_address(PRIVATE_KEY)
client = SailAPIClient(BASE_URL, PROJECT_ID, PAGE_ID)

# Authenticate
auth_message = "Authenticate SDK agent for Sail API"
signature = sign_message(auth_message, PRIVATE_KEY)
auth_response = client.authenticate(wallet_address, signature)
print(f"Authenticated as user: {auth_response['user_id']}")

# Get balance
try:
    balance = client.get_balance()
    print(f"Balance: {balance['balance']}")
except Exception as e:
    print(f"Error getting balance: {e}")

# Get automation status
try:
    status = client.get_automation_status()
    print(f"Automation Status: {status['status']}")
except Exception as e:
    print(f"Error getting automation status: {e}")

# Get tier info
try:
    tier_info = client.get_tier_info()
    print(f"Current Tier: {tier_info['userTier']['name']}")
except Exception as e:
    print(f"Error getting tier info: {e}")
```

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'eth_account'**
   - Solution: Install dependencies with `pip install eth-account requests`

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

### Debugging

Enable verbose logging to see request/response details:

```python
import logging
import requests

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Or enable requests debug logging
import http.client
http.client.HTTPConnection.debuglevel = 1
```

## Best Practices

1. **Use environment variables** for sensitive data like private keys
2. **Implement retry logic** for transient network errors
3. **Cache tokens** when possible to avoid re-authentication
4. **Validate responses** before using data
5. **Handle errors gracefully** with try/except blocks
6. **Use type hints** for better code documentation
7. **Write unit tests** for your API integration code

## Additional Resources

- [eth-account documentation](https://eth-account.readthedocs.io/)
- [requests documentation](https://requests.readthedocs.io/)
- [Main Sail API Documentation](README.md)
