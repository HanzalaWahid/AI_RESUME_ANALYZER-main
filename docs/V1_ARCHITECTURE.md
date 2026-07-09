# V1 Architecture

## Purpose
The V1 architecture is a cost-conscious, maintainable MVP for resume analysis. It prioritizes a local parser first, optional Gemini fallback for weak extraction, and a simple, explainable pipeline that can be understood and extended by a small engineering team.

## Design Decisions
- Keep the first-pass parser local and deterministic.
- Use either the local parser or Gemini as a selected single provider for each analysis run.
- Keep the architecture modular enough for future expansion without over-engineering V1.
- Exclude Ollama from the active runtime path in V1.

## High-Level Architecture
```text
Resume Upload
  -> File Validation
  -> Text Extraction
  -> Selected Extractor
  -> Knowledge Normalizer
  -> ATS Scorer
  -> Recommendation Engine
  -> Analysis Result / UI
```

## Runtime Flow
1. The upload endpoint accepts a PDF or DOCX file.
2. The validator checks file type, size, and structure.
3. Text extraction reads the document content.
4. The selected extractor attempts structured extraction.
5. The parsed data is enriched and normalized.
6. The normalized data feeds ATS scoring and recommendations.
7. The final payload is returned to the frontend.

## Module Responsibilities
- api.py: request handling, validation response mapping, and output shaping
- services/analysis_service.py: orchestration of the runtime pipeline
- parser/custom_parser.py: V1 local extraction logic
- parser/llm_extractor.py: Gemini fallback integration
- parser/text_extraction.py: extraction of raw text from PDF/DOCX
- validation/validator.py: file integrity and safety checks
- knowledge/repository.py: skill normalization and unknown-skill logging
- ats/engine.py: ATS scoring and breakdown generation
- recommendation/engine.py: skill and career recommendations

## Parser Strategy
The V1 parser strategy favors deterministic rules and low operational cost. Gemini is only used when the local parser produces sparse or weak output.

## Extractor Strategy
V1 supports one selected extractor per run. The default path is the custom rule-based parser, and Gemini is available when explicitly selected via configuration or request input.

## ATS Scoring Flow
The ATS scorer uses extracted fields such as name, email, skills, experience, education, and projects to generate a score and explainable sub-scores.

## Recommendation Flow
The recommendation engine consumes the normalized extraction result and suggests likely career fields, skills, and resources.

## Normalization / Knowledge Layer Role
The knowledge layer normalizes extracted skill names, resolves common aliases, and records unknown skills for future review.

## Why Ollama Is Excluded from V1
Ollama is excluded from V1 to keep the architecture simple, predictable, and easier to document. V1 prioritizes a local parser plus a single fallback provider rather than a broader local-model strategy.

## Current Limitations
- OCR for scanned PDFs is not part of V1.
- The extraction path is single-provider per run.
- The system is not yet a full production provider router.
- The knowledge layer is limited to normalization and unknown-skill logging.
