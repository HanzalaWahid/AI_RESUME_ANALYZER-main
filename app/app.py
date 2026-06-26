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

from app.Courses import courses, interview_videos, resume_videos
from app.config import get_geocoder_user_agent
from app.data_access import AnalysisRecord, create_tables, get_connection, insert_analysis_record, insert_feedback_record
from app.file_services import save_uploaded_resume
from app.services.analysis_service import ResumeAnalysisService
from app.ui_helpers import get_csv_download_link, show_logo

nltk.download('stopwords')
nlp = spacy.load('en_core_web_sm')

# Initialize analyzer in run() reactively

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
    
    st.sidebar.markdown("### Settings")
    provider_labels = {
        "Custom Rule-based Extractor": "custom_rule",
        "Gemini LLM Extractor": "gemini",
        "Ollama Local Extractor": "ollama",
        "Pyresparser (Legacy)": "pyresparser"
    }
    selected_label = st.sidebar.selectbox("Extraction Provider", list(provider_labels.keys()), index=0)
    selected_provider = provider_labels[selected_label]
    
    # Reactive analyzer service instantiation
    analysis_service = ResumeAnalysisService(provider=selected_provider)
    
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
        pdf_file = st.file_uploader("Choose your resume", type=["pdf", "docx"])
        if pdf_file is not None:
            with st.spinner ('Hang on While We Cook magic for you...'):
                time.sleep(1)
                
                save_image_path = save_uploaded_resume(pdf_file)
                pdf_name = save_image_path.name
                
                # File Validation Layer
                is_valid, validation_errors = analysis_service.validate_file(save_image_path)
                if not is_valid:
                    st.error("❌ File Validation Failed! Please resolve the following errors:")
                    for err in validation_errors:
                        st.write(f"- {err}")
                    return

                # Preview file if PDF
                if save_image_path.suffix.lower() == '.pdf':
                    show_pdf(str(save_image_path))
                else:
                    st.info("ℹ️ DOCX file uploaded. Document preview is only supported for PDF files, but analysis is available below.")

                # Analysis Orchestrator
                try:
                    analysis_result = analysis_service.analyze_resume(save_image_path)
                except Exception as e:
                    st.error(f"Analysis failed: {e}")
                    return
                
                resume_data = analysis_result.resume_data.__dict__
                
                st.header("Resume Analysis")
                st.success("Hello " + str(resume_data.get('name') or "Candidate"))
                
                # Basic Info
                st.subheader("** Your Basic Info **")
                st.text('Name: ' + str(resume_data.get('name', 'Not found')))
                st.text('Email: ' + str(resume_data.get('email', 'Not found')))
                st.text('Contact: ' + str(resume_data.get('mobile_number', 'Not found')))
                st.text('Degree: ' + str(resume_data.get('degree', 'Not found')))
                st.text('Resume pages: ' + str(resume_data.get('no_of_pages', 'N/A')))

                # Candidate Level Display
                cand_level = analysis_result.candidate_level
                if cand_level == "Intermediate":
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif cand_level == "Experienced":
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at Fresher level!!</h4>''',unsafe_allow_html=True)

                # Skill and field recommendations
                st.subheader("** Skills recommendation 💡**")
                
                predicted_field = analysis_result.recommendation.predicted_field
                recommended_skills = analysis_result.recommendation.recommended_skills
                rec_course_names = []
                reco_field = "NA"

                if predicted_field:
                    reco_field = predicted_field
                    st.success(f"** Our analysis says you are looking for {predicted_field} Jobs. **")
                    
                    st_tags(label='** Your Current Skills **', text='Skills detected', value=resume_data.get('skills', []), key='current_skills_tags')
                    st_tags(label='### Recommended skills for you.', text='Skills to add to boost success', value=recommended_skills, key='rec_skills_tags')
                    st.markdown('''<h5 style='text-align: left; color: #1ed760;'>Adding these skills to your resume will boost🚀 your chances of getting a Job💼</h5>''',unsafe_allow_html=True)
                    
                    rec_course_names = course_recommender(analysis_result.recommendation.recommended_courses)
                else:
                    st.warning("** Currently our tool only predicts and recommends for Data Science, Web, Android, iOS and UI/UX Development**")
                    st_tags(label='### Recommended skills for you.', text='Currently No Recommendations', value=['No Recommendations'], key='no_rec_tags')
                    st.markdown('''<h5 style='text-align: left; color: #092851;'>Maybe Available in Future Updates</h5>''',unsafe_allow_html=True)
                    rec_course_names = ["Sorry! Not Available for this Field"]

                # Render ATS Sub-scores breakdown
                st.subheader("** ATS Score Breakdown 📈 **")
                sub_scores = analysis_result.ats_result.sub_scores
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown("#### Category Metrics")
                    for score_name, val in sub_scores.items():
                        max_val = 20 if score_name in ["experience", "projects", "skills"] else 10 if score_name in ["contact", "keyword_match"] else 15 if score_name == "education" else 5
                        st.markdown(f"**{score_name.replace('_', ' ').title()}**: {val} / {max_val}")
                        st.progress(min(1.0, float(val) / max_val))
                
                with col2:
                    labels = [name.replace('_', ' ').title() for name in sub_scores.keys()]
                    values = list(sub_scores.values())
                    fig = px.pie(
                        names=labels,
                        values=values,
                        title="Sub-score Distribution",
                        color_discrete_sequence=px.colors.sequential.Aggrnyl
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Render overall score and detailed explanations
                st.subheader("** Resume Score **")
                overall_score = analysis_result.ats_result.score
                st.subheader("** Resume Tips & Ideas 🥂 **")
                
                for exp in analysis_result.ats_result.detailed_explanations:
                    if exp.startswith("Missing") or exp.startswith("No ") or "lacks" in exp.lower() or "minimal" in exp.lower() or "can be improved" in exp.lower():
                        st.markdown(f"❌ <span style='color:#d73b5c'>{exp}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"✅ <span style='color:#1ed760'>{exp}</span>", unsafe_allow_html=True)

                # Custom progress bar color styling
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
                for percent_complete in range(overall_score):
                    score += 1
                    time.sleep(0.01)
                    my_bar.progress(percent_complete + 1)

                st.success('** Your Resume Writing Score: ' + str(score) + ' / 100 **')
                st.warning("** Note: This score is calculated based on the content that you have in your Resume. **")

                # Insert records
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = (cur_date + '_' + cur_time)

                insert_analysis_record(AnalysisRecord(
                    sec_token=str(sec_token), ip_add=str(ip_add), host_name=host_name, dev_user=dev_user,
                    os_name_ver=os_name_var, latlong=str(latlong), city=city, state=state, country=country,
                    act_name=act_name, act_mail=act_mail, act_mob=act_mob,
                    name=resume_data.get('name', 'Unknown'), email=resume_data.get('email', 'Unknown'),
                    res_score=str(overall_score), timestamp=timestamp, no_of_pages=str(resume_data.get('no_of_pages', 0)),
                    reco_field=reco_field, cand_level=cand_level, skills=str(resume_data.get('skills', [])),
                    recommended_skills=str(recommended_skills), courses=str(rec_course_names), pdf_name=pdf_name,
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