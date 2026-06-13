# Find Nearby Subskill

## Overview
Location-based discovery for nearby points of interest, events, and activities.

## Features
- Search by category (food, entertainment, outdoor, etc.)
- Filter by distance, rating, price
- Get directions and contact info
- Save favorites

## Usage
```bash
# Find nearby restaurants
find-nearby --category food --radius 5km

# Find events this weekend
find-nearby --category events --date weekend

# Find parks and outdoor activities
find-nearby --category outdoor --radius 10km
```

## Data Sources
- OpenStreetMap
- Google Places API
- Yelp API
- Eventbrite API

## Configuration
```yaml
# ~/.config/leisure/find-nearby.yaml
default_radius: 5km
preferred_categories:
  - food
  - entertainment
  - outdoor
api_keys:
  google_places: ${GOOGLE_PLACES_API_KEY}
  yelp: ${YELP_API_KEY}
```
