# Architecture Summary

NextRoute relies on `NetworkX` mapping the transportation system as a `MultiDiGraph`.
- **Nodes**: Stations / Bus Stops
- **Edges**: Route Segments (Trains/Buses)
- **Scoring**: A weighted factor model aggregating safety, reliability, cost, and duration into a final 0-100 score.
