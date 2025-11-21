"""
SailBE SDK API Example - Python

This script demonstrates how to:
1. Authenticate using wallet signatures
2. Use JWT tokens for subsequent API requests
3. Call all available SDK endpoints

Requirements:
    pip install eth-account requests
"""

import requests
from eth_account import Account
from eth_account.messages import encode_defunct
from typing import Optional, Dict, Any, List
import json


# ============================================================================
# CONFIGURATION
# ============================================================================

# Base URL of the Sail API server
# Production API URL: https://app.sail.money/prod
BASE_URL = "https://app.sail.money/prod"

# Project and Page IDs
# Default values for Sail production
PROJECT_ID = "sail"
PAGE_ID = "home"

# Wallet configuration
# IMPORTANT: Never commit private keys to version control!
# Get your private key from: https://sail.money/manage-wallet/7702
# Use environment variables or secure key management in production
PRIVATE_KEY = "0x" + "0" * 64  # Replace with your private key
WALLET_ADDRESS = None  # Will be derived from private key


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def sign_message(message: str, private_key: str) -> str:
    """
    Sign a message using Ethereum private key.
    
    Args:
        message: The message to sign
        private_key: Private key in hex format (with or without 0x prefix)
        
    Returns:
        Signature in hex format
    """
    # Ensure private key has 0x prefix
    if not private_key.startswith("0x"):
        private_key = "0x" + private_key
    
    # Create account from private key
    account = Account.from_key(private_key)
    
    # Encode message for signing
    message_encoded = encode_defunct(text=message)
    
    # Sign message
    signed_message = account.sign_message(message_encoded)
    
    # Return signature
    return signed_message.signature.hex()


def get_wallet_address(private_key: str) -> str:
    """
    Get wallet address from private key.
    
    Args:
        private_key: Private key in hex format
        
    Returns:
        Wallet address in hex format
    """
    if not private_key.startswith("0x"):
        private_key = "0x" + private_key
    
    account = Account.from_key(private_key)
    return account.address


# ============================================================================
# API CLIENT CLASS
# ============================================================================

