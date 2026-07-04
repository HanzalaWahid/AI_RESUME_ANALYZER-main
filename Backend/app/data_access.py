import os
from dataclasses import dataclass

import pymysql


@dataclass
class AnalysisRecord:
    sec_token: str
    ip_add: str
    host_name: str
    dev_user: str
    os_name_ver: str
    latlong: str
    city: str
    state: str
    country: str
    act_name: str
    act_mail: str
    act_mob: str
    name: str
    email: str
    res_score: str
    timestamp: str
    no_of_pages: str
    reco_field: str
    cand_level: str
    skills: str
    recommended_skills: str
    courses: str
    pdf_name: str


def get_connection():
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '3306')),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        db=os.getenv('DB_NAME', 'cv'),
        charset='utf8mb4',
        autocommit=True,
    )


def create_tables(cursor):
    cursor.execute("CREATE DATABASE IF NOT EXISTS cv")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            ID INT NOT NULL AUTO_INCREMENT,
            sec_token varchar(20) NOT NULL,
            ip_add varchar(50) NULL,
            host_name varchar(50) NULL,
            dev_user varchar(50) NULL,
            os_name_ver varchar(50) NULL,
            latlong varchar(50) NULL,
            city varchar(50) NULL,
            state varchar(50) NULL,
            country varchar(50) NULL,
            act_name varchar(50) NOT NULL,
            act_email varchar(50) NOT NULL,
            act_mob varchar(20) NOT NULL,
            Name varchar(500) NOT NULL,
            Email_ID VARCHAR(500) NOT NULL,
            resume_score VARCHAR(8) NOT NULL,
            Timestamp VARCHAR(50) NOT NULL,
            Page_no VARCHAR(5) NOT NULL,
            Predicted_Field BLOB NOT NULL,
            User_level BLOB NOT NULL,
            Actual_skills BLOB NOT NULL,
            Recommended_skills BLOB NOT NULL,
            Recommended_courses BLOB NOT NULL,
            pdf_name varchar(50) NOT NULL,
            PRIMARY KEY (ID)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_feedback (
            ID INT NOT NULL AUTO_INCREMENT,
            feed_name varchar(50) NOT NULL,
            feed_email VARCHAR(50) NOT NULL,
            feed_score VARCHAR(10) NOT NULL,
            comments VARCHAR(50) NOT NULL,
            Timestamp VARCHAR(50) NOT NULL,
            PRIMARY KEY (ID)
        )
    """)


def insert_analysis_record(record: AnalysisRecord):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO user_data (
                sec_token, ip_add, host_name, dev_user, os_name_ver, latlong,
                city, state, country, act_name, act_email, act_mob,
                Name, Email_ID, resume_score, Timestamp, Page_no,
                Predicted_Field, User_level, Actual_skills,
                Recommended_skills, Recommended_courses, pdf_name
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                record.sec_token, record.ip_add, record.host_name, record.dev_user, record.os_name_ver,
                record.latlong, record.city, record.state, record.country, record.act_name,
                record.act_mail, record.act_mob, record.name, record.email, record.res_score,
                record.timestamp, record.no_of_pages, record.reco_field, record.cand_level,
                record.skills, record.recommended_skills, record.courses, record.pdf_name,
            ),
        )
        connection.commit()
    finally:
        connection.close()


def insert_feedback_record(feed_name, feed_email, feed_score, comments, timestamp):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO user_feedback (feed_name, feed_email, feed_score, comments, Timestamp)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (feed_name, feed_email, feed_score, comments, timestamp),
        )
        connection.commit()
    finally:
        connection.close()
