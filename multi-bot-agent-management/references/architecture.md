# Multi-Bot Agent Management - Architecture

## Four-Bot Architecture

### Hermes Bot (@hermes_vpss_bot)
- Purpose: Communication with user
- Service: `telegram-bot.service`
- Commands: 58
- Token: User's Hermes token

### Titan Bot (@Titan_Smokes_Bot)
- Purpose: Infrastructure and development
- Service: `telegram-titan.service`
- Commands: 58
- Token: User's Titan token

### Avery Bot (@IvankaSlaw_Bot)
- Purpose: Child-safe agent for Ava
- Service: `telegram-avery.service`
- Commands: 18
- Token: User's Avery token

### Agent Allman Bot (@Agent_Allman_Bot)
- Purpose: Agent creation with ERC-8004 onchain identity
- Service: `telegram-agent-allman.service`
- Commands: 58
- Token: User's Agent Allman token
- Creates agents with builder code hardwired

## Key Components

1. **Agent Manager** - Creates agents with unique identities, auto-initializes workspace structure, hardwires builder code
2. **Workspace Structure** - Standardized directory layout (30+ directories), automatic file categorization
3. **Submission Handler** - Auto-detects content type, saves to correct directory, provides search and retrieval
4. **Builder Code Integration** - Hardcodes builder code into agent creation, ensures all agents inherit builder code
