# Weather API Formats

## wttr.in Formats

### One-line Summary
```
curl "wttr.in/London?format=3"
# Output: London: ☀️ +22°C
```

### Custom Format
```
curl "wttr.in/London?format=%l:+%c+%t+(feels+like+%f),+%w+wind,+%h+humidity"
# Output: London: ☀️ +22°C (feels like +24°C), 10km/h wind, 65% humidity
```

### Format Codes
| Code | Description |
|------|-------------|
| `%l` | Location |
| `%c` | Weather condition emoji |
| `%t` | Temperature |
| `%f` | Feels like temperature |
| `%w` | Wind |
| `%h` | Humidity |
| `%p` | Precipitation |
| `%P` | Pressure |
| `%u` | UV index |

### Output Types
| Parameter | Description |
|-----------|-------------|
| `?0` | Current conditions (ANSI) |
| `?1` | Tomorrow forecast |
| `?2` | Day after tomorrow |
| `?format=v2` | Week forecast (visual) |
| `?format=j1` | JSON output |
| `.png` | PNG image |

## Open-Meteo Formats

### Current Weather
```
curl "https://api.open-meteo.com/v1/forecast?latitude=51.51&longitude=-0.13&current_weather=true"
```

### Forecast
```
curl "https://api.open-meteo.com/v1/forecast?latitude=51.51&longitude=-0.13&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=auto"
```

### Parameters
| Parameter | Description |
|-----------|-------------|
| `latitude` | Latitude (-90 to 90) |
| `longitude` | Longitude (-180 to 180) |
| `current_weather` | Include current weather |
| `daily` | Daily forecast variables |
| `hourly` | Hourly forecast variables |
| `timezone` | Timezone (auto or IANA) |