class SailAPIClient:
    """Client for interacting with SailBE SDK API."""
    
    def __init__(self, base_url: str, project_id: str, page_id: str, token: Optional[str] = None):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the API server
            project_id: Project ID
            page_id: Page ID
            token: Optional JWT token (if already authenticated)
        """
        self.base_url = base_url.rstrip("/")
        self.project_id = project_id
        self.page_id = page_id
        self.token = token
        self.base_path = f"/api/v1/projects/{project_id}/pages/{page_id}"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make an API request.
        
        Args:
            method: HTTP method (GET, POST, PUT, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            Response JSON as dictionary
        """
        url = f"{self.base_url}{self.base_path}{endpoint}"
        headers = self._get_headers()
        
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))
        
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()
    
    # ========================================================================
    # AUTHENTICATION
    # ========================================================================
    
    def authenticate(self, wallet_address: str, signature: str) -> Dict[str, Any]:
        """
        Authenticate using wallet signature.
        
        Args:
            wallet_address: Wallet address
            signature: Signature of the authentication message
            
        Returns:
            Authentication response with token
        """
        url = f"{self.base_url}{self.base_path}/authenticate"
        payload = {
            "walletAddress": wallet_address,
            "signature": signature
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        
        # Store token for future requests
        self.token = result.get("token")
        
        return result
    
    # ========================================================================
    # BALANCE
    # ========================================================================
    
    def get_balance(
        self,
        token_address: Optional[str] = None,
        chain_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get balance for a wallet.
        Wallet address is extracted from JWT token, not from parameters.
        
        Args:
            token_address: Optional token address
            chain_id: Optional chain ID
            
        Returns:
            Balance information
        """
        params = {}
        if token_address:
            params["tokenAddress"] = token_address
        if chain_id:
            params["chainId"] = chain_id
        
        return self._request("GET", "/balance", params=params)
    
    # ========================================================================
    # DEPOSIT
    # ========================================================================
    
    def deposit(
        self,
        amount: str,
        token_address: Optional[str] = None,
        chain_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Deposit funds.
        Wallet address is extracted from JWT token, not from parameters.
        
        Args:
            amount: Amount to deposit (human-readable format, e.g., '1' for 1 ETH, '10' for 10 USDC)
            token_address: Optional token address
            chain_id: Optional chain ID
            
        Returns:
            Deposit response
        """
        payload = {
            "amount": amount
        }
        if token_address:
            payload["tokenAddress"] = token_address
        if chain_id:
            payload["chainId"] = chain_id
        
        return self._request("POST", "/deposit", json=payload)
    
    def get_deposit_info(self) -> Dict[str, Any]:
        """
        Get deposit information.
        Wallet address is extracted from JWT token, not from parameters.
        
        Returns:
            Deposit info including balance, permitted tokens, etc.
        """
        return self._request("GET", "/deposit-info")
    
    def pre_deposit_hooks(
        self,
        amount: str,
        token_address: Optional[str] = None,
        chain_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute pre-deposit hooks.
        Wallet address is extracted from JWT token, not from parameters.
        
        Args:
            amount: Amount to deposit (human-readable format, e.g., '1' for 1 ETH, '10' for 10 USDC)
            token_address: Optional token address
            chain_id: Optional chain ID
            
        Returns:
            Pre-deposit hooks response
        """
        payload = {
            "amount": amount
        }
        if token_address:
            payload["tokenAddress"] = token_address
        if chain_id:
            payload["chainId"] = chain_id
        
        return self._request("POST", "/deposit/pre-hooks", json=payload)
    
    def post_deposit_hooks(
        self,
        amount: str,
        tx_hash: str,
        token_address: Optional[str] = None,
        chain_id: Optional[int] = None,
        status: str = "success"
    ) -> Dict[str, Any]:
        """
        Execute post-deposit hooks.
        Wallet address is extracted from JWT token, not from parameters.
        
        Args:
            amount: Amount that was deposited (human-readable format, e.g., '1' for 1 ETH, '10' for 10 USDC)
            tx_hash: Transaction hash
            token_address: Optional token address
            chain_id: Optional chain ID
            status: Transaction status ("success" or "error")
            
        Returns:
            Post-deposit hooks response
        """
        payload = {
            "amount": amount,
            "txHash": tx_hash,
            "status": status
        }
        if token_address:
            payload["tokenAddress"] = token_address
        if chain_id:
            payload["chainId"] = chain_id
        
        return self._request("POST", "/deposit/post-hooks", json=payload)
    
    # ========================================================================
    # WITHDRAW
    # ========================================================================
    
    def withdraw(
        self,
        amount: str,
        token_address: Optional[str] = None,
        chain_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Withdraw funds.
        Wallet address is extracted from JWT token, not from parameters.
        
        Args:
            amount: Amount to withdraw (human-readable format, e.g., '1' for 1 ETH, '10' for 10 USDC)
            token_address: Optional token address
            chain_id: Optional chain ID
            
        Returns:
            Withdraw response
        """
        payload = {
            "amount": amount
        }
        if token_address:
            payload["tokenAddress"] = token_address
        if chain_id:
            payload["chainId"] = chain_id
        
        return self._request("POST", "/withdraw", json=payload)
    
    def get_withdraw_info(self) -> Dict[str, Any]:
        """
        Get withdraw information.
        Wallet address is extracted from JWT token, not from parameters.
        
        Returns:
            Withdraw info including balance, permitted tokens, etc.
        """
        return self._request("GET", "/withdraw-info")
    
    def pre_withdraw_hooks(
        self,
        amount: str,
        recipient: str,
        token_address: Optional[str] = None,
        chain_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute pre-withdraw hooks.
        Wallet address is extracted from JWT token, not from parameters.
        
        Args:
            amount: Amount to withdraw (human-readable format, e.g., '1' for 1 ETH, '10' for 10 USDC)
            recipient: Recipient address for the withdrawal
            token_address: Optional token address
            chain_id: Optional chain ID
            
        Returns:
            Pre-withdraw hooks response
        """
        payload = {
            "amount": amount,
            "recipient": recipient
        }
        if token_address:
            payload["tokenAddress"] = token_address
        if chain_id:
            payload["chainId"] = chain_id
        
        return self._request("POST", "/withdraw/pre-hooks", json=payload)
    
    def post_withdraw_hooks(
        self,
        amount: str,
        tx_hash: str,
        recipient: str,
        token_address: Optional[str] = None,
        chain_id: Optional[int] = None,
        status: str = "success"
    ) -> Dict[str, Any]:
        """
        Execute post-withdraw hooks.
        Wallet address is extracted from JWT token, not from parameters.
        
        Args:
            amount: Amount that was withdrawn (human-readable format, e.g., '1' for 1 ETH, '10' for 10 USDC)
            tx_hash: Transaction hash
            recipient: Recipient address for the withdrawal
            token_address: Optional token address
            chain_id: Optional chain ID
            status: Transaction status ("success" or "error")
            
        Returns:
            Post-withdraw hooks response
        """
        payload = {
            "amount": amount,
            "txHash": tx_hash,
            "recipient": recipient,
            "status": status
        }
        if token_address:
            payload["tokenAddress"] = token_address
        if chain_id:
            payload["chainId"] = chain_id
        
        return self._request("POST", "/withdraw/post-hooks", json=payload)
    
    # ========================================================================
    # PORTFOLIO
    # ========================================================================
    
    def get_portfolio_total_balance(self) -> Dict[str, Any]:
        """
        Get total portfolio balance.
        Wallet address is extracted from JWT token, not from parameters.
        
        Returns:
            Total portfolio balance
        """
        return self._request("GET", "/portfolio/total-balance")
    
    def get_portfolio_tokens(self) -> Dict[str, Any]:
        """
        Get portfolio token balances.
        Wallet address is extracted from JWT token, not from parameters.
        
        Returns:
            List of token balances
        """
        return self._request("GET", "/portfolio/tokens")
    
    # ========================================================================
    # SESSION KEYS
    # ========================================================================
    
    def sign_permitted_keys(
        self,
        wallet_address: str,
        signatures: Dict[str, str],
        session_specs: Dict[str, Dict[str, Any]],
        owner_eoa: Optional[str] = None,
        backend_wallet_transaction_hashes: Optional[Dict[str, str]] = None,
        approval_transaction_hashes: Optional[Dict[str, str]] = None,
        approvals: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Sign permitted session keys.
        
        Args:
            wallet_address: Smart account address
            signatures: Dictionary mapping sessionKeyId to signature
            session_specs: Dictionary mapping sessionKeyId to sessionSpec
            owner_eoa: Optional EOA owner address (for ERC-7702)
            backend_wallet_transaction_hashes: Optional transaction hashes
            approval_transaction_hashes: Optional approval transaction hashes
            approvals: Optional list of approvals
            
        Returns:
            Sign permitted keys response
        """
        payload = {
            "walletAddress": wallet_address,
            "signatures": signatures,
            "sessionSpecs": session_specs
        }
        if owner_eoa:
            payload["ownerEOA"] = owner_eoa
        if backend_wallet_transaction_hashes:
            payload["backendWalletTransactionHashes"] = backend_wallet_transaction_hashes
        if approval_transaction_hashes:
            payload["approvalTransactionHashes"] = approval_transaction_hashes
        if approvals:
            payload["approvals"] = approvals
        
        return self._request("POST", "/sign-permitted-keys", json=payload)
    
    def get_permitted_keys_for_signing(self) -> Dict[str, Any]:
        """
        Get permitted keys available for signing.
        Wallet address is extracted from JWT token, not from parameters.
        
        Returns:
            Permitted keys information
        """
        return self._request("GET", "/get-permitted-keys-for-signing")
    
    def check_remaining_authorizations(self) -> Dict[str, Any]:
        """
        Check remaining authorizations.
        Wallet address is extracted from JWT token, not from parameters.
        
        Returns:
            Remaining authorizations information
        """
        return self._request("GET", "/check-remaining-authorizations")
    
    def get_session_keys_display(self) -> Dict[str, Any]:
        """
        Get session keys display information.
        Wallet address is extracted from JWT token, not from parameters.
        
        Returns:
            Session keys display information
        """
        return self._request("GET", "/session-keys-display")
    
    def enable_delegation(
        self,
        chain_id: int,
        delegation_data: str
    ) -> Dict[str, Any]:
        """
        Enable delegation.
        Wallet address is extracted from JWT token, not from parameters.
        
        Args:
            chain_id: Chain ID
            delegation_data: Encoded enableDelegation transaction data (hex string with 0x prefix)
            
        Returns:
            Enable delegation response
        """
        payload = {
            "chainId": chain_id,
            "delegationData": delegation_data
        }
        
        return self._request("POST", "/enable-delegation", json=payload)
    
    def check_bulk_authorization_status(
        self,
        session_key_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Check bulk authorization status for session keys.
        Wallet address is extracted from JWT token, not from parameters.
        
        Args:
            session_key_ids: List of session key IDs
            
        Returns:
            Bulk authorization status
        """
        payload = {
            "sessionKeyIds": session_key_ids
        }
        
        # This endpoint is at a different path
        url = f"{self.base_url}/api/v1/session-key/check-bulk-authorization-status"
        headers = self._get_headers()
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    
    # ========================================================================
    # AUTOMATION
    # ========================================================================
    
    def get_automation_status(self) -> Dict[str, Any]:
        """
        Get automation job status.
        Wallet address is extracted from JWT token, not from parameters.
        
        Returns:
            Automation status
        """
        return self._request("GET", "/automation/status")
    
    def start_automation(
        self,
        graph_id: str,
        prompt: str,
        param_values: Optional[Dict[str, Any]] = None,
        iterations: Optional[int] = 1,
        branch_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Start automation job.
        Wallet address is extracted from JWT token, not from parameters.
        
        Args:
            graph_id: Graph ID to run
            prompt: Prompt/message for the graph
            param_values: Optional parameter values
            iterations: Number of iterations
            branch_id: Optional branch ID
            
        Returns:
            Start automation response
        """
        payload = {
            "graphId": graph_id,
            "prompt": prompt,
            "iterations": iterations
        }
        if param_values:
            payload["paramValues"] = param_values
        if branch_id:
            payload["branchId"] = branch_id
        
        return self._request("POST", "/automation/start", json=payload)
    
    def pause_automation(self) -> Dict[str, Any]:
        """
        Pause automation job.
        Wallet address is extracted from JWT token, not from parameters.
        
        Returns:
            Pause automation response
        """
        return self._request("POST", "/automation/pause")
    
    def resume_automation(self) -> Dict[str, Any]:
        """
        Resume automation job.
        Wallet address is extracted from JWT token, not from parameters.
        
        Returns:
            Resume automation response
        """
        return self._request("POST", "/automation/resume")
    
    def stop_automation(self) -> Dict[str, Any]:
        """
        Stop automation job.
        Wallet address is extracted from JWT token, not from parameters.
        
        Returns:
            Stop automation response
        """
        return self._request("POST", "/automation/stop")
    
    # ========================================================================
    # VAULT
    # ========================================================================
    
    def get_share_price_history(
        self,
        vault_addresses: str,  # Comma-separated list
        chain_id: int,
        days: Optional[int] = 90,
        start_timestamp: Optional[int] = None,
        end_timestamp: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get share price history for vaults.
        Wallet address is extracted from JWT token, not from parameters.
        
        Args:
            vault_addresses: Comma-separated list of vault addresses
            chain_id: Chain ID
            days: Number of days (default: 90)
            start_timestamp: Optional start datetime (ISO 8601 string) or Unix timestamp in seconds
            end_timestamp: Optional end datetime (ISO 8601 string) or Unix timestamp in seconds
            
        Returns:
            Share price history
        """
        params = {
            "vaultAddresses": vault_addresses,
            "chainId": chain_id,
            "days": days
        }
        if start_timestamp:
            params["startTimestamp"] = start_timestamp
        if end_timestamp:
            params["endTimestamp"] = end_timestamp
        
        return self._request("GET", "/share-price-history", params=params)
    
    def get_vault_info(
        self,
        wallet_address: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> float:
        """
        Get vault information.
        Vault address and chain ID are configured in the tool/graph, not passed as parameters.
        Wallet address is extracted from JWT token, not from parameters.
        
        Args:
            wallet_address: Optional wallet address (only passed to tool if provided)
            start_time: Optional start datetime (ISO 8601 string) or Unix timestamp in seconds
            end_time: Optional end datetime (ISO 8601 string) or Unix timestamp in seconds
            
        Returns:
            Vault information as a simple number (e.g., 10.31)
        """
        params = {}
        if wallet_address:
            params["walletAddress"] = wallet_address
        if start_time is not None:
            params["startTime"] = start_time
        if end_time is not None:
            params["endTime"] = end_time
        
        return self._request("GET", "/vault-info", params=params)
    
    # ========================================================================
    # CHATBOT
    # ========================================================================
    
    def get_chatbots(self) -> Dict[str, Any]:
        """
        Get list of chatbots.
        Wallet address is extracted from JWT token, not from parameters.
        
        Returns:
            List of chatbots
        """
        return self._request("GET", "/chatbots")
    
    def get_chatbot_memories(
        self,
        graph_id: str,
        page: Optional[int] = 1,
        limit: Optional[int] = 20
    ) -> Dict[str, Any]:
        """
        Get chatbot memories.
        Wallet address is extracted from JWT token, not from parameters.
        
        Args:
            graph_id: Graph ID (chatbot graph ID)
            page: Page number (default: 1)
            limit: Items per page (default: 20)
            
        Returns:
            Chatbot memories
        """
        params = {
            "graphId": graph_id,
            "page": page,
            "limit": limit
        }
        
        return self._request("GET", "/chatbot-memories", params=params)
    
    # ========================================================================
    # GRAPH
    # ========================================================================
    
    def run_graph(
        self,
        graph_id: str,
        prompt: str,
        param_values: Optional[Dict[str, Any]] = None,
        iterations: Optional[int] = 1,
        branch_id: Optional[str] = None,
        include_context_report: Optional[bool] = False,
        context_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run a graph execution.
        Wallet address is extracted from JWT token, not from parameters.
        
        Args:
            graph_id: Graph ID
            prompt: User prompt/message
            param_values: Optional parameter values
            iterations: Number of iterations (default: 1)
            branch_id: Optional branch ID
            include_context_report: Include context report
            context_data: Optional context data
            
        Returns:
            Graph execution results
        """
        payload = {
            "id": graph_id,
            "prompt": prompt,
            "iterations": iterations,
            "includeContextReport": include_context_report
        }
        if param_values:
            payload["paramValues"] = param_values
        if branch_id:
            payload["branchId"] = branch_id
        if context_data:
            payload["contextData"] = context_data
        
        return self._request("POST", "/run-graph", json=payload)
    
    # ========================================================================
    # PROFILE
    # ========================================================================
    
    def get_profile(self) -> Dict[str, Any]:
        """
        Get user profile.
        Wallet address is extracted from JWT token, not from parameters.
        
        Returns:
            User profile
        """
        return self._request("GET", "/profile")
    
    def update_profile(
        self,
        profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update user profile.
        Wallet address is extracted from JWT token, not from parameters.
        
        Args:
            profile_data: Profile data to update
            
        Returns:
            Updated profile
        """
        return self._request("PUT", "/profile", json=profile_data)
    
    def upload_profile_avatar(
        self,
        file_path: str
    ) -> Dict[str, Any]:
        """
        Upload profile avatar.
        Wallet address is extracted from JWT token, not from parameters.
        
        Args:
            file_path: Path to image file
            
        Returns:
            Upload response
        """
        url = f"{self.base_url}{self.base_path}/profile/avatar"
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(url, headers=headers, files=files)
            response.raise_for_status()
            return response.json()
    
    def upload_profile_banner(
        self,
        file_path: str
    ) -> Dict[str, Any]:
        """
        Upload profile banner.
        Wallet address is extracted from JWT token, not from parameters.
        
        Args:
            file_path: Path to image file
            
        Returns:
            Upload response
        """
        url = f"{self.base_url}{self.base_path}/profile/banner"
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(url, headers=headers, files=files)
            response.raise_for_status()
            return response.json()
    
    # ========================================================================
    # PAGE
    # ========================================================================
    
    def get_page(self) -> Dict[str, Any]:
        """
        Get page information.
        
        Returns:
            Page data including title, project info, authConfig, themeConfig
        """
        return self._request("GET", "/page")
    
    def get_pages(
        self,
        project_id: Optional[str] = None,
        limit: Optional[int] = 100,
        offset: Optional[int] = 0
    ) -> Dict[str, Any]:
        """
        Get list of pages.
        
        Args:
            project_id: Optional project ID filter
            limit: Maximum number of results (default: 100)
            offset: Offset for pagination (default: 0)
            
        Returns:
            List of pages
        """
        params = {"limit": limit, "offset": offset}
        if project_id:
            params["projectId"] = project_id
        
        # This endpoint is at a different path
        url = f"{self.base_url}/api/v1/pages"
        headers = self._get_headers()
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    
    # ========================================================================
    # TIER
    # ========================================================================
    
    def get_tier_info(self) -> Dict[str, Any]:
        """
        Get tier information.
        Wallet address is extracted from JWT token, not from parameters.
        
        Returns:
            Tier information including user tier, eligible tiers, etc.
        """
        return self._request("GET", "/tier")
    
    # ========================================================================
    # CUSTOM
    # ========================================================================
    
    def get_custom_api(
        self,
        api_id: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Call custom GET API endpoint.
        Wallet address is extracted from JWT token, not from parameters.
        
        Args:
            api_id: Custom API ID
            params: Optional query parameters
            
        Returns:
            Custom API response
        """
        query_params = {}
        if params:
            query_params.update(params)
        
        return self._request("GET", f"/custom/{api_id}", params=query_params)
    
    def post_custom_api(
        self,
        api_id: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call custom POST API endpoint.
        Wallet address is extracted from JWT token, not from parameters.
        
        Args:
            api_id: Custom API ID
            payload: Request payload
            
        Returns:
            Custom API response
        """
        return self._request("POST", f"/custom/{api_id}", json=payload)


# ============================================================================
# MAIN EXAMPLE
# ============================================================================

def main():
    """Main example demonstrating API usage."""
    
    # Initialize wallet
    if not PRIVATE_KEY or PRIVATE_KEY == "0x" + "0" * 64:
        print("ERROR: Please set PRIVATE_KEY in the configuration section")
        return
    
    wallet_address = get_wallet_address(PRIVATE_KEY)
    print(f"Wallet Address: {wallet_address}")
    
    # Initialize API client
    client = SailAPIClient(BASE_URL, PROJECT_ID, PAGE_ID)
    
    # Step 1: Authenticate
    print("\n=== Step 1: Authentication ===")
    auth_message = "Authenticate SDK agent for Sail API"
    signature = sign_message(auth_message, PRIVATE_KEY)
    print(f"Signing message: {auth_message}")
    print(f"Signature: {signature[:20]}...")
    
    try:
        auth_response = client.authenticate(wallet_address, signature)
        print(f"Authentication successful!")
        print(f"Token: {auth_response.get('token')[:20]}...")
        print(f"User ID: {auth_response.get('user_id')}")
        print(f"Is New User: {auth_response.get('is_new_user')}")
    except Exception as e:
        print(f"Authentication failed: {e}")
        return
    
    # Step 2: Get Balance
    print("\n=== Step 2: Get Balance ===")
    try:
        balance = client.get_balance()
        print(f"Balance: {balance.get('balance')}")
        print(f"Balance Formatted: {balance.get('balanceFormatted')}")
    except Exception as e:
        print(f"Get balance failed: {e}")
    
    # Step 3: Get Deposit Info
    print("\n=== Step 3: Get Deposit Info ===")
    try:
        deposit_info = client.get_deposit_info()
        print(f"Current Balance: {deposit_info.get('currentBalance')}")
        print(f"Eligible Tier IDs: {deposit_info.get('eligibleTierIds')}")
    except Exception as e:
        print(f"Get deposit info failed: {e}")
    
    # Step 4: Get Portfolio Total Balance
    print("\n=== Step 4: Get Portfolio Total Balance ===")
    try:
        portfolio_balance = client.get_portfolio_total_balance()
        print(f"Total Balance: {portfolio_balance.get('balance')}")
        print(f"Balance Formatted: {portfolio_balance.get('balanceFormatted')}")
    except Exception as e:
        print(f"Get portfolio balance failed: {e}")
    
    # Step 5: Get Page Info
    print("\n=== Step 5: Get Page Info ===")
    try:
        page_info = client.get_page()
        print(f"Page Title: {page_info.get('title')}")
        print(f"Project Title: {page_info.get('projectTitle')}")
    except Exception as e:
        print(f"Get page info failed: {e}")
    
    # Step 6: Get Tier Info
    print("\n=== Step 6: Get Tier Info ===")
    try:
        tier_info = client.get_tier_info()
        print(f"User Tier: {tier_info.get('userTier')}")
        print(f"User Balance: {tier_info.get('userBalance')}")
    except Exception as e:
        print(f"Get tier info failed: {e}")
    
    # Step 7: Get Chatbots
    print("\n=== Step 7: Get Chatbots ===")
    try:
        chatbots = client.get_chatbots()
        print(f"Found {len(chatbots.get('chatbots', []))} chatbot(s)")
        for bot in chatbots.get('chatbots', []):
            print(f"  - {bot.get('name')} (ID: {bot.get('id')})")
    except Exception as e:
        print(f"Get chatbots failed: {e}")
    
    # Step 8: Get Automation Status
    print("\n=== Step 8: Get Automation Status ===")
    try:
        automation_status = client.get_automation_status()
        print(f"Has Job: {automation_status.get('hasJob')}")
        print(f"Status: {automation_status.get('status')}")
    except Exception as e:
        print(f"Get automation status failed: {e}")
    
    print("\n=== Example Complete ===")
    print("\nNote: Many endpoints require specific configurations on the SailBE server.")
    print("Some endpoints may fail if the required tools, graphs, or configurations are not set up.")
    print("Refer to the README files for more detailed usage examples.")


if __name__ == "__main__":
    main()

