# Apple Troubleshooting

Common issues with Apple/macOS automation.

## Permission Errors

- Grant Full Disk Access in System Preferences > Security & Privacy
- Enable Accessibility access for automation
- Check Shortcuts permissions in System Preferences

## AppleScript Failures

- Ensure target application is running
- Check AppleScript syntax with `osascript -e 'return 1'`
- Verify application supports AppleScript

## iMessage Issues

- Messages.app must be running and signed in
- Phone number or email must match recipient
- Check iMessage is enabled in Messages preferences
