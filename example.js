/**
 * SailBE SDK API Example - JavaScript/Node.js
 * 
 * This script demonstrates how to:
 * 1. Authenticate using wallet signatures
 * 2. Use JWT tokens for subsequent API requests
 * 3. Call all available SDK endpoints
 * 
 * Requirements:
 *     npm install ethers axios form-data
 *     or
 *     yarn add ethers axios form-data
 */

const { ethers } = require('ethers');
const axios = require('axios');
const fs = require('fs');
const FormData = require('form-data');

// ============================================================================
// CONFIGURATION
// ============================================================================

// Base URL of the Sail API server
// Production API URL: https://app.sail.money/prod
const BASE_URL = 'https://app.sail.money/prod';

// Project and Page IDs
// Default values for Sail production
const PROJECT_ID = 'sail';
const PAGE_ID = 'home';

// Wallet configuration
// IMPORTANT: Never commit private keys to version control!
// Get your private key from: https://sail.money/manage-wallet/7702
// Use environment variables or secure key management in production
const PRIVATE_KEY = '0x' + '0'.repeat(64); // Replace with your private key
let WALLET_ADDRESS = null; // Will be derived from private key

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Sign a message using Ethereum private key.
 * 
 * @param {string} message - The message to sign
 * @param {string} privateKey - Private key in hex format (with or without 0x prefix)
 * @returns {Promise<string>} Signature in hex format
 */
async function signMessage(message, privateKey) {
    // Create wallet from private key
    const wallet = new ethers.Wallet(privateKey);
    
    // Sign message
    const signature = await wallet.signMessage(message);
    
    return signature;
}

/**
 * Get wallet address from private key.
 * 
 * @param {string} privateKey - Private key in hex format
 * @returns {string} Wallet address in hex format
 */
function getWalletAddress(privateKey) {
    const wallet = new ethers.Wallet(privateKey);
    return wallet.address;
}

// ============================================================================
// API CLIENT CLASS
// ============================================================================

class SailAPIClient {
    /**
     * Initialize the API client.
     * 
     * @param {string} baseUrl - Base URL of the API server
     * @param {string} projectId - Project ID
     * @param {string} pageId - Page ID
     * @param {string|null} token - Optional JWT token (if already authenticated)
     */
    constructor(baseUrl, projectId, pageId, token = null) {
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.projectId = projectId;
        this.pageId = pageId;
        this.token = token;
        this.basePath = `/api/v1/projects/${projectId}/pages/${pageId}`;
    }

