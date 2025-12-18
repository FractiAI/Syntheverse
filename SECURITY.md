# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| < 2.0   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability, please report it responsibly.

### How to Report

1. **Do not** open a public GitHub issue
2. Email security details to: info@fractiai.com
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

### Response Timeline

- We will acknowledge receipt within 48 hours
- We will provide an initial assessment within 7 days
- We will keep you informed of our progress
- We will notify you when the vulnerability is resolved

### Disclosure Policy

- We will not disclose vulnerabilities until they are fixed
- We will credit you for responsible disclosure (if desired)
- We will work with you to coordinate public disclosure

## Security Best Practices

### For Contributors

- Never commit API keys or secrets
- Use environment variables for sensitive data
- Validate all user inputs
- Follow secure coding practices
- Review code for security issues before submitting

### For Users

- Keep your API keys secure
- Use strong passwords for wallet access
- Verify contract addresses before transactions
- Report suspicious activity immediately
- Keep software dependencies up-to-date

## Known Security Considerations

### API Keys

- Store API keys in environment variables
- Never commit `.env` files to version control
- Rotate keys regularly
- Use different keys for development and production

### Smart Contracts

- Contracts are audited before mainnet deployment
- Use testnet for development and testing
- Verify contract addresses on block explorer
- Review contract code before interacting

### File Uploads

- Validate file types and sizes
- Scan uploaded files for malicious content
- Store files securely
- Clean up temporary files

## Security Updates

Security updates will be announced through:
- GitHub Security Advisories
- Project documentation
- Email notifications (for critical issues)

## Contact

For security-related questions or concerns:
- Email: info@fractiai.com
- Subject: [SECURITY] Your Subject








