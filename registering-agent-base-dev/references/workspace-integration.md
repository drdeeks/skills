# Base Builder Code Registration - Workspace Integration

## Agent Workspace Integration (Phase 5)

When registering an agent in a structured workspace (e.g., `~/hermes-agent/workspaces/agent-allman`):

### 5a. Update agent.json
```json
{
  "builderCode": {
    "code": "bc_p7hkhhor",
    "hex": "0x62635f7037686b68686f72",
    "owner": "0x...",
    "hardwired": true,
    "enforced": true
  },
  "builder_code_enforcement": {
    "required_for_all_agents": true,
    "auto_add_to_agent_json": true,
    "auto_add_to_config": true,
    "verify_before_creation": true,
    "builder_code": "bc_p7hkhhor",
    "builder_code_hex": "0x62635f7037686b68686f72",
    "owner": "0x..."
  }
}
```

### Builder Code to Hex Conversion
```python
"0x" + "bc_p7hkhhor".encode().hex()  # e.g. "0x62635f7037686b68686f72"
```

### 5b. Update systemd service
```bash
sudo sed -i 's|WorkingDirectory=.*|WorkingDirectory=/path/to/workspace|' /etc/systemd/system/<service-name>.service
sudo systemctl daemon-reload
```

### 5c. Clean up old files
Remove files created in wrong locations after copying to correct workspace.
