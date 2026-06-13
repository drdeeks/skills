# Media API Integrations

## Giphy API
- **Endpoint**: https://api.giphy.com/v1/gifs
- **Auth**: API key required
- **Rate Limit**: 1000 requests/day (free)
- **Endpoints**: search, trending, translate, random

## Tenor API
- **Endpoint**: https://tenor.googleapis.com/v2
- **Auth**: API key required
- **Rate Limit**: Configurable
- **Endpoints**: search, trending, categories

## Spotify API
- **Endpoint**: https://api.spotify.com/v1
- **Auth**: OAuth 2.0
- **Rate Limit**: Variable
- **Endpoints**: search, playlists, tracks, artists

## YouTube Data API
- **Endpoint**: https://www.googleapis.com/youtube/v3
- **Auth**: API key / OAuth 2.0
- **Quota**: 10,000 units/day
- **Endpoints**: videos, channels, playlists, search

## youtube-transcript-api
- **Library**: https://github.com/jdepoix/youtube-transcript-api
- **No API key needed**
- **Rate Limited**: Respectful usage
- **Features**: Multi-language, timestamps, auto-generated

## Configuration
```yaml
# ~/.config/media/apis.yaml
giphy:
  api_key: ${GIPHY_API_KEY}
tenor:
  api_key: ${TENOR_API_KEY}
spotify:
  client_id: ${SPOTIFY_CLIENT_ID}
  client_secret: ${SPOTIFY_CLIENT_SECRET}
youtube:
  api_key: ${YOUTUBE_API_KEY}
```
