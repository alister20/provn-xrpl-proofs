# Security Policy

## Reporting a vulnerability

If you believe you have found a security issue in this library, please report it privately. **Do not open a public GitHub issue for security reports.**

Email: **support@useprovn.io**

Please include:

- A short description of the issue
- Steps to reproduce, or a proof-of-concept
- The affected version (commit SHA or release tag)
- Your name and contact details, if you would like to be credited

You should expect an acknowledgement within five business days. We will keep you informed as we investigate and triage.

## Scope

This repository contains a read-only XRPL transaction verifier. Reports concerning the verifier code itself are in scope. Examples:

- Incorrect verification results (false positives or false negatives)
- Crash, hang, or denial-of-service triggered by RPC responses
- Insecure handling of user input in the CLI or library
- Supply-chain issues in declared dependencies

Reports concerning the broader Provn product, infrastructure, or commercial services are out of scope for this repository. Please direct those to **support@useprovn.io** with a clear note of which system the report concerns.

## Out of scope

- Issues in third-party XRPL nodes used as RPC endpoints
- Vulnerabilities in dependencies that have already been disclosed upstream
- Findings that require physical access to a user's machine

## Disclosure

We follow coordinated disclosure. Once a fix is available and users have had reasonable time to upgrade, we will publish a security advisory in this repository. Reporters who request credit will be acknowledged in the advisory.

## Supported versions

Only the latest release on `main` is supported with security fixes. Earlier releases are not maintained.