    /**
     * Get request headers with authentication.
     * 
     * @returns {Object} Headers object
     */
    _getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        return headers;
    }

    /**
     * Make an API request.
     * 
     * @param {string} method - HTTP method (GET, POST, PUT, etc.)
     * @param {string} endpoint - API endpoint path
     * @param {Object} options - Additional options (params, data, headers, etc.)
     * @returns {Promise<Object>} Response JSON as object
     */
    async _request(method, endpoint, options = {}) {
        const url = `${this.baseUrl}${this.basePath}${endpoint}`;
        const headers = this._getHeaders();
        
        if (options.headers) {
            Object.assign(headers, options.headers);
        }

        const config = {
            method,
            url,
            headers,
            ...options
        };

        const response = await axios(config);
        return response.data;
    }

    // ========================================================================
    // AUTHENTICATION
    // ========================================================================

    /**
     * Authenticate using wallet signature.
     * 
     * @param {string} walletAddress - Wallet address
     * @param {string} signature - Signature of the authentication message
     * @returns {Promise<Object>} Authentication response with token
     */
    async authenticate(walletAddress, signature) {
        const url = `${this.baseUrl}${this.basePath}/authenticate`;
        const payload = {
            walletAddress,
            signature
        };

        const response = await axios.post(url, payload);
        
        // Store token for future requests
        this.token = response.data.token;
        
        return response.data;
    }

    // ========================================================================
    // BALANCE
    // ========================================================================

    /**
     * Get balance for a wallet.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @param {string|null} tokenAddress - Optional token address
     * @param {number|null} chainId - Optional chain ID
     * @returns {Promise<Object>} Balance information
     */
    async getBalance(tokenAddress = null, chainId = null) {
        const params = {};
        if (tokenAddress) params.tokenAddress = tokenAddress;
        if (chainId) params.chainId = chainId;

        return this._request('GET', '/balance', { params });
    }

    // ========================================================================
    // DEPOSIT
    // ========================================================================

    /**
     * Deposit funds.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @param {string} amount - Amount to deposit (human-readable format, e.g., '1' for 1 ETH, '10' for 10 USDC)
     * @param {string|null} tokenAddress - Optional token address
     * @param {number|null} chainId - Optional chain ID
     * @returns {Promise<Object>} Deposit response
     */
    async deposit(amount, tokenAddress = null, chainId = null) {
        const payload = {
            amount
        };
        if (tokenAddress) payload.tokenAddress = tokenAddress;
        if (chainId) payload.chainId = chainId;

        return this._request('POST', '/deposit', { data: payload });
    }

    /**
     * Get deposit information.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @returns {Promise<Object>} Deposit info including balance, permitted tokens, etc.
     */
    async getDepositInfo() {
        return this._request('GET', '/deposit-info');
    }

    /**
     * Execute pre-deposit hooks.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @param {string} amount - Amount to deposit (human-readable format, e.g., '1' for 1 ETH, '10' for 10 USDC)
     * @param {string|null} tokenAddress - Optional token address
     * @param {number|null} chainId - Optional chain ID
     * @returns {Promise<Object>} Pre-deposit hooks response
     */
    async preDepositHooks(amount, tokenAddress = null, chainId = null) {
        const payload = {
            amount
        };
        if (tokenAddress) payload.tokenAddress = tokenAddress;
        if (chainId) payload.chainId = chainId;

        return this._request('POST', '/deposit/pre-hooks', { data: payload });
    }

    /**
     * Execute post-deposit hooks.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @param {string} amount - Amount that was deposited (human-readable format, e.g., '1' for 1 ETH, '10' for 10 USDC)
     * @param {string} txHash - Transaction hash
     * @param {string|null} tokenAddress - Optional token address
     * @param {number|null} chainId - Optional chain ID
     * @param {string} status - Transaction status ("success" or "error")
     * @returns {Promise<Object>} Post-deposit hooks response
     */
    async postDepositHooks(amount, txHash, tokenAddress = null, chainId = null, status = 'success') {
        const payload = {
            amount,
            txHash,
            status
        };
        if (tokenAddress) payload.tokenAddress = tokenAddress;
        if (chainId) payload.chainId = chainId;

        return this._request('POST', '/deposit/post-hooks', { data: payload });
    }

    // ========================================================================
    // WITHDRAW
    // ========================================================================

    /**
     * Withdraw funds.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @param {string} amount - Amount to withdraw (human-readable format, e.g., '1' for 1 ETH, '10' for 10 USDC)
     * @param {string|null} tokenAddress - Optional token address
     * @param {number|null} chainId - Optional chain ID
     * @returns {Promise<Object>} Withdraw response
     */
    async withdraw(amount, tokenAddress = null, chainId = null) {
        const payload = {
            amount
        };
        if (tokenAddress) payload.tokenAddress = tokenAddress;
        if (chainId) payload.chainId = chainId;

        return this._request('POST', '/withdraw', { data: payload });
    }

    /**
     * Get withdraw information.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @returns {Promise<Object>} Withdraw info including balance, permitted tokens, etc.
     */
    async getWithdrawInfo() {
        return this._request('GET', '/withdraw-info');
    }

    /**
     * Execute pre-withdraw hooks.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @param {string} amount - Amount to withdraw (human-readable format, e.g., '1' for 1 ETH, '10' for 10 USDC)
     * @param {string} recipient - Recipient address for the withdrawal
     * @param {string|null} tokenAddress - Optional token address
     * @param {number|null} chainId - Optional chain ID
     * @returns {Promise<Object>} Pre-withdraw hooks response
     */
    async preWithdrawHooks(amount, recipient, tokenAddress = null, chainId = null) {
        const payload = {
            amount,
            recipient
        };
        if (tokenAddress) payload.tokenAddress = tokenAddress;
        if (chainId) payload.chainId = chainId;

        return this._request('POST', '/withdraw/pre-hooks', { data: payload });
    }

    /**
     * Execute post-withdraw hooks.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @param {string} amount - Amount that was withdrawn (human-readable format, e.g., '1' for 1 ETH, '10' for 10 USDC)
     * @param {string} txHash - Transaction hash
     * @param {string} recipient - Recipient address for the withdrawal
     * @param {string|null} tokenAddress - Optional token address
     * @param {number|null} chainId - Optional chain ID
     * @param {string} status - Transaction status ("success" or "error")
     * @returns {Promise<Object>} Post-withdraw hooks response
     */
    async postWithdrawHooks(amount, txHash, recipient, tokenAddress = null, chainId = null, status = 'success') {
        const payload = {
            amount,
            txHash,
            recipient,
            status
        };
        if (tokenAddress) payload.tokenAddress = tokenAddress;
        if (chainId) payload.chainId = chainId;

        return this._request('POST', '/withdraw/post-hooks', { data: payload });
    }

    // ========================================================================
    // PORTFOLIO
    // ========================================================================

    /**
     * Get total portfolio balance.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @returns {Promise<Object>} Total portfolio balance
     */
    async getPortfolioTotalBalance() {
        return this._request('GET', '/portfolio/total-balance');
    }

    /**
     * Get portfolio token balances.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @returns {Promise<Object>} List of token balances
     */
    async getPortfolioTokens() {
        return this._request('GET', '/portfolio/tokens');
    }

    // ========================================================================
    // SESSION KEYS
    // ========================================================================

    /**
     * Sign permitted session keys.
     * 
     * @param {string} walletAddress - Smart account address
     * @param {Object<string, string>} signatures - Dictionary mapping sessionKeyId to signature
     * @param {Object<string, Object>} sessionSpecs - Dictionary mapping sessionKeyId to sessionSpec
     * @param {string|null} ownerEOA - Optional EOA owner address (for ERC-7702)
     * @param {Object<string, string>|null} backendWalletTransactionHashes - Optional transaction hashes
     * @param {Object<string, string>|null} approvalTransactionHashes - Optional approval transaction hashes
     * @param {Array<Object>|null} approvals - Optional list of approvals
     * @returns {Promise<Object>} Sign permitted keys response
     */
    async signPermittedKeys(
        walletAddress,
        signatures,
        sessionSpecs,
        ownerEOA = null,
        backendWalletTransactionHashes = null,
        approvalTransactionHashes = null,
        approvals = null
    ) {
        const payload = {
            walletAddress,
            signatures,
            sessionSpecs
        };
        if (ownerEOA) payload.ownerEOA = ownerEOA;
        if (backendWalletTransactionHashes) payload.backendWalletTransactionHashes = backendWalletTransactionHashes;
        if (approvalTransactionHashes) payload.approvalTransactionHashes = approvalTransactionHashes;
        if (approvals) payload.approvals = approvals;

        return this._request('POST', '/sign-permitted-keys', { data: payload });
    }

    /**
     * Get permitted keys available for signing.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @returns {Promise<Object>} Permitted keys information
     */
    async getPermittedKeysForSigning() {
        return this._request('GET', '/get-permitted-keys-for-signing');
    }

    /**
     * Check remaining authorizations.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @returns {Promise<Object>} Remaining authorizations information
     */
    async checkRemainingAuthorizations() {
        return this._request('GET', '/check-remaining-authorizations');
    }

    /**
     * Get session keys display information.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @returns {Promise<Object>} Session keys display information
     */
    async getSessionKeysDisplay() {
        return this._request('GET', '/session-keys-display');
    }

    /**
     * Enable delegation.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @param {number} chainId - Chain ID
     * @param {string} delegationData - Encoded enableDelegation transaction data (hex string with 0x prefix)
     * @returns {Promise<Object>} Enable delegation response
     */
    async enableDelegation(chainId, delegationData) {
        const payload = {
            chainId,
            delegationData
        };

        return this._request('POST', '/enable-delegation', { data: payload });
    }

    /**
     * Check bulk authorization status for session keys.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @param {Array<string>} sessionKeyIds - List of session key IDs
     * @returns {Promise<Object>} Bulk authorization status
     */
    async checkBulkAuthorizationStatus(sessionKeyIds) {
        const url = `${this.baseUrl}/api/v1/session-key/check-bulk-authorization-status`;
        const payload = {
            sessionKeyIds
        };

        const response = await axios.post(url, payload, { headers: this._getHeaders() });
        return response.data;
    }

    // ========================================================================
    // AUTOMATION
    // ========================================================================

    /**
     * Get automation job status.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @returns {Promise<Object>} Automation status
     */
    async getAutomationStatus() {
        return this._request('GET', '/automation/status');
    }

    /**
     * Start automation job.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @param {string} graphId - Graph ID to run
     * @param {string} prompt - Prompt/message for the graph
     * @param {Object|null} paramValues - Optional parameter values
     * @param {number} iterations - Number of iterations
     * @param {string|null} branchId - Optional branch ID
     * @returns {Promise<Object>} Start automation response
     */
    async startAutomation(graphId, prompt, paramValues = null, iterations = 1, branchId = null) {
        const payload = {
            graphId,
            prompt,
            iterations
        };
        if (paramValues) payload.paramValues = paramValues;
        if (branchId) payload.branchId = branchId;

        return this._request('POST', '/automation/start', { data: payload });
    }

    /**
     * Pause automation job.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @returns {Promise<Object>} Pause automation response
     */
    async pauseAutomation() {
        return this._request('POST', '/automation/pause');
    }

    /**
     * Resume automation job.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @returns {Promise<Object>} Resume automation response
     */
    async resumeAutomation() {
        return this._request('POST', '/automation/resume');
    }

    /**
     * Stop automation job.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @returns {Promise<Object>} Stop automation response
     */
    async stopAutomation() {
        return this._request('POST', '/automation/stop');
    }

    // ========================================================================
    // VAULT
    // ========================================================================

    /**
     * Get share price history for vaults.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @param {string} vaultAddresses - Comma-separated list of vault addresses
     * @param {number} chainId - Chain ID
     * @param {number} days - Number of days (default: 90)
     * @param {string|number|null} startTimestamp - Optional start datetime (ISO 8601 string) or Unix timestamp in seconds
     * @param {string|number|null} endTimestamp - Optional end datetime (ISO 8601 string) or Unix timestamp in seconds
     * @returns {Promise<Object>} Share price history
     */
    async getSharePriceHistory(vaultAddresses, chainId, days = 90, startTimestamp = null, endTimestamp = null) {
        const params = {
            vaultAddresses,
            chainId,
            days
        };
        if (startTimestamp) params.startTimestamp = startTimestamp;
        if (endTimestamp) params.endTimestamp = endTimestamp;

        return this._request('GET', '/share-price-history', { params });
    }

    /**
     * Get vault information.
     * Vault address and chain ID are configured in the tool/graph, not passed as parameters.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @param {string|null} walletAddress - Optional wallet address (only passed to tool if provided)
     * @param {string|number|null} startTime - Optional start datetime (ISO 8601 string) or Unix timestamp in seconds
     * @param {string|number|null} endTime - Optional end datetime (ISO 8601 string) or Unix timestamp in seconds
     * @returns {Promise<number>} Vault information as a simple number (e.g., 10.31)
     */
    async getVaultInfo(walletAddress = null, startTime = null, endTime = null) {
        const params = {};
        if (walletAddress) {
            params.walletAddress = walletAddress;
        }
        if (startTime !== null) {
            params.startTime = startTime;
        }
        if (endTime !== null) {
            params.endTime = endTime;
        }

        return this._request('GET', '/vault-info', { params });
    }

    // ========================================================================
    // CHATBOT
    // ========================================================================

    /**
     * Get list of chatbots.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @returns {Promise<Object>} List of chatbots
     */
    async getChatbots() {
        return this._request('GET', '/chatbots');
    }

    /**
     * Get chatbot memories.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @param {string} graphId - Graph ID (chatbot graph ID)
     * @param {number} page - Page number (default: 1)
     * @param {number} limit - Items per page (default: 20)
     * @returns {Promise<Object>} Chatbot memories
     */
    async getChatbotMemories(graphId, page = 1, limit = 20) {
        const params = {
            graphId,
            page,
            limit
        };

        return this._request('GET', '/chatbot-memories', { params });
    }

    // ========================================================================
    // GRAPH
    // ========================================================================

    /**
     * Run a graph execution.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @param {string} graphId - Graph ID
     * @param {string} prompt - User prompt/message
     * @param {Object|null} paramValues - Optional parameter values
     * @param {number} iterations - Number of iterations (default: 1)
     * @param {string|null} branchId - Optional branch ID
     * @param {boolean} includeContextReport - Include context report
     * @param {Object|null} contextData - Optional context data
     * @returns {Promise<Object>} Graph execution results
     */
    async runGraph(
        graphId,
        prompt,
        paramValues = null,
        iterations = 1,
        branchId = null,
        includeContextReport = false,
        contextData = null
    ) {
        const payload = {
            id: graphId,
            prompt,
            iterations,
            includeContextReport
        };
        if (paramValues) payload.paramValues = paramValues;
        if (branchId) payload.branchId = branchId;
        if (contextData) payload.contextData = contextData;

        return this._request('POST', '/run-graph', { data: payload });
    }

    // ========================================================================
    // PROFILE
    // ========================================================================

    /**
     * Get user profile.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @returns {Promise<Object>} User profile
     */
    async getProfile() {
        return this._request('GET', '/profile');
    }

    /**
     * Update user profile.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @param {Object} profileData - Profile data to update
     * @returns {Promise<Object>} Updated profile
     */
    async updateProfile(profileData) {
        return this._request('PUT', '/profile', { data: profileData });
    }

    /**
     * Upload profile avatar.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @param {string} filePath - Path to image file
     * @returns {Promise<Object>} Upload response
     */
    async uploadProfileAvatar(filePath) {
        const url = `${this.baseUrl}${this.basePath}/profile/avatar`;
        const formData = new FormData();
        formData.append('file', fs.createReadStream(filePath));

        const response = await axios.post(url, formData, {
            headers: {
                ...this._getHeaders(),
                'Content-Type': 'multipart/form-data'
            }
        });

        return response.data;
    }

    /**
     * Upload profile banner.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @param {string} filePath - Path to image file
     * @returns {Promise<Object>} Upload response
     */
    async uploadProfileBanner(filePath) {
        const url = `${this.baseUrl}${this.basePath}/profile/banner`;
        const formData = new FormData();
        formData.append('file', fs.createReadStream(filePath));

        const response = await axios.post(url, formData, {
            headers: {
                ...this._getHeaders(),
                'Content-Type': 'multipart/form-data'
            }
        });

        return response.data;
    }

    // ========================================================================
    // PAGE
    // ========================================================================

    /**
     * Get page information.
     * 
     * @returns {Promise<Object>} Page data including title, project info, authConfig, themeConfig
     */
    async getPage() {
        return this._request('GET', '/page');
    }

    /**
     * Get list of pages.
     * 
     * @param {string|null} projectId - Optional project ID filter
     * @param {number} limit - Maximum number of results (default: 100)
     * @param {number} offset - Offset for pagination (default: 0)
     * @returns {Promise<Object>} List of pages
     */
    async getPages(projectId = null, limit = 100, offset = 0) {
        const params = { limit, offset };
        if (projectId) params.projectId = projectId;

        const url = `${this.baseUrl}/api/v1/pages`;
        const response = await axios.get(url, {
            params,
            headers: this._getHeaders()
        });
        return response.data;
    }

    // ========================================================================
    // TIER
    // ========================================================================

    /**
     * Get tier information.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @returns {Promise<Object>} Tier information including user tier, eligible tiers, etc.
     */
    async getTierInfo() {
        return this._request('GET', '/tier');
    }

    // ========================================================================
    // CUSTOM
    // ========================================================================

    /**
     * Call custom GET API endpoint.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @param {string} apiId - Custom API ID
     * @param {Object|null} params - Optional query parameters
     * @returns {Promise<Object>} Custom API response
     */
    async getCustomAPI(apiId, params = null) {
        const queryParams = {};
        if (params) Object.assign(queryParams, params);

        return this._request('GET', `/custom/${apiId}`, { params: queryParams });
    }

    /**
     * Call custom POST API endpoint.
     * Wallet address is extracted from JWT token, not from parameters.
     * 
     * @param {string} apiId - Custom API ID
     * @param {Object} payload - Request payload
     * @returns {Promise<Object>} Custom API response
     */
    async postCustomAPI(apiId, payload) {
        return this._request('POST', `/custom/${apiId}`, { data: payload });
    }
}

