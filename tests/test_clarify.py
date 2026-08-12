from someone_already_made_it.clarify import plan_clarify
from someone_already_made_it.closure import expansion_queries
from someone_already_made_it.extract import names_from_hit


def test_clarify_dislike_notion():
    p = plan_clarify("I don't like Notion")
    assert p["inferred_products"] == ["Notion"]
    slots = [q["slot"] for q in p["questions"]]
    assert "pain" in slots
    assert "job" in slots
    assert len(p["questions"]) <= 5


def test_clarify_fitbit_gap():
    p = plan_clarify("I want to manage Fitbit from my laptop")
    assert "Fitbit" in p["inferred_products"]
    assert p["questions"][0]["slot"] == "pain"


def test_expansion_queries():
    qs = expansion_queries("Tavily", "AI agents")
    assert any("alternatives" in q for q in qs)
    assert any("vs" in q for q in qs)


def test_names_from_hit_repo():
    names = names_from_hit(
        {
            "title": "browser-use/browser-use",
            "url": "https://github.com/browser-use/browser-use",
            "content": "Make websites accessible for AI agents",
        }
    )
    assert any("browser-use" in n.lower() or "Browser" in n for n in names)
