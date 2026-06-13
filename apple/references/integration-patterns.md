# Apple Integration Patterns

Patterns for integrating with Apple ecosystem services.

## Authentication

- iCloud account required for most services
- Shortcuts may require explicit permission grants
- Keychain access for credential storage

## API Access

- AppleScript for direct macOS automation
- Shortcuts app for workflow automation
- Command-line tools: `osascript`, `shortcuts`

## Limitations

- iMessage requires Messages.app running
- Some services need user approval per session
- Cross-platform compatibility limited to macOS
