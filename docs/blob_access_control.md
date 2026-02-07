# Blob Fields Access Control

## Overview

ZMS implements fine-grained access control for blob fields (images and files) to ensure that media assets are only accessible to authorized users based on their roles, permissions, language access, and contextual factors.

## Access Control Mechanisms

### 1. Basic Access Control (Existing)

The basic access control for blob fields checks:
- **Visibility**: Whether the parent object and its parent node are visible (`isVisible()`)
- **Access Permission**: Whether the user has View permission or the object has public access (`hasAccess()`)
- **Global Public Access**: Configuration property `ZMS.blobfields.grant_public_access` can grant public access to all blob fields
- **Preview Mode**: Preview mode (`preview=preview`) bypasses visibility checks for content editors

### 2. Fine-Grained Access Control (New)

The new `_check_fine_grained_access()` method implements additional security checks:

#### User Role Checking
- **Administrator Access**: Users with `ZMSAdministrator` or `Manager` roles always have access
- **Role Verification**: Users must have at least one valid ZMS role:
  - `ZMSEditor` - Content editors
  - `ZMSAuthor` - Content authors
  - `ZMSSubscriber` - Read-only subscribers
- **Insufficient Roles**: Access is denied if the user has no valid ZMS roles

#### Language-Based Access Control
- Users can be restricted to specific languages via `getUserLangs()`
- If a user has language restrictions (not `*`), they can only access blobs for their allowed languages
- The request language is compared against the user's allowed languages

#### Time-Based Access Windows
- Users can have active start and end dates (`attrActiveStart`, `attrActiveEnd`)
- Access is denied if the current date is outside the user's active period
- Useful for temporary access grants or expiring credentials

#### Restricted Ancestor Nodes
- The system checks all ancestor nodes in the breadcrumb path
- If any ancestor node has restricted access (`hasRestrictedAccess()`), the user must have explicit permission
- This ensures that content in restricted folders is properly protected

### 3. Custom Access Hooks

The system supports custom access rules via the `hasCustomAccess()` method:
- Applications can implement custom access logic in parent objects
- Return `True` or `False` to grant or deny access
- Return `404` to trigger a redirect

## Access Denial Logging

When access is denied through fine-grained checks, the system logs:
- Authenticated user identity
- Reason for denial (e.g., `insufficient_roles`, `language_restriction`, `outside_active_period`, `restricted_ancestor_node`)
- Request URL path

This audit trail helps administrators monitor security events and troubleshoot access issues.

## Configuration

### Global Configuration Properties

- **`ZMS.blobfields.grant_public_access`**: Set to `1` to grant public access to all blob fields (default: `0`)
- **`ZMS.security.roles`**: Define security roles and their permissions
- **`ZMS.security.users`**: Configure user-to-node role assignments

### User Attributes

- **`attrActiveStart`**: Start date for user access window (optional)
- **`attrActiveEnd`**: End date for user access window (optional)
- **`langs`**: List of allowed languages for the user (default: `['*']` for all languages)
- **`nodes`**: Node-specific role assignments for the user

## Implementation Details

### Access Check Flow

```
1. Check if object and parent are visible
   ↓
2. Check basic hasAccess() or global public access grant
   ↓
3. If basic access granted, perform fine-grained checks:
   a. Check user roles (admin/valid roles)
   b. Check language restrictions
   c. Check time-based access window
   d. Check restricted ancestor nodes
   ↓
4. If all checks pass, check custom access hook (if exists)
   ↓
5. Grant or deny access
```

### Error Handling

The fine-grained access control is designed to be fail-safe:
- If a specific check fails due to an error, it logs the error and continues to other checks
- Errors during access checking do not automatically deny access
- This prevents access control failures from breaking blob delivery

## Anonymous Users

Anonymous users are handled specially:
- They bypass fine-grained role and language checks
- Access is determined solely by:
  - Object visibility
  - Public access settings
  - Custom access hooks

## Example Use Cases

### Use Case 1: Role-Based Image Access
A sensitive document with embedded images should only be accessible to editors and administrators:
- Users without `ZMSEditor` or `ZMSAdministrator` roles will be denied access to the blob
- Access denial is logged with reason: `insufficient_roles`

### Use Case 2: Language-Specific Documents
A multilingual site where translators should only access content in their assigned languages:
- French translator has `langs=['fra']`
- Attempting to access a German document's images is denied with reason: `language_restriction`

### Use Case 3: Temporary Contractor Access
A contractor needs access for a specific project period:
- Set `attrActiveStart='2024-01-01'` and `attrActiveEnd='2024-12-31'`
- After December 31, 2024, access is denied with reason: `outside_active_period`

### Use Case 4: Restricted Section
A folder is marked as restricted (e.g., internal documents):
- Even if a user has access to specific pages, ancestor folder restriction is checked
- Access denied with reason: `restricted_ancestor_node` if user lacks permission on restricted parent

## Security Considerations

1. **Defense in Depth**: Multiple layers of access control provide better security
2. **Audit Trail**: Access denials are logged for security monitoring
3. **Fail-Safe Design**: Errors don't automatically deny access to prevent availability issues
4. **Backward Compatibility**: Existing access control mechanisms remain unchanged
5. **Performance**: Checks are performed efficiently with minimal overhead

## Testing

The test suite includes:
- Basic access control verification
- Role-based access tests
- Language restriction tests
- Time-based access window tests
- Anonymous user handling

Run tests with:
```bash
python3 -m unittest tests.test_blobfields_access
```

## Future Enhancements

Potential future improvements:
- IP-based access restrictions
- Device/client type restrictions
- Bandwidth throttling for different user roles
- Fine-grained permissions per blob field type (images vs. files)
- Integration with external authentication providers
