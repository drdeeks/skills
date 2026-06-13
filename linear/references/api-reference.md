# Linear GraphQL API Reference

## Endpoint
```
POST https://api.linear.app/graphql
Authorization: YOUR_API_KEY
Content-Type: application/json
```

## Core Types

### Viewer
```graphql
viewer {
  id
  name
  email
  assignedIssues(first: 25) { nodes { identifier title state { name type } priority url } }
}
```

### Team
```graphql
teams { nodes { id name key } }
workflowStates(filter: { team: { key: { eq: "ENG" } } }) { nodes { id name type } }
```

### Issue
```graphql
issue(id: "ENG-123") {
  id
  identifier
  title
  description
  priority
  state { id name type }
  assignee { id name }
  team { key }
  project { name }
  labels { nodes { name } }
  comments { nodes { body user { name } createdAt } }
  url
}
```

### Issue Filters
```graphql
issues(filter: {
  state: { type: { in: ["started"] } },
  team: { key: { eq: "ENG" } },
  assignee: { email: { eq: "user@example.com" } }
}, first: 20) {
  nodes { identifier title state { name } assignee { name } }
}
```

### Issue Search
```graphql
issueSearch(query: "bug login", first: 10) {
  nodes { identifier title state { name } assignee { name } url }
}
```

### Project
```graphql
projects(first: 20) { nodes { id name description progress lead { name } teams { nodes { key } } url } }
```

## Mutations

### Create Issue
```graphql
mutation($input: IssueCreateInput!) {
  issueCreate(input: $input) { success issue { id identifier title url } }
}
Variables: { "input": { "teamId": "UUID", "title": "Fix bug", "description": "...", "priority": 2 } }
```

### Update Issue
```graphql
mutation { issueUpdate(id: "ENG-123", input: { stateId: "STATE_UUID" }) { success issue { identifier state { name type } } } }
```

### Assign Issue
```graphql
mutation { issueUpdate(id: "ENG-123", input: { assigneeId: "USER_UUID" }) { success issue { identifier assignee { name } } } }
```

### Add Comment
```graphql
mutation { commentCreate(input: { issueId: "ISSUE_UUID", body: "Comment" }) { success comment { id body } } }
```

### Create Project
```graphql
mutation($input: ProjectCreateInput!) {
  projectCreate(input: $input) { success project { id name url } }
}
```

## Pagination
- Relay-style cursor pagination
- `first: N` (max 250, default 50)
- `after: "cursor"` for next page
- `pageInfo { hasNextPage endCursor }`
