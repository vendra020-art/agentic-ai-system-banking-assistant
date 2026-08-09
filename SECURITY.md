# Security policy

## Supported version

Security fixes are applied to the latest commit on `main`.

## Reporting a vulnerability

Please use GitHub's **Report a vulnerability** / private security advisory flow for this repository. Do not include real customer, account, card, identity or banking-system data in a report.

## Project boundary

Aegis Bank AI is a mock-first portfolio reference implementation. It contains synthetic data and a known demo-only bearer value; that value is not a credential and grants access only to local mock services. The repository must not be connected to a real bank, identity provider or customer-data source without a separate threat model, penetration test, privacy review and compliance approval.

See [docs/SECURITY.md](docs/SECURITY.md) for the implemented controls and documented production gaps.
