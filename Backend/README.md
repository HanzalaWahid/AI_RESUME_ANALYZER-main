# AI Resume Analyzer Backend – V1

This backend provides the V1 runtime for the AI Resume Analyzer. It accepts uploaded resumes, validates them, extracts structured content through a selected parser provider, normalizes skills, scores ATS-readiness, and returns recommendations to the UI.

## V1 Scope
The current V1 release is intentionally focused on a credible, maintainable MVP:
- upload and validation for PDF and DOCX files
- text extraction from the uploaded document
- one selected extractor per analysis run
- skill normalization through the knowledge layer
- ATS-style scoring and recommendation generation
- FastAPI response shaping for the frontend

## Runtime Architecture
The active V1 flow is:
1. receive an uploaded resume
2. validate the file
3. extract raw text
4. run the selected extractor (custom rule-based parser by default, Gemini when explicitly selected)
5. normalize and enrich the parsed data
6. run ATS scoring and recommendation generation
7. return the analysis payload

## Core Modules
- app/api.py: FastAPI routes and response mapping
- app/services/analysis_service.py: orchestration of the runtime pipeline
- app/parser/custom_parser.py: default local extractor
- app/parser/llm_extractor.py: optional Gemini extractor
- app/parser/text_extraction.py: raw text extraction from PDF and DOCX
- app/validation/validator.py: file validation and safety checks
- app/knowledge/repository.py: skill normalization and unknown-skill logging
- app/ats/engine.py: ATS scoring
- app/recommendation/engine.py: recommendation generation

## Environment Variables
The backend reads configuration from environment variables and a local .env file.

Common settings:
- EXTRACTOR_PROVIDER=auto or custom_rule or gemini
- GEMINI_API_KEY=your key when Gemini is selected
- MAX_UPLOAD_SIZE_MB=5.0

## Local Setup
```bash
cd Backend
pip install -r requirements.txt
python main.py
```

The API will be available at http://localhost:8000/docs.

## Notes on V1
- Ollama is not part of the active V1 runtime path.
- V1 uses one selected extractor per run rather than a multi-provider orchestration flow.
- ATS and recommendations consume the normalized results produced by the selected extractor.

## Known Limitations
- OCR for scanned resumes is not part of V1.
- The runtime remains single-provider per run.
- The knowledge layer is currently focused on skill normalization and unknown-skill tracking.

