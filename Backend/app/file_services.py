import os
from pathlib import Path

from werkzeug.utils import secure_filename


def save_uploaded_resume(uploaded_file):
    safe_name = secure_filename(uploaded_file.name)
    if not safe_name:
        raise ValueError('Invalid uploaded filename.')

    upload_dir = Path(__file__).resolve().parent / 'Uploaded_Resume'
    upload_dir.mkdir(exist_ok=True)

    target_path = upload_dir / f"{os.urandom(8).hex()}_{safe_name}"
    with open(target_path, 'wb') as fh:
        fh.write(uploaded_file.getbuffer())
    return target_path


from pyresparser.resume_parser import ResumeParser


def analyze_resume_file(resume_path):
    parser = ResumeParser(str(resume_path))
    return parser.get_extracted_data()
