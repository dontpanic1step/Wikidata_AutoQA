# Error Bucket Harvest Benchmark Summary

| Domain | Heavy (s) | Light (s) | Faster | Speedup | Heavy Candidates | Light Candidates | Heavy Bottleneck | Light Bottleneck | Heavy Retries | Light Retries |
|---|---:|---:|---|---:|---:|---:|---|---|---:|---:|
| beverage_manufacturer | 94.454 | 74.171 | light | 1.27 | 2 | 1 | wbgetentities | wbgetentities | 2 | 1 |
| company_that_released_product_founder | 30.466 | 31.088 | heavy | 1.02 | 0 | 0 | exception | exception | 0 | 0 |
| literary_magazine_country | 1037.996 | 586.225 | light | 1.77 | 0 | 0 | wbgetentities | wbgetentities | 1 | 8 |
| person_birth_date | 8.107 | 17.834 | heavy | 2.2 | 10 | 10 | wbgetentities | wdqs_query | 0 | 0 |
| person_death_date | 11.013 | 26.387 | heavy | 2.4 | 10 | 10 | wbgetentities | wbgetentities | 0 | 1 |
| species_parent_taxon | 41.427 | 37.467 | light | 1.11 | 0 | 10 | unknown | wbgetentities | 0 | 0 |
| stadium_architect | 3.624 | 58.922 | heavy | 16.26 | 0 | 17 | wdqs_query | wbgetentities | 0 | 0 |
| tv_series_creator | 101.633 | 91.309 | light | 1.11 | 0 | 0 | wbgetentities | wdqs_query | 3 | 5 |
| university_country | 98.211 | 1099.066 | heavy | 11.19 | 0 | 10 | wdqs_query | wbgetentities | 0 | 10 |
