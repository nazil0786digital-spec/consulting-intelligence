from app.contracts import Citation


DEMO_ORGANIZATION = "demo-consulting"

SOURCES = [
    {
        "id": "release-notes-26-2",
        "title": "Aggregate Reporting 26.2 Release Notes",
        "section": "Known limitations",
        "text": "After upgrade, report result differences can occur when legacy inclusion rules remain enabled. Validate report configuration and recalculate the source population.",
    },
    {
        "id": "inc-481",
        "title": "INC-481: Aggregate report count mismatch",
        "section": "Resolution",
        "text": "A client observed a count mismatch after upgrade. Root cause was a legacy inclusion-rule setting. The team corrected configuration and reran the report.",
    },
]


def citations_for(issue_text: str) -> list[Citation]:
    terms = set(issue_text.lower().split())
    ranked = sorted(SOURCES, key=lambda source: len(terms.intersection(source["text"].lower().split())), reverse=True)
    return [
        Citation(source_id=source["id"], title=source["title"], section=source["section"], excerpt=source["text"])
        for source in ranked
    ]
