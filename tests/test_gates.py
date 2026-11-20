"""The gates decide what counts as data. They must never pass a made-up brand."""
from study.gates import (MIN_HANDCHECK_ROWS, check_answer, check_coding, norm_text,
                         results_gate)

ANSWER = "For most runners I'd start with the Brooks Ghost 16. Avoid “budget” no-name pairs."


def coding(*brands, gives=True):
    return {"gives_recommendation": gives, "brands": list(brands)}


def brand(name, quote, stance="recommended"):
    return {"brand": name, "stance": stance, "quote": quote}


def test_quote_found_in_answer_passes():
    assert check_coding(coding(brand("Brooks", "the Brooks Ghost 16")), ANSWER) == []


def test_invented_quote_is_rejected():
    problems = check_coding(coding(brand("Zzyzx", "Zzyzx is great")), ANSWER)
    assert len(problems) == 1 and "not in the answer text" in problems[0]


def test_missing_quote_is_rejected():
    assert "has no quote" in check_coding(coding(brand("Brooks", "")), ANSWER)[0]


def test_quote_matching_ignores_case_punctuation_and_curly_quotes():
    assert norm_text("Avoid “budget” no-name") == norm_text('avoid "budget" no name')
    assert check_coding(coding(brand("Brooks", "BROOKS ghost 16.")), ANSWER) == []


def test_recommendation_flag_must_match_the_brand_stances():
    mentioned = brand("Brooks", "the Brooks Ghost 16", stance="mentioned")
    assert check_coding(coding(mentioned, gives=True), ANSWER)
    assert check_coding(coding(mentioned, gives=False), ANSWER) == []


def out(text="x" * 200, status="ok", served="model-a-2026"):
    return {"text": text, "status": status, "served_model": served}


def test_good_answer_is_accepted():
    v = check_answer(out(), "model-a")
    assert v.accept and not v.flag


def test_refusals_and_short_answers_are_kept_as_data():
    assert check_answer(out(status="refusal"), "model-a").flag == "refusal"
    short = check_answer(out(text="Buy Brooks."), "model-a")
    assert short.accept and short.flag == "short"


def test_technical_failures_are_retried():
    for bad in (out(status="truncated"), out(text="   ")):
        v = check_answer(bad, "model-a")
        assert not v.accept and v.retry


def test_wrong_served_model_is_rejected_without_retry():
    v = check_answer(out(served="model-b"), "model-a")
    assert not v.accept and not v.retry


def answers_and_codings(n, failed=0):
    codings = [{"provider": "claude", "check_failed": i < failed} for i in range(n)]
    return [], codings


def test_results_are_not_ready_without_a_human_handcheck():
    answers, codings = answers_and_codings(100)
    reasons = results_gate({"claude": 100}, answers, codings, {"checked": 0})
    assert any("hand-checked" in r for r in reasons)


def test_results_are_ready_when_complete_and_accurate():
    answers, codings = answers_and_codings(100)
    handcheck = {"checked": MIN_HANDCHECK_ROWS, "accuracy": 1.0}
    assert results_gate({"claude": 100}, answers, codings, handcheck) == []


def test_results_gate_stops_on_too_many_failures_or_low_accuracy():
    answers, codings = answers_and_codings(100, failed=5)
    handcheck = {"checked": MIN_HANDCHECK_ROWS, "accuracy": 0.85}
    reasons = results_gate({"claude": 100}, answers, codings, handcheck)
    assert any("missing or failed" in r for r in reasons)
    assert any("below" in r for r in reasons)
