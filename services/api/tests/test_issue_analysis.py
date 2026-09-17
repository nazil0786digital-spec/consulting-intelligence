import unittest

from app.issue_analysis import analyze_issue


class IssueAnalysisTests(unittest.TestCase):
    def test_extracts_explicit_consulting_issue_context(self) -> None:
        context, missing = analyze_issue(
            "Client ABC Pharma reports PADER report count mismatch after upgrade to version 26.2. Expected 42, actual 37."
        )
        self.assertEqual(context["client"], "ABC Pharma")
        self.assertEqual(context["module"], "Aggregate Reporting")
        self.assertEqual(context["version"], "26.2")
        self.assertEqual(context["issue_type"], "upgrade or configuration issue")
        self.assertNotIn("product version", missing)

    def test_identifies_context_missing_from_a_vague_issue(self) -> None:
        _context, missing = analyze_issue("The workflow is not working as expected.")
        self.assertIn("affected client", missing)
        self.assertIn("affected module", missing)
        self.assertIn("product version", missing)
