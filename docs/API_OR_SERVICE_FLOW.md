# API / Service Flow

## Main Service Entry Point
The main service entry point for V1 is the analysis service in Backend/app/services/analysis_service.py.

## What AnalysisService Does
The service coordinates the analysis pipeline from file input to result output. It is responsible for:
- selecting the active parser strategy
- validating the extraction quality of the local parser output
- selecting the active single extractor
- normalizing extracted fields
- generating ATS scoring data
- generating recommendation data
- returning a structured result model

## Expected Input
The analysis service expects a file path to a resume file. In the active runtime path, the FastAPI route passes a temporary uploaded file path.

## Expected Output
The service returns a ResumeAnalysisResult object with:
- resume_data
- ats_result
- recommendation
- raw_text
- candidate_level
- provider_used
- fallback_used
- confidence_score

## Step-by-Step Analysis Pipeline
1. The file is received by the API route.
2. The file is saved to a temporary path.
3. The validator checks the file.
4. The analysis service selects the local parser.
5. The selected extractor extracts structured data and raw text.
6. The result is enriched and normalized.
7. ATS and recommendation engines run.
8. A final response object is returned.

## Failure Points
Potential failure points include:
- invalid upload type or size
- unreadable or corrupted PDF/DOCX
- empty extracted text
- missing Gemini configuration when Gemini is selected
- malformed or low-quality AI output

## How the Backend Could Be Exposed Later
The current service logic is already structured so that it could be exposed through additional REST endpoints, background jobs, or queue-based tasks. The service layer is the natural boundary for future API expansion.
