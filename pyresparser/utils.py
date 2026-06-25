import re
import textract
import PyPDF2
from io import BytesIO
from collections import OrderedDict


def extract_text(file, ext):
    """Extract text from PDF or DOC/DOCX using textract or PyPDF2."""
    text = ''
    try:
        if ext == '.pdf':
            if isinstance(file, BytesIO):
                reader = PyPDF2.PdfReader(file)
            else:
                reader = PyPDF2.PdfReader(open(file, 'rb'))
            for page in reader.pages:
                text += page.extract_text() + '\n'
        else:
            text = textract.process(file).decode('utf-8')
    except Exception as e:
        print(f"Error extracting text: {e}")
    return text


def extract_email(text):
    """Extract email address from text."""
    match = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match[0] if match else None


def extract_mobile_number(text, custom_regex=None):
    """Extract mobile number using regex."""
    if custom_regex:
        pattern = re.compile(custom_regex)
    else:
        pattern = re.compile(r'\+?\d[\d\s\-()]{9,15}')
    matches = pattern.findall(text)
    for match in matches:
        match = re.sub(r'\D', '', match)
        if 10 <= len(match) <= 14:
            return match
    return None


def extract_skills(nlp_text, noun_chunks, skills_file=None):
    """Extract skills based on a given list or default list."""
    SKILLS = [
        'python', 'java', 'c++', 'machine learning', 'deep learning', 'html', 'css',
        'flask', 'django', 'data science', 'sql', 'tableau', 'excel', 'powerpoint'
    ]
    if skills_file:
        with open(skills_file, 'r') as f:
            SKILLS = [line.strip().lower() for line in f.readlines()]

    tokens = [token.text.lower() for token in nlp_text if not token.is_stop]
    noun_chunks = [chunk.text.lower().strip() for chunk in noun_chunks]

    found_skills = set()
    for skill in SKILLS:
        if skill in tokens or skill in noun_chunks:
            found_skills.add(skill)

    return list(found_skills)


def get_total_experience(text):
    """Dummy placeholder: return experience in months if found."""
    return 0


def get_number_of_pages(file):
    """Return number of pages in a PDF."""
    try:
        if isinstance(file, BytesIO):
            reader = PyPDF2.PdfReader(file)
        else:
            reader = PyPDF2.PdfReader(open(file, 'rb'))
        return len(reader.pages)
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return 0


def extract_entities_wih_custom_model(nlp_text):
    """Fake extractor for name, degree, designation, company."""
    labels = ['Name', 'Degree', 'Designation', 'Companies worked at']
    dummy = {label: [] for label in labels}

    for ent in nlp_text.ents:
        if ent.label_ == 'PERSON':
            dummy['Name'].append(ent.text)
        elif ent.label_ == 'ORG':
            dummy['Companies worked at'].append(ent.text)
        elif ent.label_ in ['EDUCATION', 'QUALIFICATION']:
            dummy['Degree'].append(ent.text)
        elif ent.label_ in ['JOB', 'TITLE']:
            dummy['Designation'].append(ent.text)

    return dummy


def extract_entity_sections_grad(text):
    """Very basic section extractor based on section keywords."""
    sections = OrderedDict()
    lines = text.split('\n')
    current_section = None

    for line in lines:
        line = line.strip().lower()
        if 'education' in line:
            current_section = 'Education'
        elif 'experience' in line:
            current_section = 'experience'
        elif 'college' in line:
            current_section = 'College Name'

        if current_section:
            if current_section not in sections:
                sections[current_section] = ''
            sections[current_section] += line + '\n'

    return sections
