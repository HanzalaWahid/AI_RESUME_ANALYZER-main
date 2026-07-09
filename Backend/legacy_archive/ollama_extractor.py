from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict
import requests

from app.parser.interfaces import ResumeExtractor
from app.parser.text_extraction import extract_text
from app.config import get_env

logger = logging.getLogger(__name__)


class OllamaExtractor(ResumeExtractor):
    """
    Resume extractor that leverages a local Ollama server to extract structured JSON data.
    Archived from V1 runtime to keep active flow clean of local model dependencies.
    """

    def __init__(self, host: str | None = None, model: str | None = None) -> None:
        self.host = host or get_env("OLLAMA_BASE_URL") or get_env("OLLAMA_HOST", "http://localhost:11434")
        self.model = model or get_env("OLLAMA_MODEL", "llama3")

    def extract(self, resume_path: Path) -> Dict[str, Any]:
        raw_text = extract_text(resume_path)
        if not raw_text:
            return {"parsed_data": {}, "raw_text": ""}

        prompt = f"""
You are an expert AI Resume Parser. Extract structured information from the following resume text as a JSON block.
Do not output any introductory text, prefix, suffix or conversational filler. Output raw JSON only.

JSON Schema:
{{
  "name": "Candidate Name (string or null)",
    "professional_title": "current professional title (string or null)",
  "email": "email address (string or null)",
  "mobile_number": "phone number (string or null)",
    "address": "candidate location/address (string or null)",
    "linkedin": "linkedin url (string or null)",
    "github": "github url (string or null)",
    "portfolio": "portfolio url (string or null)",
    "website": "personal website url (string or null)",
  "skills": ["list of skills"],
    "technical_skills": ["technical skills only"],
    "soft_skills": ["soft skills only"],
    "skill_categories": {{"category_name": ["skills"]}},
  "college_name": "college name (string or null)",
  "degree": "degree (string or null)",
  "designation": "designation (string or null)",
  "company_names": ["companies"],
  "experience": "experience (string or null)",
    "experiences": [
        {{
            "company": "string",
            "position": "string",
            "employment_period": "string",
            "location": "string",
            "responsibilities": ["list"],
            "achievements": ["list"],
            "technologies_used": ["list"]
        }}
    ],
  "total_experience": (float number),
  "projects": ["projects"],
    "project_details": [{{"name": "string", "description": "string", "technologies": ["list"]}}],
  "internships": ["internships"],
  "achievements": ["achievements"],
    "certifications": ["list of certifications"],
    "languages": ["list of spoken languages"],
    "awards": ["list of awards"],
    "publications": ["list of publications"],
  "hobbies": ["hobbies"],
  "interests": ["interests"],
  "objective": "objective (string or null)",
  "education": "education (string or null)",
    "education_entries": [{{"degree": "string", "institution": "string", "dates": "string", "gpa": "string", "coursework": ["list"]}}],
  "summary": "summary (string or null)"
}}

Resume text:
{raw_text}
"""
        url = f"{self.host}/api/chat"
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "format": "json"
        }

        try:
            logger.info("Calling local Ollama API on %s with model %s...", self.host, self.model)
            response = requests.post(url, json=payload, timeout=45)
            response.raise_for_status()
            data = response.json()
            
            content_text = data['message']['content']
            parsed_json = json.loads(content_text)
            
            return {
                "parsed_data": parsed_json,
                "raw_text": raw_text
            }
        except Exception as e:
            logger.error("Ollama API call failed: %s", e)
            raise RuntimeError(f"Ollama extraction failed: {e}")
