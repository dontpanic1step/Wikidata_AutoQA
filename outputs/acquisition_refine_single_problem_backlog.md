# Workflow Problem Backlog

This file tracks issues that should be reviewed beyond the narrow per-template loop.

- `acquisition_purchase_price`: Live run completed with request-layer errors
  Evidence: {"total_requests": 5, "network_requests": 15, "cache_hits": 0, "retry_count": 10, "errors": 5, "events": [{"url": "https://query.wikidata.org/sparql?query=SELECT+%3Fstmt+%3Ftarget+%3Facquirer+%3Fstart+WHERE+%7B%0A++%3Ftarget+p%3AP127+%3Fstmt.%0A++%3Fstmt+ps%3AP127+%3Facquirer%3B%0A++++++++pq%3AP580+%3Fstart%3B%0A++++++++pq%3AP2130+%3FpriceLiteral.%0A++FILTER%28%3Fstart+%3E%3D+%222026-01-01T00%3A00%3A00Z%22%5E%5Exsd%3AdateTime%29%0A++FILTER%28%3Fstart+%3C%3D+%222026-01-31T23%3A59%3A59Z%22%5E%5Exs
  Next step: Review request events and decide whether the instability is query-specific or environment-specific.
