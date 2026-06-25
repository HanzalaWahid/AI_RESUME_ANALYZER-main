import os
import multiprocessing as mp
import io
import spacy
import re
import pprint
from spacy.matcher import Matcher
from . import utils


class ResumeParser:

    def __init__(self, resume, skills_file=None, custom_regex=None):
        self.__nlp = spacy.load('en_core_web_sm')
        self.__custom_nlp = spacy.load("en_core_web_sm")
        self.__skills_file = skills_file
        self.__custom_regex = custom_regex
        self.__matcher = Matcher(self.__nlp.vocab)
        self.__resume = resume
        self.__details = {
            'name': None,
            'email': None,
            'mobile_number': None,
            'skills': None,
            'college_name': None,
            'degree': None,
            'designation': None,
            'experience': None,
            'company_names': None,
            'no_of_pages': None,
            'total_experience': None,
            'projects': None,
            'internships': None,
            'achievements': None,
            'hobbies': None,
            'interests': None,
            'objective': None,
            'education': None,
            'summary': None
        }

        ext = os.path.splitext(self.__resume)[1].split('.')[1] if not isinstance(self.__resume, io.BytesIO) else self.__resume.name.split('.')[1]
        self.__text_raw = utils.extract_text(self.__resume, '.' + ext)
        self.__text = ' '.join(self.__text_raw.split())
        self.__doc = self.__nlp(self.__text)
        self.__custom_doc = self.__custom_nlp(self.__text_raw)
        self.__noun_chunks = list(self.__doc.noun_chunks)

        self.__get_basic_details()

    def get_extracted_data(self):
        return self.__details

    def __get_basic_details(self):
        entities_custom = utils.extract_entities_wih_custom_model(self.__custom_doc)
        entities_raw = utils.extract_entity_sections_grad(self.__text_raw)

        name = self.__extract_name(entities_custom)
        self.__details['name'] = name

        self.__details['email'] = utils.extract_email(self.__text)
        self.__details['mobile_number'] = utils.extract_mobile_number(self.__text, self.__custom_regex)
        self.__details['skills'] = utils.extract_skills(self.__doc, self.__noun_chunks, self.__skills_file)
        self.__details['college_name'] = entities_raw.get('College Name', None)
        self.__details['degree'] = entities_custom.get('Degree', None)
        self.__details['designation'] = entities_custom.get('Designation', None)
        self.__details['company_names'] = entities_custom.get('Companies worked at', None)
        self.__details['experience'] = entities_raw.get('experience', None)

        try:
            exp = round(utils.get_total_experience(entities_raw['experience']) / 12, 2)
            self.__details['total_experience'] = exp
        except Exception:
            self.__details['total_experience'] = 0

        self.__details['no_of_pages'] = utils.get_number_of_pages(self.__resume)

        self.__details['projects'] = self.__extract_section(["project", "implemented", "developed", "designed", "created", "built", "engineered"])
        self.__details['internships'] = self.__extract_section(["internship", "interned", "trainee"])
        self.__details['achievements'] = self.__extract_section(["achievement", "awarded", "honor", "prize", "recognized"])
        self.__details['hobbies'] = self.__extract_section(["hobbies", "interests", "reading", "traveling", "sports"], limit_by_heading="hobbies")
        self.__details['interests'] = self.__extract_section(["interests", "passion", "keen on", "enthusiastic about"], limit_by_heading="interests")
        self.__details['objective'] = self.__extract_section(["objective", "career goal", "aim"], limit_by_heading="objective")
        self.__details['education'] = self.__extract_section(["education", "academic background", "qualifications"], limit_by_heading="education")
        self.__details['summary'] = self.__extract_section(["summary", "profile summary", "about me"], limit_by_heading="summary")

    def __extract_name(self, custom_entities):
        try:
            return custom_entities['Name'][0]
        except (KeyError, IndexError):
            pass

        for ent in self.__doc.ents:
            if ent.label_ == "PERSON" and len(ent.text.split()) <= 3:
                return ent.text

        name_match = re.search(r"(?:name\s*[:\-]?\s*)([A-Z][a-z]+\s[A-Z][a-z]+)", self.__text, re.IGNORECASE)
        if name_match:
            return name_match.group(1)

        return None

    def __extract_section(self, keywords, limit_by_heading=None):
        lines = self.__text_raw.split('\n')
        section = []
        start_capture = False
        heading_pattern = re.compile(rf'^\s*{limit_by_heading}\s*[:\-]?\s*$', re.IGNORECASE) if limit_by_heading else None

        for i, line in enumerate(lines):
            if heading_pattern and heading_pattern.match(line):
                start_capture = True
                continue

            if any(k.lower() in line.lower() for k in keywords) or start_capture:
                clean_line = line.strip()
                if 20 < len(clean_line) < 500:
                    section.append(clean_line)
                    start_capture = True
                elif start_capture and clean_line == "":
                    break

        return list(set(section)) if section else None


def resume_result_wrapper(resume):
    parser = ResumeParser(resume)
    return parser.get_extracted_data()


if __name__ == '__main__':
    pool = mp.Pool(mp.cpu_count())
    resumes = []
    for root, _, filenames in os.walk('resumes'):
        for filename in filenames:
            resumes.append(os.path.join(root, filename))
    results = pool.map(resume_result_wrapper, resumes)
    pprint.pprint(results)
