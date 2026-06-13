# AgentMail Troubleshooting

Common issues and solutions for AgentMail integration.

## ModuleNotFoundError

**Cause:** Wrong Python version
**Solution:** Use `python3.12` explicitly, not `python3`

## Rate Limited

**Cause:** Too many requests in short period
**Solution:** Wait 60-120 seconds between attempts

## Empty Inbox

**Cause:** Email not yet delivered
**Solution:** Poll with 5-second intervals, wait up to 60 seconds

## Verification Link Expired

**Cause:** Links expire after 10 minutes
**Solution:** Act quickly after receiving verification email
