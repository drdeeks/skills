# Smart Home Device Protocols

## Supported Protocols
- **Zigbee**: Low-power mesh network (IEEE 802.15.4)
- **Z-Wave**: Sub-GHz mesh network
- **Thread**: IPv6-based mesh (Matter compatible)
- **Matter**: Unified connectivity standard
- **Wi-Fi**: Direct IP connectivity
- **Bluetooth LE**: Short-range devices

## Bridge/Hub Requirements
- Zigbee: Coordinator (e.g., ConBee, Sonoff)
- Z-Wave: Controller (e.g., Aeotec, Zooz)
- Thread: Border router (e.g., HomePod, Google Nest)
- Matter: Controller + Thread border router

## Integration Patterns
- Local control (no cloud dependency)
- Cloud-to-local bridge
- MQTT bridge for Home Assistant
