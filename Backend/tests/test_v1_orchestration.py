import unittest
from pathlib import Path

from app.api import ATSScoreResponse, AnalysisResponse, PersonalInfo, RecommendationResponse
from app.services.analysis_service import ResumeAnalysisService


class DummyExtractor:
    def __init__(self, parsed_data=None, raw_text="") -> None:
        self.parsed_data = parsed_data or {}
        self.raw_text = raw_text
        self.calls = []

    def extract(self, resume_path: Path):
        self.calls.append(resume_path)
        return {"parsed_data": self.parsed_data, "raw_text": self.raw_text}


class V1OrchestrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ResumeAnalysisService(provider="custom_rule")

    def test_quality_scoring_requires_core_fields(self) -> None:
        weak = {"name": "Jane Doe", "skills": []}
        strong = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "mobile_number": "+1-555-123-4567",
            "skills": ["Python", "FastAPI"],
            "experience": "Senior Software Engineer",
            "education": "BS Computer Science",
        }

        weak_score = self.service._score_extraction_quality(weak, "")
        strong_score = self.service._score_extraction_quality(strong, "Python FastAPI")

        self.assertLess(weak_score, 0.7)
        self.assertGreaterEqual(strong_score, 0.7)

    def test_merge_prefers_non_empty_values_from_fallback(self) -> None:
        local = {
            "name": "Jane Doe",
            "email": None,
            "skills": ["Python"],
            "experience": "",
            "education": "",
        }
        fallback = {
            "name": "",
            "email": "jane@example.com",
            "skills": ["FastAPI", "Docker"],
            "experience": "Senior Software Engineer",
            "education": "BS Computer Science",
        }

        merged = self.service._merge_extraction_results(local, fallback)

        self.assertEqual(merged["email"], "jane@example.com")
        self.assertIn("FastAPI", merged["skills"])
        self.assertEqual(merged["experience"], "Senior Software Engineer")
        self.assertEqual(merged["education"], "BS Computer Science")

    def test_runtime_stays_single_provider_for_v1(self) -> None:
        service = ResumeAnalysisService(provider="custom_rule")
        service.extractor = DummyExtractor(parsed_data={"name": "Jane Doe"}, raw_text="Jane Doe")
        fallback_extractor = DummyExtractor(parsed_data={"name": "Fallback"}, raw_text="Fallback")
        service.fallback_extractor = fallback_extractor

        result = service.analyze_resume(Path("dummy.pdf"))

        self.assertEqual(result.provider_used, "custom_rule")
        self.assertFalse(result.fallback_used)
        self.assertEqual(fallback_extractor.calls, [])

    def test_analysis_response_exposes_runtime_metadata(self) -> None:
        response = AnalysisResponse(
            success=True,
            filename="resume.pdf",
            provider_used="custom_rule",
            fallback_used=False,
            confidence_score=0.78,
            personal_info=PersonalInfo(
                name="Jane Doe",
                professional_title="Software Engineer",
                email="jane@example.com",
                mobile_number=None,
                address=None,
                linkedin=None,
                github=None,
                portfolio=None,
                website=None,
                college_name=None,
                degree=None,
                designation=None,
                company_names=[],
                no_of_pages=1,
                candidate_level="Fresher",
            ),
            skills=["Python"],
            technical_skills=["Python"],
            soft_skills=[],
            skill_categories={},
            normalized_skill_map=[],
            experience=None,
            experiences=[],
            total_experience=0.0,
            projects=[],
            project_details=[],
            education=None,
            education_entries=[],
            summary=None,
            certifications=[],
            languages=[],
            awards=[],
            publications=[],
            interests=[],
            ats_score=ATSScoreResponse(
                overall=80,
                breakdown=[],
                strengths=[],
                improvements=[],
                keywords_found=[],
                section_coverage={},
            ),
            recommendation=RecommendationResponse(),
        )

        self.assertEqual(response.provider_used, "custom_rule")
        self.assertFalse(response.fallback_used)
        self.assertEqual(response.confidence_score, 0.78)


if __name__ == "__main__":
    unittest.main()
