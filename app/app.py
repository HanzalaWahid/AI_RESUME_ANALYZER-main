import base64
import datetime
import io
import os
import platform
import random
import secrets
import socket
import time

import geocoder
import nltk
import pandas as pd
import plotly.express as px
import spacy
import streamlit as st
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.geocoders import Nominatim
from pdfminer3.converter import TextConverter
from pdfminer3.layout import LAParams
from pdfminer3.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer3.pdfpage import PDFPage
from PIL import Image
from streamlit_tags import st_tags

from Courses import courses, interview_videos, resume_videos
from config import get_field_rules, get_geocoder_user_agent
from data_access import AnalysisRecord, create_tables, get_connection, insert_analysis_record, insert_feedback_record
from services import analyze_resume_file, save_uploaded_resume
from ui_helpers import get_csv_download_link, show_logo

nltk.download('stopwords')
nlp = spacy.load('en_core_web_sm')



def analyze_resume(resume_path):
    extracted_data = analyze_resume_file(resume_path)
    text = ' '.join([str(v) for v in extracted_data.values() if v])

    field_rules = get_field_rules()
    detected_field_key = None
    text_lower = text.lower()
    for key, keywords in field_rules.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_field_key = key
            break

    
    suggested = courses.get(detected_field_key, [])

    return extracted_data, suggested

def extract_name(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return "Not Found"
def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager , fake_file_handle , laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager,converter)
    with open (file ,'rb') as fh:
        for page in PDFPage.get_pages(fh,caching=True,check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text =  fake_file_handle.getvalue()

    converter.close()
    fake_file_handle.close()
    return text 
def  show_pdf(file_path):
    with open (file_path , "rb") as f:
        base64_pdf= base64.b64encode(f.read()).decode('utf-8') 
    pdf_display  = F'<iframe src ="data:application/pdf;base64,{base64_pdf} #toolbar=1&zoom=100" width="700" height="1000" type= "application/pdf"></iframe> '
    st.markdown(pdf_display, unsafe_allow_html=True)
def course_recommender(course_list):
    st.subheader("**Course & Certification Recommendation 👨‍🎓**")
    c = 0
    rec_course = []
    no_of_reco = st.slider('Choose number of Course Recommendation: 1 ,5 ,10',min_value=1, max_value=10, value=5)
    random.shuffle(course_list)
    for c_name , c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}][{c_link}]" )
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course

def insertf_data(feed_name, feed_email, feed_score, comments, Timestamp):
    insert_feedback_record(feed_name, feed_email, feed_score, comments, Timestamp)



