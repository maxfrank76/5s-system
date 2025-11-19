# Security Policy

## Supported Versions

This is a prototype application. No versions are currently supported for production use.

## Reporting a Vulnerability

Since this is a prototype for demonstration purposes, security vulnerabilities are expected.

If you find a security issue, please:
1. Do not use this system in production
2. Understand that this is a learning/demonstration project
3. Consider contributing a fix if you have the expertise

## Security Limitations

This prototype has known security limitations:

- Passwords stored with basic hashing
- No protection against brute force attacks
- Session security not fully implemented
- SQL injection protection via ORM only
- No input sanitization for all endpoints
- No HTTPS enforcement
- No rate limiting

**DO NOT USE THIS SYSTEM TO STORE SENSITIVE DATA OR IN PRODUCTION ENVIRONMENTS**