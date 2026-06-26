from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict
import requests

from .interfaces import ResumeExtractor
from .text_extraction import extract_text
from ..config import get_env

logger = logging.getLogger(__name__)


class GeminiExtractor(ResumeExtractor):
    """
    Resume extractor that leverages the Google Gemini API to parse unstructured text 
    into a structured JSON schema.
    """

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or get_env("GEMINI_API_KEY")

    def extract(self, resume_path: Path) -> Dict[str, Any]:
        raw_text = extract_text(resume_path)
        if not raw_text:
            return {"parsed_data": {}, "raw_text": ""}

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not configured. Please set it in your environment or configuration.")

        prompt = f"""
You are an expert AI Resume Parser. Analyze the following resume raw text and extract structured information.
You must output a valid JSON block containing the exact keys specified in the schema below.
Do not include any chat prefix/suffix or markdown formatting outside of the valid JSON block.

JSON Schema:
{{
  "name": "Candidate Name (string or null)",
  "email": "email address (string or null)",
  "mobile_number": "phone number (string or null)",
  "skills": ["list of technical and professional skills"],
  "college_name": "university/college name (string or null)",
  "degree": "academic degree name (string or null)",
  "designation": "latest or current job title/designation (string or null)",
  "company_names": ["list of companies worked at"],
  "experience": "raw summary or history of work experience (string or null)",
  "total_experience": (float number of years of experience, e.g. 2.5),
  "projects": ["list of major projects"],
  "internships": ["list of internships"],
  "achievements": ["list of honors/awards/achievements"],
  "hobbies": ["list of hobbies"],
  "interests": ["list of fields of interest"],
  "objective": "career objective (string or null)",
  "education": "summary description of education details (string or null)",
  "summary": "profile summary (string or null)"
}}

Resume text:
{raw_text}
"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }

        try:
            logger.info("Calling Gemini API for resume extraction...")
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            content_text = data['candidates'][0]['content']['parts'][0]['text']
            parsed_json = json.loads(content_text)
            
            return {
                "parsed_data": parsed_json,
                "raw_text": raw_text
            }
        except Exception as e:
            logger.error("Gemini API call failed: %s", e)
            raise RuntimeError(f"Gemini extraction failed: {e}")


class OllamaExtractor(ResumeExtractor):
    """
    Resume extractor that leverages a local Ollama server to extract structured JSON data.
    """

    def __init__(self, host: str | None = None, model: str | None = None) -> None:
        self.host = host or get_env("OLLAMA_HOST", "http://localhost:11434")
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
  "email": "email address (string or null)",
  "mobile_number": "phone number (string or null)",
  "skills": ["list of skills"],
  "college_name": "college name (string or null)",
  "degree": "degree (string or null)",
  "designation": "designation (string or null)",
  "company_names": ["companies"],
  "experience": "experience (string or null)",
  "total_experience": (float number),
  "projects": ["projects"],
  "internships": ["internships"],
  "achievements": ["achievements"],
  "hobbies": ["hobbies"],
  "interests": ["interests"],
  "objective": "objective (string or null)",
  "education": "education (string or null)",
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
