# AgentMail Setup Guide

Step-by-step guide for setting up AgentMail for agent automation.

## Prerequisites

1. Create account at agentmail.to
2. Generate API key from dashboard
3. Install Python package: `pip install agentmail`

## Configuration

Store API key in `.secrets/.agentmail-[agent-name]`:
```
AGENTMAIL_API_KEY=am_xxxxxxxxxxxx
```

## Python Version Note

AgentMail requires Python 3.12+. If using a virtual environment with 3.11, use system Python explicitly:
```bash
python3.12 -c "from agentmail import AgentMail; print('OK')"
```
