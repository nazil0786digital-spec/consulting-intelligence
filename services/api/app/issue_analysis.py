import re


MODULE_PATTERNS = {
    "Aggregate Reporting": ("aggregate reporting", "pader", "report"),
    "Case Processing": ("case processing", "case intake", "case workflow"),
    "Safety Database": ("safety database", "database", "record"),
}


def analyze_issue(issue_text: str) -> tuple[dict[str, str | None], list[str]]:
    """Extract only explicit, reviewable issue clues; do not infer missing facts."""
    normalized = issue_text.lower()
    version_match = re.search(r"\b(?:version\s*)?(\d{1,2}\.\d{1,2}(?:\.\d+)?)\b", issue_text, re.IGNORECASE)
    client_match = re.search(r"\bclient\s+(.+?)\s+(?:reports|has|is|was|after|on|with)\b", issue_text, re.IGNORECASE)
    module = next(
        (name for name, terms in MODULE_PATTERNS.items() if any(term in normalized for term in terms)),
        None,
    )
    issue_type = (
        "upgrade or configuration issue"
        if any(term in normalized for term in ("upgrade", "version", "configuration", "migration"))
        else "requires evidence review"
    )
    context = {
        "client": client_match.group(1).strip() if client_match else None,
        "product": None,
        "module": module,
        "version": version_match.group(1) if version_match else None,
        "issue_type": issue_type,
    }
    missing = []
    if not context["client"]:
        missing.append("affected client")
    if not context["module"]:
        missing.append("affected module")
    if not context["version"]:
        missing.append("product version")
    if not any(term in normalized for term in ("error", "log", "expected", "actual", "count", "result")):
        missing.append("expected and actual result or relevant logs")
    return context, missing
