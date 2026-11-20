"""The design is 3 categories x 5 intents x 4 wordings x 3 models x 10 repeats."""
from study.design import CATEGORIES, INTENTS, REPEATS, build_prompts, build_units
from study.gates import design_check


def test_design_has_sixty_unique_prompts():
    prompts = build_prompts()
    assert len(prompts) == len({p["prompt_id"] for p in prompts}) == 60
    assert design_check() == []


def test_every_prompt_is_rendered_for_its_category():
    for p in build_prompts():
        assert "{" not in p["text"]
        assert CATEGORIES[p["category"]] in p["text"]
        assert p["intent"] in INTENTS


def test_full_run_is_1800_units_with_unique_ids():
    providers = ["claude", "gpt", "gemini"]
    units = build_units({p: f"{p}-model" for p in providers}, providers)
    assert len(units) == 60 * len(providers) * REPEATS == 1800
    assert len({u["id"] for u in units}) == 1800
