import base64

import streamlit as st
from PIL import Image


def show_logo():
    try:
        img = Image.open('logo/reume_logo.jpeg')
        st.image(img)
    except Exception:
        st.info('Logo image not found.')


def get_csv_download_link(df, filename, text):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href
