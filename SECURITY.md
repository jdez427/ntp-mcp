# Security Policy - NTP-MCP v1.0

## Security Features

### Geographic Filtering
This MCP implements geographic security filtering to block potentially untrusted sources:
- Certain country-code top-level domains
- Known problematic service providers
- Domains associated with security risks

### IP Address Blocking
- All direct IPv4 addresses blocked
- All direct IPv6 addresses blocked
- Only domain names from approved list allowed

### Default Deny Policy
- Only whitelisted servers are allowed
- Unknown servers are blocked by default
- 25 approved servers from reputable providers

### Additional Security
- Rate limiting: 60 requests per minute
- Response caching: 30 second TTL
- Input validation on server names
- Timeout protection on NTP requests

## Approved Servers
Run `list_approved_servers` tool to see full list.

## Reporting Security Issues

Please report security vulnerabilities through GitHub's security advisories:
1. Go to the Security tab in the repository
2. Click on "Report a vulnerability"
3. Provide detailed information about the issue

Alternatively, you can open a private security advisory or contact the maintainers directly through GitHub.