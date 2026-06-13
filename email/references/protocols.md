# Email Protocols Reference

## Protocols

| Protocol | Purpose | Port |
|----------|---------|------|
| SMTP | Sending email | 587, 465 |
| IMAP | Reading email | 993 |
| POP3 | Download email | 995 |

## SMTP Commands

| Command | Description |
|---------|-------------|
| HELO/EHLO | Identify client |
| MAIL FROM | Specify sender |
| RCPT TO | Specify recipient |
| DATA | Start message body |
| QUIT | End session |

## Authentication Methods

| Method | Security | Usage |
|--------|----------|-------|
| Plain | Low | Legacy systems |
| Login | Medium | Basic auth |
| CRAM-MD5 | Medium | Challenge-response |
| OAuth2 | High | Modern clients |

## Email Headers

```
From: sender@example.com
To: recipient@example.com
Subject: Hello
Date: Mon, 01 Jan 2024 00:00:00 +0000
Message-ID: <unique-id@example.com>
Content-Type: text/plain; charset=UTF-8
```

## Troubleshooting

| Issue | Check |
|-------|-------|
| Email not sending | SMTP credentials, port, firewall |
| Email in spam | SPF, DKIM, DMARC records |
| Connection timeout | DNS resolution, network |
| Authentication failed | App password, OAuth token |
