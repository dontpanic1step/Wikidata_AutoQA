# Workflow Problem Backlog

This file tracks issues that should be reviewed beyond the narrow per-template loop.

- `ordinal_country_prime_minister`: Live run completed with request-layer errors
  Evidence: {"total_requests": 7, "network_requests": 7, "cache_hits": 4, "retry_count": 4, "errors": 2, "events": [{"url": "https://query.wikidata.org/sparql?query=SELECT+%3Fsubject+%3Foffice+WHERE+%7B%0A++%3Fsubject+wdt%3AP31%2Fwdt%3AP279%2A+wd%3AQ6256.%0A++%7B+%3Foffice+wdt%3AP1001+%3Fsubject.+%7D+UNION+%7B+%3Foffice+wdt%3AP17+%3Fsubject.+%7D%0A++%3Foffice+rdfs%3Alabel+%3FofficeLabel.%0A++FILTER%28LANG%28%3FofficeLabel%29+%3D+%22en%22%29%0A++FILTER%28CONTAINS%28LCASE%28STR%28%3FofficeLabel%29%29%2C+%22pr
  Next step: Review request events and decide whether the instability is query-specific or environment-specific.
