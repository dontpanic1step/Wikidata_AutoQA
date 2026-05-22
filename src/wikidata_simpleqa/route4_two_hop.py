"""Route 4 Wikidata two-hop public API."""

from __future__ import annotations

from .route1_hidden_entity import (
    CLUE_HIDDEN_OBJECT,
    CLUE_HIDDEN_SUBJECT,
    HIDDEN_ENTITY_REASONING_STYLE,
    ROUTE4_TWO_HOP_CONTRACT,
    ROUTE4_WIKIDATA_TWO_HOP_ROUTE,
    Route1HiddenEntityTwoHopComposer as Route4TwoHopComposer,
    Route1HiddenEntityTwoHopSeedUnit as Route4TwoHopSeedUnit,
    attach_hidden_entity_seed_metadata as attach_route4_two_hop_seed_metadata,
    hidden_entity_seed_key_from_record as route4_two_hop_seed_key_from_record,
    hidden_entity_seed_unit_from_candidate as route4_two_hop_seed_unit_from_candidate,
)
from .route4_template_catalog import (
    get_route4_reviewed_single_hop_templates,
    get_route4_reviewed_template_by_key,
)
from .route4_two_hop_template_catalog import (
    Route4TwoHopTemplate,
    get_route4_combinable_single_hop_templates,
    get_route4_two_hop_template_catalog,
    get_route4_two_hop_template_summary,
    get_route4_uncombined_single_hop_templates,
)


def get_route4_two_hop_single_hop_templates(templates):
    """Return single-hop templates usable by Route 4 two-hop composition."""
    from .route1_hidden_entity import get_route1_hidden_entity_single_hop_templates

    return get_route1_hidden_entity_single_hop_templates(templates)
