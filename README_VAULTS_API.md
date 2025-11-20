# Sail API - BasisOS Vaults API Guide

This guide provides detailed instructions for using the BasisOS Vaults API endpoints with low-level HTTP requests in JavaScript and Python.

> **📖 New to the Sail API?** Start with the [main README](README.md) for an overview of authentication and getting started.

## Overview

The BasisOS Vaults API provides endpoints to query vault information and share price history. These endpoints are used by BasisOS/SDK to fetch vault data for analysis and display.

## Authentication

All BasisOS Vaults API requests require authentication using a JWT token. You must authenticate first using the authentication endpoint (see [main README](README.md#authentication)) to obtain a JWT token.

Include the token in the `Authorization` header for all requests:

```
Authorization: Bearer {your_jwt_token}
```

## Endpoints

### 1. Share Price History

Get historical share price data for one or more vaults.

**Endpoint:** `GET /api/v1/projects/{project_id}/pages/{page_id}/share-price-history`

#### Path Parameters

- `project_id` (string, required): The project ID (e.g., "sail")
- `page_id` (string, required): The page ID (e.g., "home")

#### Query Parameters

- `vaultAddresses` (string, required): Comma-separated list of vault addresses
- `chainId` (integer, required): Chain ID (e.g., 8453 for Base, 1 for Ethereum)
- `days` (integer, optional): Number of days of history to retrieve (default: 90)
- `startTimestamp` (integer, optional): Start timestamp in seconds (Unix epoch)
- `endTimestamp` (integer, optional): End timestamp in seconds (Unix epoch)

#### Response Format

```json
{
  "sharePriceHistories": [
    {
      "name": "Vault Name",
      "address": "0x...",
      "price_history": [
        [1696118400, 1.05],
        [1696204800, 1.06]
      ]
    }
  ],
  "rawOutput": {},
  "formatError": null
}
```

**Response Fields:**
- `sharePriceHistories` (array): List of share price history items
  - `name` (string): Vault name
  - `address` (string): Vault address
  - `price_history` (array): Array of `[timestamp, price]` tuples
- `rawOutput` (object, optional): Raw tool output if available
- `formatError` (string, optional): Error message if tool output format doesn't match expected format

#### JavaScript Example (using fetch)

```javascript
// Configuration
const BASE_URL = 'https://app.sail.money/prod';
const PROJECT_ID = 'sail';
const PAGE_ID = 'home';
const JWT_TOKEN = 'your_jwt_token_here'; // Get this from authentication endpoint

// Vault addresses (comma-separated)
const vaultAddresses = '0x1234...,0x5678...';
const chainId = 8453; // Base chain
const days = 90; // Optional, defaults to 90

// Build URL with query parameters
const url = new URL(`${BASE_URL}/api/v1/projects/${PROJECT_ID}/pages/${PAGE_ID}/share-price-history`);
url.searchParams.append('vaultAddresses', vaultAddresses);
url.searchParams.append('chainId', chainId.toString());
url.searchParams.append('days', days.toString());

// Optional: Add timestamp filters
// url.searchParams.append('startTimestamp', '1696118400');
// url.searchParams.append('endTimestamp', '1698796800');

// Make request
fetch(url.toString(), {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${JWT_TOKEN}`,
    'Content-Type': 'application/json'
  }
})
  .then(response => {
    if (!response.ok) {
      return response.json().then(err => Promise.reject(err));
    }
    return response.json();
  })
  .then(data => {
    console.log('Share Price Histories:', data.sharePriceHistories);
    console.log('Raw Output:', data.rawOutput);
    if (data.formatError) {
      console.warn('Format Error:', data.formatError);
    }
    
    // Process each vault's price history
    data.sharePriceHistories.forEach(vault => {
      console.log(`Vault: ${vault.name} (${vault.address})`);
      console.log(`Price History Points: ${vault.price_history.length}`);
      vault.price_history.forEach(([timestamp, price]) => {
        console.log(`  ${new Date(timestamp * 1000).toISOString()}: ${price}`);
      });
    });
  })
  .catch(error => {
    console.error('Error fetching share price history:', error);
    if (error.detail) {
      console.error('Error detail:', error.detail);
    }
  });
```

#### Python Example (using requests)

```python
import requests
from typing import Optional, List

# Configuration
BASE_URL = "https://app.sail.money/prod"
PROJECT_ID = "sail"
PAGE_ID = "home"
JWT_TOKEN = "your_jwt_token_here"  # Get this from authentication endpoint

