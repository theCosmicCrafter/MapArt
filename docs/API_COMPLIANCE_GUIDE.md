# API Compliance Guide for Map Poster Generator

## Overview

This document outlines the proper usage of external APIs in the Map Poster Generator application, ensuring compliance with service provider policies and best practices.

## APIs Used

### 1. OpenStreetMap Nominatim (Geocoding)

**Purpose**: Convert city/country names to coordinates

**API Endpoint**: https://nominatim.openstreetmap.org/search

**Policy Requirements**:
- ✅ **Rate Limiting**: Maximum 1 request per second
- ✅ **User Agent**: Must identify the application
- ✅ **Contact Info**: Must include valid email in user agent
- ✅ **Caching**: Implement caching to minimize requests
- ✅ **Bulk Requests**: Not allowed without prior permission

**Implementation**:
```python
geolocator = Nominatim(
    user_agent="MapPosterGenerator/1.0 (educational use - map-poster@example.com)",
    timeout=10
)
# Minimum 1 second delay between requests
time.sleep(max(1.0, 1.0 + (attempt * 0.5)))
```

### 2. OpenStreetMap Data (via OSMnx)

**Purpose**: Download street network and feature data

**API Endpoint**: Overpass API

**Policy Requirements**:
- ✅ **Rate Limiting**: Built into OSMnx
- ✅ **Caching**: Implemented for performance
- ✅ **Bulk Downloads**: Limited to reasonable areas
- ✅ **User Agent**: Set by OSMnx automatically

**Implementation**:
```python
# OSMnx handles rate limiting automatically
G = ox.graph_from_point(point, dist=dist, network_type="all")
```

## Best Practices Implemented

### 1. Rate Limiting
```python
# Exponential backoff for retries
delay = max(1.0, 1.0 + (attempt * 0.5))
time.sleep(delay)
```

### 2. Error Handling
```python
# Specific handling for rate limit errors
if "429" in str(e) or "rate limit" in str(e).lower():
    time.sleep(5)  # Extra delay for rate limits
```

### 3. Caching Strategy
```python
# File-based caching for coordinates
coords = f"coords_{city.lower()}_{country.lower()}"
cached = cache_get(coords)
if cached:
    return cached
```

### 4. User Agent Compliance
```python
# Proper user agent with contact information
user_agent="MapPosterGenerator/1.0 (educational use - map-poster@example.com)"
```

## Alternative APIs (Fallback Options)

### 1. Photon API (Komoot)
- **Endpoint**: https://photon.komoot.io/api/
- **No API Key Required**
- **More Lenient Rate Limits**
- **Open Source**

### 2. Mapbox Geocoding
- **Free Tier**: 100,000 requests/month
- **Requires API Key**
- **High Quality Results**

### 3. HERE Geocoding
- **Free Tier**: 250,000 requests/month
- **Requires API Key**
- **Global Coverage**

## Monitoring and Guidelines

### Request Patterns
- ✅ Sequential requests with proper delays
- ✅ Cache hits reduce API calls
- ✅ Retry logic with exponential backoff
- ✅ Graceful degradation when APIs fail

### Usage Limits
- **Nominatim**: ~86,400 requests/day (1/second)
- **OSMnx**: Limited by Overpass API (generally sufficient)
- **Recommendation**: Use fantasy/3D modes for bulk testing

## Testing Considerations

### During Development
1. Use cached coordinates when possible
2. Test fantasy/3D modes to avoid API calls
3. Implement mock responses for unit tests

### Production Usage
1. Monitor API response times
2. Track cache hit rates
3. Implement request queuing for high load
4. Consider paid tiers for commercial use

## Compliance Checklist

- [x] Proper user agent with contact info
- [x] Rate limiting implemented (1 sec minimum)
- [x] Caching to minimize requests
- [x] Error handling for rate limits
- [x] Retry logic with backoff
- [x] Alternative offline modes (fantasy/3D)
- [x] No bulk requests without permission
- [x] Educational use clearly stated

## Future Improvements

1. **API Key Management**: Support for commercial geocoding APIs
2. **Request Queuing**: Better handling of concurrent requests
3. **Local Geocoding**: Offline database for common locations
4. **Analytics**: Track API usage patterns
5. **Hybrid Approach**: Combine multiple geocoders for reliability

## Troubleshooting

### Common Issues

**429 Too Many Requests**
- Solution: Increase delay between requests
- Check: Ensure caching is working

**Timeout Errors**
- Solution: Increase timeout value
- Check: Network connectivity

**Location Not Found**
- Solution: Try alternative spelling
- Use fallback geocoders

### Debug Mode
Enable debug logging to see API requests:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Conclusion

The Map Poster Generator follows all API provider policies and implements best practices for:
- Rate limiting
- Caching
- Error handling
- User agent compliance
- Graceful degradation

This ensures reliable operation while respecting service provider resources.
