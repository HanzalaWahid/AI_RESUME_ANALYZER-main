# Runbook

## Install Dependencies
```bash
cd Backend
pip install -r requirements.txt
```

## Configure Gemini
Set a Gemini API key in your environment:
```env
GEMINI_API_KEY=your_key_here
EXTRACTOR_PROVIDER=auto
```

## Run the Backend
```bash
cd Backend
python main.py
```

## Run the Frontend
```bash
cd "resume Analyzer frontend"
npm install
npm run dev
```

## Test Parsing on Sample Resumes
Upload a sample PDF or DOCX through the UI or invoke the analysis endpoint directly.

## Debugging Failed Extraction
Check:
- whether the file is text-based or scanned
- whether validation rejected the file
- whether the selected parser returned empty or sparse fields
- whether the selected provider is configured correctly

## Debugging Gemini Failures
If Gemini extraction fails, inspect:
- whether GEMINI_API_KEY is configured
- whether the package dependencies are available
- whether the API returned malformed or empty output

## Identifying Whether the Result Came from Local or Gemini
The response includes provider metadata through the service result object. In the current V1 flow, a result is marked as the selected provider for that run.

## Common Issues
- Unsupported file type
- Empty extracted text
- Missing Gemini key
- Very weak parser output on unusual resume formats
