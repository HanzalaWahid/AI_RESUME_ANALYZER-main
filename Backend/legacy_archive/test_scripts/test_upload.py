#!/usr/bin/env python
"""Test script to verify resume upload and analysis workflow."""
import sys
from pathlib import Path
import requests

# Find a test resume file
test_resume_dir = Path("Backend/app/Uploaded_Resume")
resume_files = list(test_resume_dir.glob("*.pdf"))

if not resume_files:
    print("❌ No test resume files found in Backend/app/Uploaded_Resume/")
    sys.exit(1)

test_file = resume_files[0]
print(f"✓ Using test file: {test_file.name}")

# Upload the file
url = "http://localhost:8000/api/analyze"
with open(test_file, "rb") as f:
    files = {"file": f}
    data = {"provider": "custom_rule"}
    
    print("\n📤 Uploading resume to backend...")
    response = requests.post(url, files=files, data=data)

if response.status_code == 200:
    result = response.json()
    print("\n✅ Upload successful!")
    print(f"Provider used: {result.get('provider_used')}")
    print(f"Candidate name: {result['personal_info'].get('name', 'N/A')}")
    print(f"Email: {result['personal_info'].get('email', 'N/A')}")
    print(f"ATS Score: {result['ats_score']['overall']}/100")
    print(f"Recommended field: {result.get('recommendation', {}).get('predicted_field', 'N/A')}")
else:
    print(f"\n❌ Upload failed with status {response.status_code}")
    print(f"Error: {response.text}")
    sys.exit(1)
