FRAGMENT_CATEGORIES = {
    "trigger": ["when consumed", "on touch", "upon use"],
    "effect": ["removes ability", "grants immunity", "causes", "boosts", "gives an ability"],
    "trait": ["with moh", "glows brightly", "unbreakable", "lightweight", "steel-hard"],
    "region": ["found in forest", "deep sea", "tundra", "volcano", "underground"],
}


def detect_fragments(query: str) -> list:
    results = []
    lowered_query = query.lower()

    for category, fragments in FRAGMENT_CATEGORIES.items():
        for phrase in fragments:
            if phrase in lowered_query:
                results.append({
                    "category": category,
                    "fragment": phrase
                })

    return results
