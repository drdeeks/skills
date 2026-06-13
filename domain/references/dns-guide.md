# DNS Configuration Guide

## Record Types

| Record | Purpose | Example |
|--------|---------|---------|
| A | Maps domain to IP | example.com → 1.2.3.4 |
| CNAME | Alias to another domain | www → example.com |
| MX | Mail server | example.com → mail.example.com |
| TXT | Text records (SPF, DKIM) | v=spf1 include:_spf.google.com ~all |
| NS | Name server | example.com → ns1.example.com |

## Common Configurations

### Website
```
A     @       1.2.3.4
CNAME www     example.com
```

### Email (Google Workspace)
```
MX    @       1  ASPMX.L.GOOGLE.COM
TXT   @       v=spf1 include:_spf.google.com ~all
```

### Subdomain
```
A     api     1.2.3.4
CNAME app     example.com
```

## TTL Recommendations

| Record Type | TTL |
|-------------|-----|
| A (stable) | 3600 |
| A (frequent changes) | 300 |
| MX | 3600 |
| TXT | 3600 |