st.set_page_config(
    page_title = "AI Resume Analyzer",
    page_icon = "",
)
def run():
    show_logo()
    st.sidebar.markdown(" # Choose Something... ")
    activites = ["User","Feedback","About","Admin"]
    choice = st.sidebar.selectbox("Choose among the given options: ", activites)
    link = '<b>Built with  🤍 by  <a href="" style="text-decoration: none: color: #021659;">Snakes & Co </a></b>'
    st.sidebar.markdown(link, unsafe_allow_html=True)
    st.markdown('''
<div id="sfct2xghr8ak6lfqt3kgru233378jya38dy" hidden></div>

<noscript>
    <a href="https://www.freecounterstat.com" title="hit counter">
        <img src="https://counter9.stat.ovh/private/freecounterstat.php?c=t2xghr8ak6lfqt3kgru233378jya38dy" border="0" title="hit counter" alt="hit counter">
    </a>
</noscript>
''', unsafe_allow_html=True)

    connection = get_connection()
    cursor = connection.cursor()
    try:
        create_tables(cursor)
    finally:
        connection.close()

 
    if choice == 'User':
        act_name = st.text_input('NAME*')
        act_mail = st.text_input('Email*')
        act_mob = st.text_input('Mobile Number*')
        sec_token = secrets.token_urlsafe(12)
        host_name = socket.gethostname()
        ip_add = socket.gethostbyname(host_name)
        dev_user = os.getlogin()
        os_name_var = platform.system() + " " + platform.release()
        g = geocoder.ip('me', timeout=2)
        latlong = None
        try:
            latlong = g.latlng
        except Exception:
            latlong = None
        city = state = country = "Unavailable"

        if latlong and latlong != [0.0, 0.0]:
            try:
                geo_locator = Nominatim(user_agent=get_geocoder_user_agent())
                location = geo_locator.reverse(latlong, language='en', timeout=10)
                address = location.raw.get('address', {})
                city = address.get('city') or address.get('town') or address.get('municipality') or ''
                state = address.get('state') or address.get('region') or address.get('state_district') or ''
                country = address.get('country', '')

            except Exception as e:
                st.warning(f"Geolocation failed: {e}")
        else:
            st.warning("Could not detect your location.")

        st.markdown('''<h5 style="text-align: left; color: #021659;">Upload Your Resume, And Get Smart Recommendation</h5>''', unsafe_allow_html=True)
        pdf_file = st.file_uploader("Choose your resume " , type = ["pdf"])
        if pdf_file is  not None:
            with st.spinner ('Hang on While We Cook magic for you...'):
                time.sleep(4)
                
                save_image_path = save_uploaded_resume(pdf_file)
                pdf_name = save_image_path.name
                show_pdf(str(save_image_path))

                resume_data = analyze_resume_file(save_image_path)
                if resume_data:
                    resume_text = pdf_reader(save_image_path)
                    st.header("Resume Analysis")
                    st.success("Hello" + resume_data['name'])
                    st.subheader("** Your Basic Info ")
                   
                    st.text('Name: ' + str(resume_data.get('name', 'Not found')))
                    st.text('Email: ' + str(resume_data.get('email', 'Not found')))
                    st.text('Contact: ' + str(resume_data.get('mobile_number', 'Not found')))
                    st.text('Degree: ' + str(resume_data.get('degree', 'Not found')))
                    st.text('Resume pages: ' + str(resume_data.get('no_of_pages', 'N/A')))

                    cand_level = ''
                    if resume_data['no_of_pages'] < 1:
                        cand_level = "NA"
                        st.markdown(''' <h4 style= 'text_algin: lrft; color: #d73b5c; > You are at Fresher Level! </h4> ''' , unsafe_allow_html=True)
                    elif 'INTERNSHIP' in resume_text:
                        cand_level = "Intermediate"
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                    elif 'INTERNSHIPS' in resume_text:
                        cand_level = "Intermediate"
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                    elif 'Internship' in resume_text:
                        cand_level = "Intermediate"
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                    elif 'Internships' in resume_text:
                        cand_level = "Intermediate"
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                    
                    
                    elif 'EXPERIENCE' in resume_text:
                        cand_level = "Experienced"
                        st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                    elif 'WORK EXPERIENCE' in resume_text:
                        cand_level = "Experienced"
                        st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                    elif 'Experience' in resume_text:
                        cand_level = "Experienced"
                        st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                    elif 'Work Experience' in resume_text:
                        cand_level = "Experienced"
                        st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                    else:
                        cand_level = "Fresher"
                        st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at Fresher level!!''',unsafe_allow_html=True)


                    st.subheader("** Skills recommendation 💡** ")

                    keywords= st_tags(label= '** Your Current Skills **', text = 'See our skills recommendation below', value = resume_data['skills'] , key = '1')
                    ds_keyword = ['tensorflow','keras','pytorch','machine learning','deep Learning','flask','streamlit']
                    web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress','javascript', 'angular js', 'C#', 'Asp.net', 'flask']
                    android_keyword = ['android','android development','flutter','kotlin','xml','kivy']
                    ios_keyword = ['ios','ios development','swift','cocoa','cocoa touch','xcode']
                    uiux_keyword = ['ux','adobe xd','figma','zeplin','balsamiq','ui','prototyping','wireframes','storyframes','adobe photoshop','photoshop','editing','adobe illustrator','illustrator','adobe after effects','after effects','adobe premier pro','premier pro','adobe indesign','indesign','wireframe','solid','grasp','user research','user experience']
                    finance_keyword = ['finance', 'financial analysis', 'budgeting', 'accounting', 'valuation','financial modeling', 'corporate finance', 'investment', 'balance sheet','income statement', 'cash flow', 'audit', 'ledger', 'taxation', 'fintech','bookkeeping', 'equity', 'debt', 'roi', 'capital']
                    marketing_keyword = ['marketing', 'digital marketing', 'seo', 'sem', 'social media', 'branding', 'content creation', 'email marketing', 'ppc', 'adwords', 'google analytics', 'facebook ads', 'market research', 'copywriting', 'campaigns', 'conversion rate', 'influencer marketing', 'growth hacking']
                    project_management_keyword = ['project management', 'agile', 'scrum', 'kanban', 'jira', 'confluence', 'pmp', 'sprint', 'gantt chart', 'milestones', 'resource allocation', 'risk management', 'timeline', 'stakeholder', 'scrum master', 'project planning', 'scope', 'deliverables', 'waterfall', 'trello']
                    human_resources_keyword = ['human resources', 'recruitment', 'onboarding', 'employee relations', 'hiring', 'talent acquisition', 'hr management', 'people management', 'training and development', 'compensation', 'benefits', 'performance review', 'organizational behavior', 'hr policies', 'strategic hr', 'conflict resolution', 'job evaluation', 'diversity and inclusion', 'labor law']
                    n_any = ['english','communication','writing', 'microsoft office', 'leadership','customer management', 'social media']
                    recommended_skills = []
                    reco_field = ''
                    rec_course = ''

                    for i in resume_data['skills']:
                        if i.lower() in ds_keyword:
                            print(i.lower())
                            reco_field = 'Data Science'
                            st.success("**  Our analysis says you are looking for Data Science Jobs.**")
                            recommended_skills = ['Data Visualization','Predictive Analysis','Statistical Modeling','Data Mining','Clustering & Classification','Data Analytics','Quantitative Analysis','Web Scraping','ML Algorithms','Keras','Pytorch','Probability','Scikit-learn','Tensorflow',"Flask",'Streamlit']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text = 'Recommened skills generated from system' , value= recommended_skills , key = '2')
                            st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job</h5>''',unsafe_allow_html=True)
                            rec_course = course_recommender(courses["data_science"])
                            break
                        elif i.lower() in web_keyword:
                            print(i.lower())
                            reco_field = 'Web development'
                            st.success("** Our Analysis says you are looking for Web development Jobs **")
                            recommended_skills = ['React','Django','Node JS','React JS','php','laravel','Magento','wordpress','Javascript','Angular JS','c#','Flask','SDK']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',text = 'Recommended skills generated from from system' , value = recommended_skills, key = '3')
                            st.markdown(''' <h5 style ='text-align: left ; color: #1ed760 ; > Adding this skills to resume will boost 🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                            rec_course = course_recommender(courses["web_development"])
                            break
                        elif i.lower() in android_keyword:
                            print(i.lower())
                            reco_field = ' Android Development '
                            st.success("**Our Analysis say you are looking for Android development Jobs **")
                            recommended_skills = ['Android','Android development','Flutter','Kotlin','XML','Java','Kivy','GIT','SDK','SQLite']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Recommended skills generated from System',value=recommended_skills,key = '4')
                            st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                            rec_course = course_recommender(courses["android_development"])
                            break 

                        elif i.lower() in ios_keyword:
                            print(i.lower())
                            reco_field = 'IOS Development'
                            st.success('** Our analysis says you are looking for IOS App Development Jobs **')
                            recommended_skills =  ['IOS','IOS Development','Swift','Cocoa','Cocoa Touch','Xcode','Objective-C','SQLite','Plist','StoreKit',"UI-Kit",'AV Foundation','Auto-Layout']
                            recommended_keywords = st_tags(label = '### Recommended Skills for You.',
                            text = 'Recommended Skills generated from system ',value=recommended_skills,key='5')
                            st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                            rec_course = course_recommender(courses["ios_development"])
                            break
                        elif i.lower() in uiux_keyword:
                            print(i.lower())
                            reco_field = 'UI-UX Development'
                            st.success("** Our analysis says you are looking for UI-UX Development Jobs **")
                            recommended_skills = ['UI','User Experience','Adobe XD','Figma','Zeplin','Balsamiq','Prototyping','Wireframes','Storyframes','Adobe Photoshop','Editing','Illustrator','After Effects','Premier Pro','Indesign','Wireframe','Solid','Grasp','User Research']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Recommended skills generated from System',value=recommended_skills,key = '6')
                            st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                            rec_course = course_recommender(courses["uiux_design"])
                            break
                        elif i.lower() in finance_keyword:
                            print(i.lower())
                            reco_field = 'Finance'
                            st.success("** Our analysis says you are looking for Finance Jobs **")
                            recommended_skills = ['Financial Analysis', 'Accounting', 'Budgeting', 'Valuation', 'Corporate Finance', 'Taxation', 'Investment', 'Financial Modeling', 'Ledger Management', 'Cash Flow']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                        text='Recommended skills generated from system',
                                                        value=recommended_skills, key='7')
                            st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to resume will boost🚀 the chances of getting a Job💼</h5>''',
                                        unsafe_allow_html=True)
                            rec_course = course_recommender(courses["finance"])
                            break
                        elif i.lower() in marketing_keyword:
                            print(i.lower())
                            reco_field = 'Marketing'
                            st.success("** Our analysis says you are looking for Marketing Jobs **")
                            recommended_skills = ['Digital Marketing', 'SEO', 'SEM', 'Social Media', 'Google Ads', 'Email Marketing', 'Brand Strategy', 'Analytics', 'Content Creation', 'PPC']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                        text='Recommended skills generated from system',
                                                        value=recommended_skills, key='8')
                            st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to resume will boost🚀 the chances of getting a Job💼</h5>''',
                                        unsafe_allow_html=True)
                            rec_course = course_recommender(courses["marketing"])
                            break
                        elif i.lower() in project_management_keyword:
                            print(i.lower())
                            reco_field = 'Project Management'
                            st.success("** Our analysis says you are looking for Project Management Jobs **")
                            recommended_skills = ['Agile', 'Scrum', 'Kanban', 'PMP', 'JIRA', 'Project Planning', 'Risk Management', 'Team Coordination', 'Stakeholder Communication', 'Timeline Management']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                        text='Recommended skills generated from system',
                                                        value=recommended_skills, key='9')
                            st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to resume will boost🚀 the chances of getting a Job💼</h5>''',
                                        unsafe_allow_html=True)
                            rec_course = course_recommender(courses["project_management"])
                            break
                        elif i.lower() in human_resources_keyword:
                            print(i.lower())
                            reco_field = 'Human Resources'
                            st.success("** Our analysis says you are looking for HR Jobs **")
                            recommended_skills = ['Recruitment', 'Talent Acquisition', 'People Management', 'Onboarding', 'Employee Relations', 'Training & Development', 'HR Policies', 'Compensation', 'Labor Law', 'Performance Review']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                        text='Recommended skills generated from system',
                                                        value=recommended_skills, key='10')
                            st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to resume will boost🚀 the chances of getting a Job💼</h5>''',
                                        unsafe_allow_html=True)
                            rec_course = course_recommender(courses["human_resources"])
                            break


                        elif i.lower() in n_any:
                            print(i.lower())
                            reco_field = 'NA'
                            st.warning("** Currently our tool only predicts and recommends for Data Science, Web, Android, IOS and UI/UX Development**")
                            recommended_skills = ['No Recommendations']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Currently No Recommendations',value=recommended_skills,key = '6')
                            st.markdown('''<h5 style='text-align: left; color: #092851;'>Maybe Available in Future Updates</h5>''',unsafe_allow_html=True)
                            rec_course = "Sorry! Not Available for this Field"
                            break


                    st.subheader("**Resume Tips & Ideas 🥂**")
                    resume_score = 0

                    if 'Objective' or 'Summary' in resume_text:
                        resume_score = resume_score+6
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Objective/Summary</h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add your career objective, it will give your career intension to the Recruiters.</h4>''',unsafe_allow_html=True)

                    if 'Education' or 'School' or 'College' in resume_text:
                        resume_score = resume_score +12
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Education Details</h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Education. It will give Your Qualification level to the recruiter</h4>''',unsafe_allow_html=True)

                    if 'Experience' in resume_text:
                        resume_score = resume_score + 16
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Experience</h4>''',unsafe_allow_html=True)
                    elif 'Experience' in resume_text:
                        resume_score = resume_score + 16
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Experience</h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Experience. It will help you to stand out from crowd</h4>''',unsafe_allow_html=True)

                    if 'INTERNSHIPS'  in resume_text:
                        resume_score = resume_score + 6
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                    elif 'INTERNSHIP'  in resume_text:
                        resume_score = resume_score + 6
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                    elif 'Internships'  in resume_text:
                        resume_score = resume_score + 6
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                    elif 'Internship'  in resume_text:
                        resume_score = resume_score + 6
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Internships</h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Internships. It will help you to stand out from crowd</h4>''',unsafe_allow_html=True)

                    if 'SKILLS'  in resume_text:
                        resume_score = resume_score + 7
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                    elif 'SKILL'  in resume_text:
                        resume_score = resume_score + 7
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                    elif 'Skills'  in resume_text:
                        resume_score = resume_score + 7
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                    elif 'Skill'  in resume_text:
                        resume_score = resume_score + 7
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added Skills</h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Skills. It will help you a lot</h4>''',unsafe_allow_html=True)

                    if 'HOBBIES' in resume_text:
                        resume_score = resume_score + 4
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies</h4>''',unsafe_allow_html=True)
                    elif 'Hobbies' in resume_text:
                        resume_score = resume_score + 4
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Hobbies</h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Hobbies. It will show your personality to the Recruiters and give the assurance that you are fit for this role or not.</h4>''',unsafe_allow_html=True)

                    if 'INTERESTS'in resume_text:
                        resume_score = resume_score + 5
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Interest</h4>''',unsafe_allow_html=True)
                    elif 'Interests'in resume_text:
                        resume_score = resume_score + 5
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Interest</h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Interest. It will show your interest other that job.</h4>''',unsafe_allow_html=True)

                    if 'ACHIEVEMENTS' in resume_text:
                        resume_score = resume_score + 13
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements </h4>''',unsafe_allow_html=True)
                    elif 'Achievements' in resume_text:
                        resume_score = resume_score + 13
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements </h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Achievements. It will show that you are capable for the required position.</h4>''',unsafe_allow_html=True)

                    if 'CERTIFICATIONS' in resume_text:
                        resume_score = resume_score + 12
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                    elif 'Certifications' in resume_text:
                        resume_score = resume_score + 12
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                    elif 'Certification' in resume_text:
                        resume_score = resume_score + 12
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Certifications </h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Certifications. It will show that you have done some specialization for the required position.</h4>''',unsafe_allow_html=True)

                    if 'PROJECTS' in resume_text:
                        resume_score = resume_score + 19
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                    elif 'PROJECT' in resume_text:
                        resume_score = resume_score + 19
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                    elif 'Projects' in resume_text:
                        resume_score = resume_score + 19
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                    elif 'Project' in resume_text:
                        resume_score = resume_score + 19
                        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h4>''',unsafe_allow_html=True)
                    else:
                        st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Projects. It will show that you have done work related the required position or not.</h4>''',unsafe_allow_html=True)

                    st.subheader("** Resume Score **")
                    st.markdown(
                        """
                    <style> 
                    .stProgress > div > div > div > div{
                        background-color : #d73b5c;

                    }
                    </style>""" ,  unsafe_allow_html = True 
    )
                    my_bar = st.progress(0)
                    score = 0
                    for percent_complete in range(resume_score):
                        score += 1
                        time.sleep(0.1)
                        my_bar.progress(percent_complete + 1)

                    st.success('** Your Resume Writing Score  **' + str(score) + '**')
                    st.warning("** Note: This score is calculated based on the content that you have in your Resume. **")

    

                    ts = time.time()
                    cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                    cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                    timestamp = (cur_date + '_' + cur_time)

                    insert_analysis_record(AnalysisRecord(
                        sec_token=str(sec_token), ip_add=str(ip_add), host_name=host_name, dev_user=dev_user,
                        os_name_ver=os_name_var, latlong=str(latlong), city=city, state=state, country=country,
                        act_name=act_name, act_mail=act_mail, act_mob=act_mob,
                        name=resume_data.get('name', 'Unknown'), email=resume_data.get('email', 'Unknown'),
                        res_score=str(resume_score), timestamp=timestamp, no_of_pages=str(resume_data.get('no_of_pages', 0)),
                        reco_field=reco_field, cand_level=cand_level, skills=str(resume_data.get('skills', [])),
                        recommended_skills=str(recommended_skills), courses=str(rec_course), pdf_name=pdf_name,
                    ))

                    st.header("** Bonus Video for Resume Writing Tips 💡 **")
                    resume_vid = random.choice(resume_videos)
                    st.video(resume_vid)

                    st.header("**Bonus Video for Interview Tips💡**")
                    interview_vid = random.choice(interview_videos)
                    st.video(interview_vid)
                    
                    st.balloons()
                else:
                    st.error('Something went wrong ')


    elif choice == 'Feedback':
            ts = time.time()
            cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
            cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
            timestamp = str(cur_date+'_'+cur_time)

            with st.form("my_form"):
                st.write("Feedback Form")
                feed_name = st.text_input('Name')
                feed_email = st.text_input('Email')
                feed_score = st.slider('Rate us from 1 to 5' ,1,5)
                comments = st.text_input('Comments')
                Timestamp = timestamp
                submitted = st.form_submit_button('Submit')
                if submitted:
                    insertf_data(feed_name,feed_email,feed_score,comments,Timestamp)
                    st.success("Thanks! Your Feedback was Recorded")
                    st.balloons()

            connection = get_connection()
            query = ' select * from user_feedback'
            plotfeed_data =  pd.read_sql(query,connection)
            

            labels = plotfeed_data.feed_score.unique()
            values = plotfeed_data.feed_score.value_counts()

            st.subheader("**  Past User Rating's **")
            fig = px.pie(values = values , names = labels , title ="Chart of User Rating Score 1 to 5 ", color_discrete_sequence=px.colors.sequential.Aggrnyl )
            st.plotly_chart(fig)

            cursor.execute('select feed_name , comments from user_feedback')
            plfeed_cmt_data = cursor.fetchall()

            st.subheader("** User Comments's **")
            dff = pd.DataFrame(plfeed_cmt_data, columns=['User','Comments'])
            st.dataframe(dff , width = 1000)

    elif choice == 'About':
            st.subheader("**About The Tool - AI RESUME ANALYZER**")
            st.markdown('''
    <p align='justify'>
    A group project built to parse information from resumes using natural language processing, identify key skills, classify them into relevant industry sectors, and provide personalized recommendations and analytics based on keyword analysis.
</p>

<p align="justify">
    <b>How to use it:</b><br/><br/>
    <b>User -</b> Select the "User" option from the sidebar, fill in the required fields, and upload your resume in PDF format. The tool will automatically process and analyze the resume.<br/><br/>
    <b>Feedback -</b> A section for users to submit suggestions and feedback to help improve the tool.<br/><br/>
    <b>Admin -</b> Use <b>admin</b> as the username and <b>admin@resume-analyzer</b> as the password to access the admin panel and view analysis results.
</p><br/><br/>

<p align="justify">
    Developed with 🤍 as part of a collaborative academic project focused on applying data science and NLP techniques to real-world problems.
</p>

                        ''' , unsafe_allow_html = True)
            
    else:
            st.success('Welcome to Admin Side')

            ad_user = st.text_input("Username")
            ad_passwords = st.text_input("Password", type='password')

            if st.button('Login'):
                if ad_user == 'admin' and ad_passwords == 'admin@resume-analyzer':
                    connection = get_connection()
                    cursor = connection.cursor()
                    cursor.execute('''SELECT ID, ip_add, resume_score, convert(Predicted_Field using utf8), convert(User_level using utf8), city, state, country from user_data
''')
                    datanalys = cursor.fetchall()
                    plot_data =  pd.DataFrame(datanalys, columns=['Idt', 'IP_add', 'resume_score', 'Predicted_Field', 'User_Level', 'City', 'State', 'Country'])

                    values = plot_data.Idt.count()
                    st.success("Welcome Hanzala ! Total %d " % values + "User's have used our Tool : )")

                    cursor.execute(''' SELECT ID , sec_token , ip_add , act_name ,act_mob , convert(Predicted_Field using utf8mb4), Timestamp , Name , Email_ID , resume_score , Page_no , pdf_name, convert(User_level using utf8), convert(Actual_skills using utf8), convert(Recommended_skills using utf8), convert(Recommended_courses using utf8), city, state, country, latlong, os_name_ver, host_name, dev_user from user_data
''')
                    data = cursor.fetchall()

                    st.header("** User's Data **")
                    df = pd.DataFrame(data , columns=['ID', 'Token', 'IP Address', 'Name', 'Mobile Number', 'Predicted Field', 'Timestamp',
                                                 'Predicted Name', 'Predicted Mail', 'Resume Score', 'Total Page',  'File Name',   
                                                 'User Level', 'Actual Skills', 'Recommended Skills', 'Recommended Course',
                                                 'City', 'State', 'Country', 'Lat Long', 'Server OS', 'Server Name', 'Server User',])
                    st.dataframe(df)
                    st.markdown(get_csv_download_link(df,'User_Data.csv','Download Report'), unsafe_allow_html = True)

                    cursor.execute(''' SELECT * from user_feedback''')
                    data = cursor.fetchall()

                    st.header("** User's feedback Data **")
                    df = pd.DataFrame(data,columns =['ID', 'Name','Email','feed_score','Comments','Timestamp'])
                    st.dataframe(df)

                    query = 'select * from user_feedback'
                    plotfeed_data = pd.read_sql(query,connection)
                    st.write("Plotfeed Data Columns:", plotfeed_data.columns.tolist())
                    print("Plotfeed Data Columns:", plotfeed_data.columns.tolist())

                    labels = plotfeed_data['feed_score'].unique()
                    values = plotfeed_data['feed_score'].value_counts()

                    st.subheader("**User Rating's**")
                    fig = px.pie(values = values , names= labels , title="Chart of User Rating Score From 1 - 5 🤗", color_discrete_sequence=px.colors.sequential.Aggrnyl)
                    st.plotly_chart(fig)

                    labels = plot_data.Predicted_Field.unique()
                    values = plot_data.Predicted_Field.value_counts()

                    st.subheader("**Pie-Chart for Predicted Field Recommendation**")
                    fig = px.pie(df, values=values, names=labels, title='Predicted Field according to the Skills 👽', color_discrete_sequence=px.colors.sequential.Aggrnyl_r)
                    st.plotly_chart(fig)

                    labels = plot_data.User_Level.unique()
                    values = plot_data.User_Level.value_counts()

                    st.subheader("**Pie-Chart for User's Experienced Level**")
                    fig = px.pie(df, values=values, names=labels, title="Pie-Chart 📈 for User's 👨‍💻 Experienced Level", color_discrete_sequence=px.colors.sequential.RdBu)
                    st.plotly_chart(fig)

                    labels = plot_data.resume_score.unique()                
                    values = plot_data.resume_score.value_counts()

                    st.subheader("**Pie-Chart for Resume Score**")
                    fig = px.pie(df, values=values, names=labels, title='From 1 to 100 💯', color_discrete_sequence=px.colors.sequential.Agsunset)
                    st.plotly_chart(fig)

                    labels = plot_data.IP_add.unique()
                    values = plot_data.IP_add.value_counts()

                    st.subheader("**Pie-Chart for Users App Used Count**")
                    fig = px.pie(df, values=values, names=labels, title='Usage Based On IP Address 👥', color_discrete_sequence=px.colors.sequential.matter_r)
                    st.plotly_chart(fig)

                    labels = plot_data.City.unique()
                    values = plot_data.City.value_counts()

                    st.subheader("**Pie-Chart for City**")
                    fig = px.pie(df, values=values, names=labels, title='Usage Based On City 🌆', color_discrete_sequence=px.colors.sequential.Jet)
                    st.plotly_chart(fig)

                    labels = plot_data.State.unique()
                    values = plot_data.State.value_counts()

                    st.subheader("**Pie-Chart for State**")
                    fig = px.pie(df, values=values, names=labels, title='Usage Based on State 🚉', color_discrete_sequence=px.colors.sequential.PuBu_r)
                    st.plotly_chart(fig)

                    labels = plot_data.Country.unique()
                    values = plot_data.Country.value_counts()

                    st.subheader("**Pie-Chart for Country**")
                    fig = px.pie(df, values=values, names=labels, title='Usage Based on Country 🌏', color_discrete_sequence=px.colors.sequential.Purpor_r)
                    st.plotly_chart(fig)

                else:
                    st.error("Wrong ID & Password Provided")

run()