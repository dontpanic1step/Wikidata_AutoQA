"""Tests for deterministic review-bundle filtering."""

from __future__ import annotations

import unittest

from test_support import ROOT  # noqa: F401
from scripts.build_review_bundle import record_invalid_reasons


class BuildReviewBundleTests(unittest.TestCase):
    """Check filtering of accepted records before review export."""

    def test_retired_domain_is_filtered_from_review_bundle(self) -> None:
        reasons = record_invalid_reasons(
            {
                "domain": "company_industry",
                "question": "What industry is the company Example in?",
                "answer": "software industry",
            }
        )
        self.assertEqual(reasons, ["retired_template"])


if __name__ == "__main__":
    unittest.main()
