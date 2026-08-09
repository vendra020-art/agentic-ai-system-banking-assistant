# 08 — Session management

**Change:** Keep bounded, per-session conversation history in memory.  
**Reason:** Follow-up turns and agent results need isolated context.  
**Limitation revealed:** Model choice should not leak into every agent.
