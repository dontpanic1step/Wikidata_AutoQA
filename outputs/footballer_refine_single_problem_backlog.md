# Workflow Problem Backlog

This file tracks issues that should be reviewed beyond the narrow per-template loop.

- `footballer_goals_in_ordinal_tournament`: Live run completed with request-layer errors
  Evidence: {"total_requests": 10, "network_requests": 30, "cache_hits": 0, "retry_count": 20, "errors": 10, "events": [{"url": "https://query.wikidata.org/sparql?query=SELECT+%3Fedition+%3Fseries+%3Fdate+%3FseriesPropertyPid+%3FdatePropertyPid+WHERE+%7B%0A++%3Fedition+wdt%3AP179+%3Fseries%3B%0A+++++++++++wdt%3AP585+%3Fdate.%0A++FILTER%28%3Fdate+%3E%3D+%222026-01-01T00%3A00%3A00Z%22%5E%5Exsd%3AdateTime%29%0A++FILTER%28%3Fdate+%3C%3D+%222026-01-31T23%3A59%3A59Z%22%5E%5Exsd%3AdateTime%29%0A++BIND%28%22P179%22
  Next step: Review request events and decide whether the instability is query-specific or environment-specific.
