# API Documentation

## `POST /api/v1/search/routes`
Search for routes between two stations.

**Request**
```json
{
  "from_code": "MDU",
  "to_code": "SBC",
  "date": "2026-08-05",
  "mode": "FASTEST"
}
```

**Response**
Returns an array of `ExplainedJourney` objects containing segments, durations, and overall score badges.

## `GET /api/v1/health`
Check system status and graph node counts.
