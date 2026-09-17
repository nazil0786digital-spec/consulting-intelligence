from dataclasses import dataclass

from app.contracts import EvaluationCaseResult, EvaluationReport
from app.fixtures import DEMO_ORGANIZATION, citations_for


@dataclass(frozen=True)
class BaselineScenario:
    id: str
    issue_text: str
    expected_source_ids: set[str]


BASELINE_SCENARIOS = (
    BaselineScenario(
        id="post_upgrade_count_mismatch",
        issue_text="PADER report counts differ after an upgrade to version 26.2.",
        expected_source_ids={"release-notes-26-2", "inc-481"},
    ),
    BaselineScenario(
        id="legacy_rule_investigation",
        issue_text="Investigate whether legacy inclusion rules explain the aggregate report difference.",
        expected_source_ids={"release-notes-26-2", "inc-481"},
    ),
)


def run_baseline_evaluation() -> EvaluationReport:
    """Run only sanitized fixture scenarios; customer workspaces are never used as test data."""
    results = []
    for scenario in BASELINE_SCENARIOS:
        returned = {citation.source_id for citation in citations_for(scenario.issue_text)}
        missing = sorted(scenario.expected_source_ids - returned)
        results.append(
            EvaluationCaseResult(
                scenario_id=scenario.id,
                passed=not missing,
                checks={"expected_citations_returned": not missing, "organization_scope": DEMO_ORGANIZATION == "demo-consulting"},
                detail="Expected sanitized evidence sources were retrieved." if not missing else f"Missing expected sources: {', '.join(missing)}.",
            )
        )
    return EvaluationReport(
        suite="phase_3_baseline",
        total_cases=len(results),
        passed_cases=sum(result.passed for result in results),
        results=results,
    )
