"""The distance and overlap measures behind every number in the paper."""
import pytest

from study.analyze import concentration, intent_gap, jaccard, ruzicka, stability, visibility


def test_ruzicka_identical_vectors_have_zero_distance():
    v = {"sony": 1.0, "bose": 0.5}
    assert ruzicka(v, v) == 0


def test_ruzicka_disjoint_vectors_have_distance_one():
    assert ruzicka({"sony": 1.0}, {"veja": 1.0}) == 1


def test_ruzicka_is_symmetric_and_weighted():
    a, b = {"sony": 1.0, "bose": 0.5}, {"sony": 0.5, "fairphone": 0.5}
    # shared mass 0.5 over total mass 1.0 + 0.5 + 0.5
    assert ruzicka(a, b) == pytest.approx(1 - 0.5 / 2.0)
    assert ruzicka(a, b) == ruzicka(b, a)


def test_ruzicka_two_empty_vectors():
    assert ruzicka({}, {}) == 0.0


def test_jaccard_overlap():
    assert jaccard({"a", "b"}, {"b", "c"}) == pytest.approx(1 / 3)
    assert jaccard(set(), set()) == 1.0


def test_visibility_is_share_of_answers_recommending_each_brand():
    rows = [{"rec": ["sony", "bose"]}, {"rec": ["sony"]}]
    assert visibility(rows) == {"sony": 1.0, "bose": 0.5}
    assert visibility([]) == {}


def test_intent_gap_separates_within_and_between_intent_pairs():
    cells = [{"a": 1.0}, {"a": 1.0}, {"b": 1.0}, {"b": 1.0}]
    labels = ["budget", "budget", "premium", "premium"]
    within, between = intent_gap(cells, labels)
    assert within == 0 and between == 1


def test_intent_gap_needs_both_kinds_of_pair():
    assert intent_gap([{"a": 1.0}, {"b": 1.0}], ["budget", "premium"]) is None


def test_stability_counts_identical_repeats():
    rows = [
        {"provider": "claude", "prompt_id": "p", "rec": ["sony", "bose"]},
        {"provider": "claude", "prompt_id": "p", "rec": ["sony", "bose"]},
        {"provider": "claude", "prompt_id": "p", "rec": ["sony"]},
    ]
    overlap, identical = stability(rows)
    assert identical["claude"] == pytest.approx(1 / 3)
    assert overlap["claude"][0] == pytest.approx((1 + 0.5 + 0.5) / 3)


def test_concentration_is_top_three_share():
    rows = [{"provider": "gpt", "category": "crm", "intent": "neutral",
             "rec": ["hubspot", "zoho", "salesforce", "pipedrive"]}]
    assert concentration(rows)[("gpt", "crm", "neutral")] == pytest.approx(3 / 4)
