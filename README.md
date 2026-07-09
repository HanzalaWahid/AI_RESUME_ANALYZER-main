# AI Resume Analyzer – V1

AI Resume Analyzer is a backend-focused resume analysis MVP designed to help candidates and recruiters understand a resume’s structure, quality, and improvement potential. The V1 release focuses on a practical and maintainable architecture built around a selected extractor strategy, skill normalization, ATS-style scoring, and recommendations.

## 1. Overview
This project processes uploaded resumes in PDF or DOCX format, extracts structured information, normalizes skills, scores the resume for ATS-readiness, and returns recommendations. The V1 version is intentionally scoped to be credible, understandable, and maintainable rather than overly ambitious.

## 2. V1 Scope
The V1 release prioritizes:
- reliable upload and validation
- text extraction from PDF and DOCX
- local rule-based parsing as the default path
- optional Gemini extraction when explicitly selected
- normalization of extracted skills through a knowledge layer
- ATS-style scoring and career-field recommendations
- developer-friendly documentation and a clean service-oriented structure

## 3. Key Features
- PDF and DOCX support
- Resume file validation and safety checks
- Local rule-based extraction
- Single-provider extraction per analysis run
- Skill normalization and unknown-skill tracking
- ATS-style scoring with explainable breakdown
- Career-field and skill recommendation output
- FastAPI backend with React frontend integration

## 4. High-Level Architecture
```text
Resume Upload
  -> File Validation
  -> Text Extraction
  -> Selected Extractor
  -> Skill Normalization
  -> ATS Scoring
  -> Recommendation Engine
  -> Analysis Result / UI
```

## 5. Runtime Analysis Flow
The active V1 runtime flow is:
1. The backend accepts a resume upload.
2. The file is validated for format, size, and structure.
3. Text is extracted from PDF or DOCX.
4. The selected extractor runs for the analysis.
5. The extracted data is enriched and normalized.
6. ATS scoring and recommendations are generated.
7. The response is returned to the UI.

## 6. Project Structure
```text
Backend/
  app/
    api.py                  # FastAPI routes and response models
    config.py               # environment-driven configuration
    models.py               # analysis result models
    services/
      analysis_service.py   # main orchestration service
    parser/
      custom_parser.py      # V1 local parser
      llm_extractor.py      # Gemini extractor
      text_extraction.py    # PDF/DOCX text extraction
    validation/
      validator.py          # file validation logic
    knowledge/
      repository.py         # skill normalization + unknown-skill tracking
    ats/
      engine.py             # ATS scoring logic
    recommendation/
      engine.py             # recommendation logic
```

## 7. Setup Instructions
### Prerequisites
- Python 3.10+
- pip
- optional: a Gemini API key for fallback extraction

### Install dependencies
```bash
cd Backend
pip install -r requirements.txt
```

## 8. Environment Variables
Create a `.env` file in the project root or Backend folder with values such as:
```env
EXTRACTOR_PROVIDER=auto
GEMINI_API_KEY=your_gemini_key
MAX_UPLOAD_SIZE_MB=5.0
```

## 9. Running the Application
### Backend
```bash
cd Backend
python main.py
```

The API will be available at:
- http://localhost:8000/docs

### Frontend
```bash
cd "resume Analyzer frontend"
cc
npm run dev
```

## 10. Example Analysis Flow
A user uploads a resume.
The backend validates the file, extracts text, runs the local parser, optionally invokes Gemini, normalizes skills, scores ATS readiness, and returns a structured analysis payload.

## 11. ATS Scoring Summary
The V1 ATS engine is rule-based and explainable. It evaluates:
- contact and profile completeness
- experience section quality
- education details
- projects presence
- skill coverage
- section formatting signals
- simple keyword alignment

## 12. Recommendation Engine Summary
The recommendation engine uses detected keywords and known resume signals to suggest:
- likely career field
- recommended skills
- relevant learning resources

## 13. Limitations
The V1 release is intentionally limited. It does not yet provide:
- fully production-grade OCR for scanned PDFs
- a full multi-provider router or key pool
- deep field-by-field merge logic across multiple providers
- enterprise-grade observability and retries
- broad domain generalization for all resume styles

## 14. Roadmap / V1.5 Preview
The next phase will focus on:
- stronger confidence scoring
- provider routing and multiple API key pools
- merge logic between multiple providers
- OCR and scanned-resume support
- graceful partial-failure handling
- production observability and reliability
