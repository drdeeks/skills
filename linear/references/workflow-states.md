# Linear Workflow States

## State Types (6 types)

| Type | Description | Typical Names |
|------|-------------|---------------|
| `triage` | Incoming issues needing review | "Triage", "New", "Inbox" |
| `backlog` | Acknowledged but not planned | "Backlog", "Icebox", "Later" |
| `unstarted` | Planned/ready but not started | "Todo", "Ready", "Planned" |
| `started` | Actively being worked on | "In Progress", "Doing", "Active" |
| `completed` | Done | "Done", "Completed", "Closed" |
| `canceled` | Won't do | "Won't Do", "Cancelled", "Rejected" |

## Querying States
```bash
# Get states for team
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ workflowStates(filter: { team: { key: { eq: \"ENG\" } } }) { nodes { id name type } } }"}'
```

## Changing Issue Status
1. Query workflow states for team to get target state UUID
2. Use `issueUpdate` mutation with `stateId`

```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: $LINEAR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { issueUpdate(id: \"ENG-123\", input: { stateId: \"STATE_UUID\" }) { success issue { identifier state { name type } } } }"}'
```

## Default Behavior
- Creating issue without `stateId` → first `backlog` type state
- Each team has its own named states
- State types are consistent across teams