# Vault addresses (comma-separated)
vault_addresses = "0x1234...,0x5678..."
chain_id = 8453  # Base chain
days = 90  # Optional, defaults to 90

# Build URL
url = f"{BASE_URL}/api/v1/projects/{PROJECT_ID}/pages/{PAGE_ID}/share-price-history"

# Query parameters
params = {
    "vaultAddresses": vault_addresses,
    "chainId": chain_id,
    "days": days
}

# Optional: Add timestamp filters
# params["startTimestamp"] = 1696118400
# params["endTimestamp"] = 1698796800

# Request headers
headers = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}

try:
    # Make request
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()  # Raise exception for bad status codes
    
    data = response.json()
    
    print("Share Price Histories:", data["sharePriceHistories"])
    print("Raw Output:", data.get("rawOutput"))
    if data.get("formatError"):
        print("Format Error:", data["formatError"])
    
    # Process each vault's price history
    for vault in data["sharePriceHistories"]:
        print(f"Vault: {vault['name']} ({vault['address']})")
        print(f"Price History Points: {len(vault['price_history'])}")
        for timestamp, price in vault["price_history"]:
            from datetime import datetime
            dt = datetime.fromtimestamp(timestamp)
            print(f"  {dt.isoformat()}: {price}")
            
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e.response.status_code}")
    try:
        error_detail = e.response.json()
        print(f"Error detail: {error_detail.get('detail', 'Unknown error')}")
    except:
        print(f"Error response: {e.response.text}")
except requests.exceptions.RequestException as e:
    print(f"Request error: {e}")
```

### 2. Vault Info

Get detailed information about a specific vault.

**Endpoint:** `GET /api/v1/projects/{project_id}/pages/{page_id}/vault-info`

#### Path Parameters

- `project_id` (string, required): The project ID (e.g., "sail")
- `page_id` (string, required): The page ID (e.g., "home")

#### Query Parameters

- `vaultAddress` (string, required): The vault address
- `chainId` (integer, required): Chain ID (e.g., 8453 for Base, 1 for Ethereum)

#### Response Format

```json
{
  "chain": "base",
  "address": "0x...",
  "name": "Vault Name",
  "protocol": "Protocol Name",
  "entry_cost_bps": 10,
  "exit_cost_bps": 10,
  "max_deposit_amount": 1000000000000.0,
  "risk_free_rate": 0.05,
  "last_updated_timestamp": 1696118400
}
```

**Response Fields:**
- `chain` (string): Chain name (e.g., "base", "ethereum")
- `address` (string): Vault address
- `name` (string): Vault name
- `protocol` (string): Protocol name
- `entry_cost_bps` (integer): Entry cost in basis points (1 bps = 0.01%)
- `exit_cost_bps` (integer): Exit cost in basis points
- `max_deposit_amount` (float): Maximum deposit amount
- `risk_free_rate` (float): Risk-free rate (e.g., 0.05 = 5%)
- `last_updated_timestamp` (integer): Last update timestamp in seconds (Unix epoch)

#### JavaScript Example (using fetch)

```javascript
// Configuration
const BASE_URL = 'https://app.sail.money/prod';
const PROJECT_ID = 'sail';
const PAGE_ID = 'home';
const JWT_TOKEN = 'your_jwt_token_here'; // Get this from authentication endpoint

// Vault details
const vaultAddress = '0x1234...';
const chainId = 8453; // Base chain

// Build URL with query parameters
const url = new URL(`${BASE_URL}/api/v1/projects/${PROJECT_ID}/pages/${PAGE_ID}/vault-info`);
url.searchParams.append('vaultAddress', vaultAddress);
url.searchParams.append('chainId', chainId.toString());

