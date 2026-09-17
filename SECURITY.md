# Security Policy

## Supported version

The latest release on the default branch is the supported product line. Older revisions may contain known or subsequently fixed security defects.

## Reporting a vulnerability

Do not publish sensitive vulnerability details in a public issue. Report the issue privately through the repository owner's configured GitHub security reporting channel or another private channel explicitly provided by the product owner.

Include:

- affected version or commit
- deployment mode (local, Docker Compose, HTTP enforcement, MCP enforcement)
- minimal reproduction steps
- expected versus observed behavior
- relevant logs with credentials and personal data removed

Do not include API tokens, signing secrets, database credentials, customer data, or other secrets in a report.

## Scope

The product's security boundary includes decision authenticity, tenant binding, action binding, expiry, one-time execution, approval binding and the tested HTTP/MCP enforcement paths. Infrastructure, customer identity systems, secret managers, networks and downstream tools remain deployment-specific security boundaries.
