# Smart Home Automation Patterns

## Common Automations
- **Motion-activated lights**: Turn on when motion detected, off after timeout
- **Presence simulation**: Randomize lights when away
- **Climate control**: Adjust thermostat based on occupancy/schedule
- **Security alerts**: Notify on door/window sensors when armed
- **Energy monitoring**: Track and optimize usage

## Implementation
```yaml
automation:
  - trigger: motion_detected
    condition: after_sunset
    action: turn_on_lights
    delay: 300
    action: turn_off_lights
```

## Best Practices
- Use conditions to prevent unwanted triggers
- Add delays for user experience
- Test thoroughly before deploying
- Include manual overrides
- Log all automation executions
