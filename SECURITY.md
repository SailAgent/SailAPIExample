# Security Documentation

## Overview

This document outlines the security measures implemented in the Sail API to protect user funds, prevent unauthorized access, and ensure the integrity of all API operations.

## JWT Authentication Security

### Token Generation

JWT tokens are generated using the following security measures:

- **Algorithm**: HS256 (HMAC with SHA-256)
- **Secret Key**: Stored securely in environment variables (`JWT_SECRET`), never exposed in client code
- **Expiration**: Tokens expire after 720 hours (30 days) to limit exposure window
- **Payload**: Contains only `user_id` and expiration timestamp (`exp`)

### Token Validation

All authenticated endpoints validate JWT tokens using:

1. **Signature Verification**: Tokens are verified using the shared secret key
2. **Expiration Checking**: Expired tokens are automatically rejected
3. **Algorithm Validation**: Only HS256 algorithm is accepted
4. **User ID Extraction**: User ID is extracted from the token payload, not from request parameters

### Authentication Flow

1. **Initial Authentication**:
   - User signs a message ("Authenticate SDK agent for Sail API") with their wallet private key
   - Signature is verified using cryptographic signature verification
   - JWT token is generated and returned to the client
   - **Important**: Private keys are NEVER transmitted to the API

2. **Subsequent Requests**:
   - Client includes JWT token in `Authorization: Bearer <token>` header
   - Server validates token and extracts `user_id`
   - Wallet address is retrieved from the database using the authenticated `user_id`
   - **Critical**: Wallet address is NEVER accepted as a parameter - it is always derived from the authenticated user

### Security Benefits

- **No Private Key Exposure**: Private keys never leave the client device
- **Token-Based Authentication**: Stateless authentication reduces server-side session management risks
- **Automatic Expiration**: Tokens expire after 30 days, limiting long-term exposure
- **Signature Verification**: Cryptographic proof that the user controls the wallet

## No Private Keys Policy

### Policy Statement

**The Sail API does NOT accept private keys as parameters in any endpoint.**

### Implementation

- All authentication is performed using wallet signatures, not private keys
- Private keys remain on the client device and are never transmitted
- The API only receives:
  - Wallet addresses (public identifiers)
  - Cryptographic signatures (proof of wallet ownership)
  - JWT tokens (after successful authentication)

### Why This Matters

- **Fund Safety**: Even if API requests are intercepted, attackers cannot access funds without the private key
- **Key Security**: Private keys never leave the user's secure environment
- **Compliance**: Aligns with best practices for Web3 applications

## Transaction Safety

### Agent Transaction Flow

All transactions executed through the Sail API are subject to the **Agent Transaction Flow**, which ensures:

1. **Pre-Authorization**: Transactions must be pre-authorized through session keys or explicit user permissions
2. **Scope Limitation**: Transactions can only be executed within the scope of authorized permissions
3. **No Arbitrary Transactions**: The API cannot execute arbitrary transactions that weren't pre-approved

### Fund Protection Mechanisms

1. **Session Key Authorization**:
   - Session keys are cryptographically signed by the user
   - Each session key has specific permissions (call policies, transfer policies)
   - Session keys can be revoked at any time

2. **Transaction Validation**:
   - All transactions are validated against authorized permissions
   - Unauthorized transaction attempts are rejected
   - Transaction parameters are validated before execution

3. **No Direct Fund Access**:
   - The API does not have direct access to user funds
   - All transactions require cryptographic signatures from authorized keys
   - Users maintain full control over their funds

### What This Means

- **Funds Are Safe**: Even if an attacker gains access to your JWT token, they cannot execute unauthorized transactions
- **Permission-Based**: Only transactions that have been explicitly authorized can be executed
- **Revocable**: Users can revoke session keys or permissions at any time

## Wallet Address Security

### Parameter Removal

**All endpoints have been updated to remove `walletAddress` and `userId` parameters.**

### Why This Matters

Previously, endpoints accepted wallet addresses as parameters, which could be spoofed. Now:

- Wallet addresses are **always** extracted from the JWT token
- User IDs are **always** derived from the authenticated token
- This prevents parameter injection attacks and ensures data integrity

### Implementation

The `get_authenticated_user_and_wallet()` utility function:

1. Extracts `user_id` from the validated JWT token
2. Retrieves the user document from the database
3. Returns the wallet address associated with that user
4. Ensures wallet addresses cannot be spoofed via parameters

## Security Analysis

### Current Security Posture

#### Strengths

1. **Strong Authentication**: JWT tokens with cryptographic signature verification
2. **No Private Key Exposure**: Private keys never transmitted
3. **Token Expiration**: 30-day expiration limits exposure window
4. **Parameter Security**: Wallet addresses derived from tokens, not parameters
5. **Transaction Authorization**: All transactions require pre-authorization

#### Areas for Improvement

1. **Token Refresh**: Consider implementing refresh tokens for better security
2. **Token Revocation**: Implement token blacklisting for immediate revocation
3. **Rate Limiting**: Add rate limiting to prevent brute force attacks
4. **IP Whitelisting**: Optional IP whitelisting for enhanced security
5. **Audit Logging**: Enhanced audit logging for security events
6. **Token Rotation**: Automatic token rotation for long-lived sessions

### Recommendations

#### Short-Term Improvements

1. **Implement Token Blacklisting**:
   - Store revoked tokens in a cache/database
   - Check blacklist during token validation
   - Allow users to revoke tokens from a security settings page

2. **Add Rate Limiting**:
   - Limit authentication attempts per IP address
   - Limit API requests per token
   - Implement exponential backoff for failed attempts

3. **Enhanced Logging**:
   - Log all authentication attempts (successful and failed)
   - Log token validation failures
   - Log suspicious activity patterns

#### Long-Term Improvements

1. **Refresh Token Implementation**:
   - Short-lived access tokens (1 hour)
   - Long-lived refresh tokens (30 days)
   - Automatic token refresh mechanism

2. **Multi-Factor Authentication (MFA)**:
   - Optional MFA for sensitive operations
   - Time-based one-time passwords (TOTP)
   - Hardware security key support

3. **Advanced Monitoring**:
   - Real-time threat detection
   - Anomaly detection for unusual patterns
   - Automated security alerts

4. **Security Headers**:
   - Implement security headers (CORS, CSP, etc.)
   - HSTS for HTTPS enforcement
   - X-Frame-Options to prevent clickjacking

## Best Practices for API Users

### Token Management

1. **Secure Storage**: Store JWT tokens securely (not in localStorage for web apps)
2. **Token Rotation**: Re-authenticate periodically to get fresh tokens
3. **Token Revocation**: Revoke tokens if compromised or no longer needed
4. **HTTPS Only**: Always use HTTPS when transmitting tokens

### Private Key Security

1. **Never Share**: Never share your private key with anyone or any service
2. **Secure Storage**: Store private keys in hardware wallets or secure key management systems
3. **Backup**: Maintain secure backups of private keys
4. **Rotation**: Consider rotating keys periodically

### API Usage

1. **Validate Responses**: Always validate API responses before processing
2. **Error Handling**: Implement proper error handling for authentication failures
3. **Timeout Handling**: Handle token expiration gracefully
4. **Logging**: Log authentication events for security auditing

## Reporting Security Issues

If you discover a security vulnerability, please report it responsibly:

1. **Do NOT** create a public GitHub issue
2. **Do NOT** disclose the vulnerability publicly
3. **Email** security concerns to: security@fungi.ag
4. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond to security reports within 48 hours and work to resolve issues promptly.

## Conclusion

The Sail API is designed with security as a top priority. By:

- Using JWT tokens for authentication
- Never accepting private keys
- Deriving wallet addresses from authenticated tokens
- Requiring pre-authorization for all transactions

We ensure that user funds remain safe and secure. However, security is an ongoing process, and we continuously work to improve our security posture.

For questions or concerns about security, please contact security@fungi.ag.