// ============================================================================
// MAIN EXAMPLE
// ============================================================================

async function main() {
    // Initialize wallet
    if (!PRIVATE_KEY || PRIVATE_KEY === '0x' + '0'.repeat(64)) {
        console.error('ERROR: Please set PRIVATE_KEY in the configuration section');
        return;
    }

    const walletAddress = getWalletAddress(PRIVATE_KEY);
    console.log(`Wallet Address: ${walletAddress}`);

    // Initialize API client
    const client = new SailAPIClient(BASE_URL, PROJECT_ID, PAGE_ID);

    // Step 1: Authenticate
    console.log('\n=== Step 1: Authentication ===');
    const authMessage = 'Authenticate SDK agent for Sail API';
    const signature = await signMessage(authMessage, PRIVATE_KEY);
    console.log(`Signing message: ${authMessage}`);
    console.log(`Signature: ${signature.substring(0, 20)}...`);

    try {
        const authResponse = await client.authenticate(walletAddress, signature);
        console.log('Authentication successful!');
        console.log(`Token: ${authResponse.token.substring(0, 20)}...`);
        console.log(`User ID: ${authResponse.user_id}`);
        console.log(`Is New User: ${authResponse.is_new_user}`);
    } catch (error) {
        console.error(`Authentication failed: ${error.message}`);
        if (error.response) {
            console.error(`Response: ${JSON.stringify(error.response.data, null, 2)}`);
        }
        return;
    }

    // Step 2: Get Balance
    console.log('\n=== Step 2: Get Balance ===');
    try {
        const balance = await client.getBalance();
        console.log(`Balance: ${balance.balance}`);
        console.log(`Balance Formatted: ${balance.balanceFormatted}`);
    } catch (error) {
        console.error(`Get balance failed: ${error.message}`);
    }

    // Step 3: Get Deposit Info
    console.log('\n=== Step 3: Get Deposit Info ===');
    try {
        const depositInfo = await client.getDepositInfo();
        console.log(`Current Balance: ${depositInfo.currentBalance}`);
        console.log(`Eligible Tier IDs: ${depositInfo.eligibleTierIds}`);
    } catch (error) {
        console.error(`Get deposit info failed: ${error.message}`);
    }

    // Step 4: Get Portfolio Total Balance
    console.log('\n=== Step 4: Get Portfolio Total Balance ===');
    try {
        const portfolioBalance = await client.getPortfolioTotalBalance();
        console.log(`Total Balance: ${portfolioBalance.balance}`);
        console.log(`Balance Formatted: ${portfolioBalance.balanceFormatted}`);
    } catch (error) {
        console.error(`Get portfolio balance failed: ${error.message}`);
    }

    // Step 5: Get Page Info
    console.log('\n=== Step 5: Get Page Info ===');
    try {
        const pageInfo = await client.getPage();
        console.log(`Page Title: ${pageInfo.title}`);
        console.log(`Project Title: ${pageInfo.projectTitle}`);
    } catch (error) {
        console.error(`Get page info failed: ${error.message}`);
    }

    // Step 6: Get Tier Info
    console.log('\n=== Step 6: Get Tier Info ===');
    try {
        const tierInfo = await client.getTierInfo();
        console.log(`User Tier: ${JSON.stringify(tierInfo.userTier)}`);
        console.log(`User Balance: ${tierInfo.userBalance}`);
    } catch (error) {
        console.error(`Get tier info failed: ${error.message}`);
    }

    // Step 7: Get Chatbots
    console.log('\n=== Step 7: Get Chatbots ===');
    try {
        const chatbots = await client.getChatbots();
        console.log(`Found ${chatbots.chatbots.length} chatbot(s)`);
        chatbots.chatbots.forEach(bot => {
            console.log(`  - ${bot.name} (ID: ${bot.id})`);
        });
    } catch (error) {
        console.error(`Get chatbots failed: ${error.message}`);
    }

    // Step 8: Get Automation Status
    console.log('\n=== Step 8: Get Automation Status ===');
    try {
        const automationStatus = await client.getAutomationStatus();
        console.log(`Has Job: ${automationStatus.hasJob}`);
        console.log(`Status: ${automationStatus.status}`);
    } catch (error) {
        console.error(`Get automation status failed: ${error.message}`);
    }

    console.log('\n=== Example Complete ===');
    console.log('\nNote: Many endpoints require specific configurations on the SailBE server.');
    console.log('Some endpoints may fail if the required tools, graphs, or configurations are not set up.');
    console.log('Refer to the README files for more detailed usage examples.');
}

// Run the example
if (require.main === module) {
    main().catch(console.error);
}

module.exports = { SailAPIClient, signMessage, getWalletAddress };

