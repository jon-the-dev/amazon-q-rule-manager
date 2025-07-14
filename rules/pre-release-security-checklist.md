# Pre-Release Security and Quality Checklist

This checklist is designed for LLM review of codebases before public release under GPL or MIT licenses. Each item should be verified and marked as ✅ PASS, ❌ FAIL, or ⚠️ REVIEW NEEDED.

## 🔐 Security & Credentials

### Secrets and API Keys

- [ ] No hardcoded API keys, tokens, or secrets in source code
- [ ] No AWS access keys, secret keys, or session tokens
- [ ] No database passwords or connection strings with credentials
- [ ] No private keys, certificates, or cryptographic materials
- [ ] No OAuth client secrets or JWT signing keys
- [ ] Check `.env`, `.env.example`, config files, and comments
- [ ] Verify no secrets in git history (use `git log --all --full-history -- **/*secret*` type searches)

### Personal Information

- [ ] No real email addresses (use placeholders like `user@example.com`)
- [ ] No real names, phone numbers, or addresses
- [ ] No internal company information or employee details
- [ ] No customer data or personally identifiable information (PII)
- [ ] No internal URLs, server names, or infrastructure details

### Authentication & Authorization

- [ ] No default or weak passwords
- [ ] No hardcoded authentication bypasses
- [ ] No debug authentication modes left enabled
- [ ] Proper input validation and sanitization
- [ ] No SQL injection vulnerabilities
- [ ] No command injection possibilities

## 📁 File System & Configuration

### Sensitive Files

- [ ] Ensure a .gitignore exists to prevent future development from adding unnecessary files
- [ ] No `.env` files with real credentials
- [ ] No backup files (`.bak`, `.old`, `.backup`)
- [ ] No IDE configuration with sensitive paths
- [ ] No deployment scripts with production credentials
- [ ] No database dumps or exports
- [ ] No log files with sensitive information

### Configuration Files

- [ ] Docker files don't expose unnecessary ports or services
- [ ] CI/CD configurations don't contain secrets
- [ ] Package.json/requirements.txt don't reference private repositories
- [ ] No internal registry or repository URLs

## 🏗️ Code Quality & Documentation

### Documentation

- [ ] README.md exists and is comprehensive
- [ ] Installation instructions are clear and complete
- [ ] Usage examples are provided
- [ ] API documentation is accurate
- [ ] License file is present and correct (GPL/MIT)
- [ ] Contributing guidelines exist if accepting contributions
- [ ] Security policy or contact information provided

### Code Structure

- [ ] No TODO comments referencing internal systems
- [ ] No debug print statements or console.log with sensitive data
- [ ] No commented-out code blocks with credentials
- [ ] Proper error handling without information disclosure
- [ ] No development/testing endpoints in production code

## 🔗 Dependencies & Third-Party

### Package Dependencies

- [ ] All dependencies are from public repositories
- [ ] No internal or private package references
- [ ] Dependencies are up-to-date and secure (check for known vulnerabilities)
- [ ] License compatibility check (GPL/MIT compatible dependencies)
- [ ] No unnecessary or unused dependencies

### External Services

- [ ] No references to internal APIs or services
- [ ] External API endpoints are documented and public
- [ ] No internal monitoring or logging service integrations
- [ ] Webhook URLs are examples or configurable

## 🚀 Deployment & Infrastructure

### Infrastructure References

- [ ] No internal server names, IPs, or hostnames
- [ ] No cloud account IDs or resource ARNs
- [ ] No internal DNS names or network configurations
- [ ] Docker images reference public registries only
- [ ] No internal load balancer or proxy configurations

### Environment Configuration

- [ ] Environment variables are documented
- [ ] Default values are safe for public use
- [ ] No production environment configurations
- [ ] Database connections use localhost/examples by default

## 📊 Data & Privacy

### Sample Data

- [ ] Test data contains no real information
- [ ] Database seeds/fixtures use placeholder data
- [ ] Example configurations use example.com domains
- [ ] No real user accounts or profiles in examples

### Logging & Monitoring

- [ ] Log statements don't expose sensitive information
- [ ] No internal monitoring system integrations
- [ ] Error messages don't reveal system internals
- [ ] No telemetry pointing to internal systems

## 🧪 Testing & Development

### Test Files

- [ ] Test credentials are fake/placeholder only
- [ ] No integration tests pointing to production systems
- [ ] Mock data doesn't contain real information
- [ ] Test configurations are safe for public use

### Development Tools

- [ ] No IDE-specific files with sensitive paths
- [ ] Debug configurations don't expose internals
- [ ] Development scripts use safe defaults
- [ ] No profiling or debugging code in production paths

## 📋 Legal & Compliance

### Licensing

- [ ] License file matches intended license (GPL/MIT)
- [ ] All source files have appropriate license headers
- [ ] Third-party code attribution is correct
- [ ] No proprietary code or algorithms included

### Intellectual Property

- [ ] No copyrighted material without permission
- [ ] No trademarked names or logos without rights
- [ ] No patented algorithms or processes
- [ ] Original work or properly attributed open source

## 🔍 Final Review

### Manual Verification

- [ ] Clone repository fresh and test installation
- [ ] Verify all examples work with public data only
- [ ] Check that application runs without internal dependencies
- [ ] Confirm documentation matches actual functionality
- [ ] Test with minimal/default configuration

### Automated Checks

- [ ] Run security scanners (e.g., bandit, semgrep, CodeQL)
- [ ] Check for secrets with tools like truffleHog or git-secrets
- [ ] Verify license compatibility with FOSSA or similar
- [ ] Run dependency vulnerability scans

## 📝 Review Notes

Use this section to document any findings, exceptions, or additional notes:

```bash
Date: ___________
Reviewer: ___________
Version/Commit: ___________

Findings:
- 

Actions Taken:
- 

Approved for Release: [ ] Yes [ ] No
Signature: ___________
```

## 🚨 Red Flags - Immediate Review Required

If any of these are found, **STOP** and conduct thorough manual review:

- Any string containing "password", "secret", "key", "token" with actual values
- Email addresses from your organization's domain
- Internal IP addresses (10.x.x.x, 192.168.x.x, 172.16-31.x.x)
- Cloud provider account IDs or resource identifiers
- Database connection strings with real credentials
- API endpoints pointing to internal services
- Comments mentioning internal systems, people, or processes

## Reporting

- Generate a report called PRE_RELEASE_$TIMESTAMP.md
- NEVER show the exposed token/secret - redact all but the last 4 chars to allow for validation

## 📞 Escalation

If uncertain about any item, escalate to:

- Security team for credential/security concerns
- Legal team for licensing/IP questions  
- Engineering lead for technical architecture questions

---

**Remember**: It's better to be overly cautious than to accidentally expose sensitive information. When in doubt, redact or replace with placeholder values.
