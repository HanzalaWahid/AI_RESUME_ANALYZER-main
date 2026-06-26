from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

from ..ats.engine import RuleBasedATSScorer
from ..config import get_extractor_provider, get_max_upload_size_mb
from ..knowledge.repository import KnowledgeRepository
from ..models import ATSResult, RecommendationResult, ResumeAnalysisResult, ResumeData
from ..parser.custom_parser import CustomRuleBasedExtractor
from ..parser.llm_extractor import GeminiExtractor, OllamaExtractor
from ..parser.pyresparser_adapter import PyresparserExtractor
from ..recommendation.engine import RuleBasedRecommendationEngine
from ..validation.validator import validate_resume

logger = logging.getLogger(__name__)


class ResumeAnalysisService:
    """Service layer that orchestrates resume validation, extraction, ATS scoring, and recommendations."""

    def __init__(self, provider: str | None = None) -> None:
        self.provider = provider or get_extractor_provider()
        self.extractor = self._get_extractor(self.provider)
        self.ats_engine = RuleBasedATSScorer()
        self.recommendation_engine = RuleBasedRecommendationEngine()
        self.knowledge_repo = KnowledgeRepository()

    def _get_extractor(self, provider: str) -> Any:
        provider = provider.lower()
        if provider == "gemini":
            try:
                return GeminiExtractor()
            except Exception as e:
                logger.warning("Failed to initialize GeminiExtractor: %s. Falling back to CustomRuleBasedExtractor.", e)
                return CustomRuleBasedExtractor()
        elif provider == "ollama":
            try:
                return OllamaExtractor()
            except Exception as e:
                logger.warning("Failed to initialize OllamaExtractor: %s. Falling back to CustomRuleBasedExtractor.", e)
                return CustomRuleBasedExtractor()
        elif provider == "pyresparser":
            return PyresparserExtractor()
        
        # Default fallback is our custom rule-based extractor
        return CustomRuleBasedExtractor()

    def validate_file(self, resume_path: Path) -> tuple[bool, list[str]]:
        """Validate the resume file size, signature, and integrity before processing."""
        max_size = get_max_upload_size_mb()
        return validate_resume(resume_path, max_size)

    def analyze_resume(self, resume_path: Path) -> ResumeAnalysisResult:
        # 1. Extraction
        extracted = self.extractor.extract(resume_path)
        parsed_data = extracted.get("parsed_data", {})
        raw_text = extracted.get("raw_text", "")

        # 2. Knowledge Layer: Resolve and normalize skills
        raw_skills = parsed_data.get("skills") or []
        resolved_skills = []
        for skill in raw_skills:
            resolved = self.knowledge_repo.resolve_skill(skill)
            resolved_skills.append(resolved)
            # Log unrecognized skills for system review
            if not self.knowledge_repo.is_known_skill(skill):
                self.knowledge_repo.log_unknown_skill(skill)

        # Update parsed data skills list with normalized names
        parsed_data["skills"] = list(set(resolved_skills))

        # 3. ATS Scoring
        ats_payload = self.ats_engine.score(parsed_data, raw_text)
        
        # 4. Career Field Recommendation
        recommendation_payload = self.recommendation_engine.recommend(parsed_data, raw_text)

        # 5. Populate Data Transfer Models
        resume_data = ResumeData(
            name=parsed_data.get("name"),
            email=parsed_data.get("email"),
            mobile_number=parsed_data.get("mobile_number"),
            skills=parsed_data.get("skills") or [],
            college_name=parsed_data.get("college_name"),
            degree=parsed_data.get("degree"),
            designation=parsed_data.get("designation"),
            company_names=parsed_data.get("company_names") or [],
            experience=parsed_data.get("experience"),
            total_experience=parsed_data.get("total_experience") or 0.0,
            no_of_pages=parsed_data.get("no_of_pages") or 0,
            projects=parsed_data.get("projects") or [],
            internships=parsed_data.get("internships") or [],
            achievements=parsed_data.get("achievements") or [],
            hobbies=parsed_data.get("hobbies") or [],
            interests=parsed_data.get("interests") or [],
            objective=parsed_data.get("objective"),
            education=parsed_data.get("education"),
            summary=parsed_data.get("summary"),
            raw_text=raw_text,
        )

        ats_result = ATSResult(
            score=ats_payload["score"],
            section_coverage=ats_payload["section_coverage"],
            explanations=ats_payload["explanations"],
            keywords_found=ats_payload["keywords_found"],
            sub_scores=ats_payload["sub_scores"],
            detailed_explanations=ats_payload["detailed_explanations"],
        )

        recommendation_result = RecommendationResult(
            predicted_field=recommendation_payload.get("predicted_field"),
            recommended_skills=recommendation_payload.get("recommended_skills") or [],
            recommended_courses=recommendation_payload.get("recommended_courses") or [],
            recommended_videos=recommendation_payload.get("recommended_videos") or [],
            notes=recommendation_payload.get("notes"),
        )

        candidate_level = self._detect_candidate_level(raw_text)

        return ResumeAnalysisResult(
            resume_data=resume_data,
            ats_result=ats_result,
            recommendation=recommendation_result,
            raw_text=raw_text,
            candidate_level=candidate_level,
        )

    def _detect_candidate_level(self, text: str) -> str:
        normalized_text = text.lower()
        if any(keyword in normalized_text for keyword in ["internship", "internships", "trainee"]):
            return "Intermediate"
        if any(keyword in normalized_text for keyword in ["experience", "work experience"]):
            return "Experienced"
        return "Fresher"
