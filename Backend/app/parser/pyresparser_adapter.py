from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

from pyresparser.resume_parser import ResumeParser

from .interfaces import ResumeExtractor

logger = logging.getLogger(__name__)


class PyresparserExtractor(ResumeExtractor):
    """Adapter that wraps the existing pyresparser ResumeParser."""

    def extract(self, resume_path: Path) -> Dict[str, Any]:
        parser = ResumeParser(str(resume_path))
        extracted = parser.get_extracted_data() or {}
        raw_text = parser.get_raw_text() or ""
        if not extracted and not raw_text:
            logger.warning("ResumeParser returned no extracted data or raw text for %s", resume_path)
        return {
            "parsed_data": extracted,
            "raw_text": raw_text,
        }
