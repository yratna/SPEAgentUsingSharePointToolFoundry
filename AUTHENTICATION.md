"""
SharePoint Tool Foundry - Authentication Flow Documentation

This document explains how the SharePoint agent authenticates and passes user tokens
to access Azure resources securely.
"""

# Azure Authentication Flow for SharePoint Tool Foundry

## 🔐 Authentication Architecture

### 1. Primary Authentication: DefaultAzureCredential

The agent uses Azure's `DefaultAzureCredential` which provides a secure,
standardized way to authenticate with Azure services.

```
User/Application
       ↓
DefaultAzureCredential
       ↓
[Authentication Chain]
1. Environment Variables
2. Managed Identity (Azure-hosted)
3. Azure CLI (az login)
4. Azure PowerShell
5. Interactive Browser
       ↓
Azure Active Directory (AAD)
       ↓
Access Token (JWT)
       ↓
Azure AI Foundry Project
       ↓
SharePoint Connection
       ↓
SharePoint Resources
```

### 2. Authentication Flow Steps

#### Step 1: Client Initialization
```python
# Initialize with DefaultAzureCredential
self.project_client = AIProjectClient(
    endpoint=self.config.project_endpoint,
    credential=DefaultAzureCredential(),
)
```

#### Step 2: Token Acquisition
- DefaultAzureCredential automatically handles token acquisition
- Tokens are JWT (JSON Web Tokens) with specific scopes
- Tokens include user identity and permissions

#### Step 3: SharePoint Connection Resolution
```python
# Get connection using authenticated client
connection = self.project_client.connections.get(
    name=self.config.sharepoint_resource_name
)
```

#### Step 4: SharePoint Tool Setup
```python
# Initialize tool with connection ID (includes auth context)
self.sharepoint_tool = SharepointTool(connection_id=connection.id)
```

### 3. Token Types and Scopes

#### Access Token Structure:
```json
{
  "aud": "https://cognitiveservices.azure.com",
  "iss": "https://sts.windows.net/{tenant-id}/",
  "sub": "{user-object-id}",
  "upn": "user@domain.com",
  "scp": "user_impersonation",
  "roles": ["AI.Projects.Read", "AI.Agents.Write"]
}
```

#### Required Scopes:
- `https://cognitiveservices.azure.com/.default`
- `user_impersonation` (for acting on behalf of user)

### 4. Security Features

#### Automatic Token Management:
- **Token Refresh**: Automatically handled by Azure SDK
- **Token Caching**: Secure local cache for performance
- **Token Expiration**: Automatic renewal before expiry
- **Scope Validation**: Ensures minimal required permissions

#### Security Best Practices:
- ✅ No hardcoded credentials
- ✅ Principle of least privilege
- ✅ Automatic token rotation
- ✅ Secure token storage
- ✅ Audit logging

### 5. Authentication Methods by Environment

#### Development Environment:
1. **Azure CLI Login**: `az login`
   - User logs in interactively
   - Credentials cached locally
   - DefaultAzureCredential uses cached tokens

#### Production Environment:
1. **Managed Identity** (Recommended):
   - System-assigned or User-assigned
   - No credentials to manage
   - Automatic authentication

2. **Service Principal**:
   - Client ID + Client Secret
   - Environment variables
   - Suitable for CI/CD

#### Local Testing:
1. **Interactive Browser**:
   - Fallback method
   - Opens browser for authentication
   - One-time consent

### 6. SharePoint-Specific Authentication

#### Connection Types:
- **OAuth 2.0**: For SharePoint Online
- **Certificate-based**: For enterprise scenarios
- **Managed Identity**: For Azure-hosted applications

#### Permission Model:
```
User → Azure AD → AI Foundry → SharePoint Connection → SharePoint Site
  ↓       ↓           ↓              ↓                    ↓
Auth    Token    Connection     Site Access         Document Access
```

### 7. Troubleshooting Authentication

#### Common Issues:
1. **No authentication available**
   - Solution: Run `az login` or set up Managed Identity

2. **Insufficient permissions**
   - Solution: Grant required roles in Azure AD

3. **Token expired**
   - Solution: Handled automatically by SDK

4. **Connection not found**
   - Solution: Verify SharePoint connection in AI Foundry

#### Debug Authentication:
```python
# Enable debug logging in config
DEBUG_LOGGING=true

# Check authentication status
from azure.identity import DefaultAzureCredential
credential = DefaultAzureCredential()
token = credential.get_token("https://cognitiveservices.azure.com/.default")
print(f"Token expires: {token.expires_on}")
```

### 8. Security Considerations

#### Data Flow Security:
- All communications use HTTPS/TLS
- Tokens never logged or exposed
- Secure credential storage
- Audit trail maintained

#### Access Control:
- Role-Based Access Control (RBAC)
- Resource-level permissions
- Time-limited tokens
- Conditional access policies

### 9. Monitoring and Auditing

#### What Gets Logged:
- Authentication attempts
- Token acquisition events
- Resource access patterns
- Permission changes

#### Audit Locations:
- Azure AD Sign-in logs
- Azure Activity Log
- AI Foundry audit logs
- SharePoint audit logs

## Example Implementation

See `sharepoint_agent.py` for the complete implementation of this authentication flow.
