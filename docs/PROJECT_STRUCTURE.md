# Project Structure

## Active V1 Runtime Modules
- Backend/app/api.py: API entry points and response serialization
- Backend/app/services/analysis_service.py: runtime orchestration
- Backend/app/parser/custom_parser.py: local parser
- Backend/app/parser/llm_extractor.py: Gemini extractor (optional selected provider)
- Backend/app/parser/text_extraction.py: raw text extraction
- Backend/app/validation/validator.py: file validation
- Backend/app/knowledge/repository.py: normalization and unknown-skill tracking
- Backend/app/ats/engine.py: ATS scoring
- Backend/app/recommendation/engine.py: recommendations

## Legacy / Optional Modules
- Backend/app/parser/pyresparser_adapter.py: kept as an optional adapter but not part of the active V1 runtime strategy
- Backend/app/parser/llm_extractor.py contains a legacy Ollama implementation that is intentionally not wired into the active V1 runtime path

## What Should Not Be Touched Casually
- analysis_service.py: this is the main orchestration layer
- validator.py: file handling should remain conservative and explicit
- knowledge repository: changes here affect skill normalization globally