// Make request
fetch(url.toString(), {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${JWT_TOKEN}`,
    'Content-Type': 'application/json'
  }
})
  .then(response => {
    if (!response.ok) {
      return response.json().then(err => Promise.reject(err));
    }
    return response.json();
  })
  .then(data => {
    console.log('Vault Info:', data);
    console.log(`Vault: ${data.name}`);
    console.log(`Address: ${data.address}`);
    console.log(`Chain: ${data.chain}`);
    console.log(`Protocol: ${data.protocol}`);
    console.log(`Entry Cost: ${data.entry_cost_bps} bps (${data.entry_cost_bps / 100}%)`);
    console.log(`Exit Cost: ${data.exit_cost_bps} bps (${data.exit_cost_bps / 100}%)`);
    console.log(`Max Deposit: ${data.max_deposit_amount}`);
    console.log(`Risk-Free Rate: ${data.risk_free_rate * 100}%`);
    console.log(`Last Updated: ${new Date(data.last_updated_timestamp * 1000).toISOString()}`);
  })
  .catch(error => {
    console.error('Error fetching vault info:', error);
    if (error.detail) {
      console.error('Error detail:', error.detail);
    }
  });
```

#### Python Example (using requests)

```python
import requests
from datetime import datetime

# Configuration
BASE_URL = "https://app.sail.money/prod"
PROJECT_ID = "sail"
PAGE_ID = "home"
JWT_TOKEN = "your_jwt_token_here"  # Get this from authentication endpoint

# Vault details
vault_address = "0x1234..."
chain_id = 8453  # Base chain

# Build URL
url = f"{BASE_URL}/api/v1/projects/{PROJECT_ID}/pages/{PAGE_ID}/vault-info"

# Query parameters
params = {
    "vaultAddress": vault_address,
    "chainId": chain_id
}

# Request headers
headers = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}

try:
    # Make request
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()  # Raise exception for bad status codes
    
    data = response.json()
    
    print("Vault Info:", data)
    print(f"Vault: {data['name']}")
    print(f"Address: {data['address']}")
    print(f"Chain: {data['chain']}")
    print(f"Protocol: {data['protocol']}")
    print(f"Entry Cost: {data['entry_cost_bps']} bps ({data['entry_cost_bps'] / 100}%)")
    print(f"Exit Cost: {data['exit_cost_bps']} bps ({data['exit_cost_bps'] / 100}%)")
    print(f"Max Deposit: {data['max_deposit_amount']}")
    print(f"Risk-Free Rate: {data['risk_free_rate'] * 100}%")
    last_updated = datetime.fromtimestamp(data['last_updated_timestamp'])
    print(f"Last Updated: {last_updated.isoformat()}")
    
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e.response.status_code}")
    try:
        error_detail = e.response.json()
        print(f"Error detail: {error_detail.get('detail', 'Unknown error')}")
    except:
        print(f"Error response: {e.response.text}")
except requests.exceptions.RequestException as e:
    print(f"Request error: {e}")
```

## Complete Examples

### JavaScript Complete Example

```javascript
// Complete example: Authenticate and fetch vault data
const BASE_URL = 'https://app.sail.money/prod';
const PROJECT_ID = 'sail';
const PAGE_ID = 'home';
const PRIVATE_KEY = 'your_private_key_here';

// Step 1: Authenticate (see main README for full authentication example)
async function authenticate() {
  // ... authentication code ...
  // Returns JWT token
  return jwtToken;
}

// Step 2: Get share price history
async function getSharePriceHistory(token, vaultAddresses, chainId, days = 90) {
  const url = new URL(`${BASE_URL}/api/v1/projects/${PROJECT_ID}/pages/${PAGE_ID}/share-price-history`);
  url.searchParams.append('vaultAddresses', vaultAddresses);
  url.searchParams.append('chainId', chainId.toString());
  url.searchParams.append('days', days.toString());
  
  const response = await fetch(url.toString(), {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch share price history');
  }
  
  return await response.json();
}

// Step 3: Get vault info
async function getVaultInfo(token, vaultAddress, chainId) {
  const url = new URL(`${BASE_URL}/api/v1/projects/${PROJECT_ID}/pages/${PAGE_ID}/vault-info`);
  url.searchParams.append('vaultAddress', vaultAddress);
  url.searchParams.append('chainId', chainId.toString());
  
  const response = await fetch(url.toString(), {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch vault info');
  }
  
  return await response.json();
}

// Usage
(async () => {
  try {
    // Authenticate
    const token = await authenticate();
    
    // Get share price history for multiple vaults
    const priceHistory = await getSharePriceHistory(
      token,
      '0x1234...,0x5678...',
      8453,
      90
    );
    console.log('Price History:', priceHistory);
    
    // Get info for a single vault
    const vaultInfo = await getVaultInfo(token, '0x1234...', 8453);
    console.log('Vault Info:', vaultInfo);
  } catch (error) {
    console.error('Error:', error);
  }
})();
```

### Python Complete Example

```python
import requests
from typing import Dict, Any

# Configuration
BASE_URL = "https://app.sail.money/prod"
PROJECT_ID = "sail"
PAGE_ID = "home"
PRIVATE_KEY = "your_private_key_here"

# Step 1: Authenticate (see main README for full authentication example)
def authenticate() -> str:
    # ... authentication code ...
    # Returns JWT token
    return jwt_token

# Step 2: Get share price history
def get_share_price_history(
    token: str,
    vault_addresses: str,
    chain_id: int,
    days: int = 90
) -> Dict[str, Any]:
    url = f"{BASE_URL}/api/v1/projects/{PROJECT_ID}/pages/{PAGE_ID}/share-price-history"
    params = {
        "vaultAddresses": vault_addresses,
        "chainId": chain_id,
        "days": days
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()

# Step 3: Get vault info
def get_vault_info(token: str, vault_address: str, chain_id: int) -> Dict[str, Any]:
    url = f"{BASE_URL}/api/v1/projects/{PROJECT_ID}/pages/{PAGE_ID}/vault-info"
    params = {
        "vaultAddress": vault_address,
        "chainId": chain_id
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()

# Usage
if __name__ == "__main__":
    try:
        # Authenticate
        token = authenticate()
        
        # Get share price history for multiple vaults
        price_history = get_share_price_history(
            token,
            "0x1234...,0x5678...",
            8453,
            90
        )
        print("Price History:", price_history)
        
        # Get info for a single vault
        vault_info = get_vault_info(token, "0x1234...", 8453)
        print("Vault Info:", vault_info)
    except Exception as e:
        print(f"Error: {e}")
```

## Error Handling

### Common HTTP Status Codes

- `400 Bad Request`: Invalid request parameters (e.g., missing required query params)
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: Insufficient permissions (page is private and user doesn't have access)
- `404 Not Found`: Project, page, or tool/graph not found
- `500 Internal Server Error`: Server error or tool execution failure

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### JavaScript Error Handling

```javascript
fetch(url, {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
  .then(response => {
    if (!response.ok) {
      // Try to parse error response
      return response.json()
        .then(error => {
          // Handle specific error codes
          if (response.status === 401) {
            throw new Error('Authentication failed. Please re-authenticate.');
          } else if (response.status === 403) {
            throw new Error('Access denied. This page is private.');
          } else if (response.status === 404) {
            throw new Error('Resource not found: ' + (error.detail || 'Unknown'));
          } else {
            throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
          }
        })
        .catch(() => {
          // If error response is not JSON, use status text
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        });
    }
    return response.json();
  })
  .then(data => {
    // Handle successful response
    console.log('Success:', data);
  })
  .catch(error => {
    // Handle all errors
    console.error('Request failed:', error.message);
  });
```

### Python Error Handling

```python
try:
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()
    # Handle successful response
    print('Success:', data)
except requests.exceptions.HTTPError as e:
    status_code = e.response.status_code
    try:
        error_detail = e.response.json()
        error_message = error_detail.get('detail', 'Unknown error')
    except:
        error_message = e.response.text or str(e)
    
    # Handle specific error codes
    if status_code == 401:
        print('Error: Authentication failed. Please re-authenticate.')
    elif status_code == 403:
        print('Error: Access denied. This page is private.')
    elif status_code == 404:
        print(f'Error: Resource not found: {error_message}')
    else:
        print(f'Error: HTTP {status_code}: {error_message}')
except requests.exceptions.RequestException as e:
    print(f'Request error: {e}')
```

## Notes

1. **Tool/Graph Configuration**: These endpoints require that a tool or graph is configured in the page's SDK data config. If not configured, you'll receive a 400 error with a message indicating that no tool or graph is configured.

2. **Wallet Address**: The wallet address is automatically extracted from the authenticated JWT token. You don't need to (and shouldn't) pass it as a parameter.

3. **Chain IDs**: Common chain IDs:
   - Ethereum Mainnet: 1
   - Base: 8453
   - Arbitrum: 42161
   - Optimism: 10
   - Polygon: 137

4. **Price History Format**: The `price_history` field contains an array of `[timestamp, price]` tuples where:
   - `timestamp` is a Unix timestamp in seconds
   - `price` is a floating-point number representing the share price

5. **Basis Points**: Costs are returned in basis points (bps). To convert to percentage, divide by 100 (e.g., 10 bps = 0.10%).

## Additional Resources

- [Main Sail API Documentation](README.md)
- [Python Guide](README_PYTHON.md)
- [JavaScript Guide](README_JAVASCRIPT.md)

