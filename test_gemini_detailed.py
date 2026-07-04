#!/usr/bin/env python
"""Test script to verify Gemini API resume analysis with different files."""
import sys
from pathlib import Path
import requests
import json

# Try different resume files
test_resume_dir = Path("Backend/app/Uploaded_Resume")
resume_files = sorted(list(test_resume_dir.glob("*.pdf")))

if not resume_files:
    print("❌ No test resume files found in Backend/app/Uploaded_Resume/")
    sys.exit(1)

# Use the Hanzala resume (better structured data)
test_file = None
for f in resume_files:
    if "Hanzala" in f.name:
        test_file = f
        break

if not test_file:
    test_file = resume_files[0]

print(f"✓ Using test file: {test_file.name}")

# Upload the file with Gemini provider
url = "http://localhost:8000/api/analyze"
with open(test_file, "rb") as f:
    files = {"file": f}
    data = {"provider": "gemini"}
    
    print("\n📤 Uploading resume to backend with Gemini provider...")
    print(f"   File: {test_file.name}")
    response = requests.post(url, files=files, data=data, timeout=60)

if response.status_code == 200:
    result = response.json()
    print("\n✅ Upload successful with Gemini!")
    print(f"\n📋 Extracted Information:")
    print(f"   Provider used: {result.get('provider_used')}")
    print(f"   Candidate name: {result['personal_info'].get('name', 'N/A')}")
    print(f"   Email: {result['personal_info'].get('email', 'N/A')}")
    print(f"   Mobile: {result['personal_info'].get('mobile_number', 'N/A')}")
    print(f"   College: {result['personal_info'].get('college_name', 'N/A')}")
    print(f"   Degree: {result['personal_info'].get('degree', 'N/A')}")
    print(f"   Designation: {result['personal_info'].get('designation', 'N/A')}")
    print(f"   Total Experience: {result.get('total_experience', 'N/A')} years")
    
    skills = result.get('skills', [])
    print(f"   Skills ({len(skills)}): {', '.join(skills[:5])}{'...' if len(skills) > 5 else ''}")
    
    companies = result['personal_info'].get('company_names', [])
    print(f"   Companies: {', '.join(companies) if companies else 'N/A'}")
    
    print(f"\n🎯 ATS Score: {result['ats_score']['overall']}/100")
    print(f"   Recommended field: {result.get('recommendation', {}).get('predicted_field', 'N/A')}")
    
    recommended_skills = result.get('recommendation', {}).get('recommended_skills', [])
    if recommended_skills:
        print(f"   Recommended skills: {', '.join(recommended_skills[:3])}{'...' if len(recommended_skills) > 3 else ''}")
    
    print(f"\n✨ Gemini extraction completed successfully!")
else:
    print(f"\n❌ Upload failed with status {response.status_code}")
    print(f"Error: {response.text}")
    sys.exit(1)
