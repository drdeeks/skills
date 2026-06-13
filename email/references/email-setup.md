# Email Configuration Guide

## IMAP Settings

| Provider | Server | Port | SSL |
|----------|--------|------|-----|
| Gmail | imap.gmail.com | 993 | Yes |
| Outlook | outlook.office365.com | 993 | Yes |
| Yahoo | imap.mail.yahoo.com | 993 | Yes |

## SMTP Settings

| Provider | Server | Port | SSL |
|----------|--------|------|-----|
| Gmail | smtp.gmail.com | 587 | STARTTLS |
| Outlook | smtp.office365.com | 587 | STARTTLS |
| Yahoo | smtp.mail.yahoo.com | 587 | STARTTLS |

## Authentication

### Gmail
1. Enable 2FA
2. Generate App Password
3. Use App Password for SMTP/IMAP

### Outlook
1. Enable SMTP in account settings
2. Use OAuth2 or app password

## Common Issues

| Issue | Solution |
|-------|----------|
| Connection refused | Check port and SSL settings |
| Auth failed | Use app-specific password |
| Timeout | Check firewall rules |
| Certificate error | Update CA certificates |
