# 05 — MCP service layer

**Change:** Place each domain behind a local typed HTTP boundary.  
**Reason:** Timeouts, correlation, errors and independent deployment become explicit.  
**Limitation revealed:** Network access requires a trusted caller identity.
