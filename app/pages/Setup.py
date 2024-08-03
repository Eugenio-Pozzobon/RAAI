import dotenv, time, os
import streamlit as st

from app.src.utils import load_env_variables

st.markdown('### Setup\n\nRestart the application after changing any field.')

load_env_variables()
GEMINI_API_KEY = st.text_input('Gemini API Key', type='password', value=os.getenv('GEMINI_API_KEY'))
IEEE_API_KEY = st.text_input('IEEE API Key', type='password', value=os.getenv('IEEE_API_KEY'))
ELSEVIER_API_KEY = st.text_input('Elsevier API Key', type='password', value=os.getenv('ELSEVIER_API_KEY'))
PDF_FOLDER = st.text_input('PDF Folder', value=os.getenv('PDF_FOLDER'))
BIBTEX_FOLDER = st.text_input('Bibtex Folder', value=os.getenv('BIBTEX_FOLDER'))
# add a button
if st.button('Save'):
    if GEMINI_API_KEY:
        dotenv.set_key('./app/main.env', 'GEMINI_API_KEY', GEMINI_API_KEY)
    if IEEE_API_KEY:
        dotenv.set_key('./app/main.env', 'IEEE_API_KEY', IEEE_API_KEY)
    if ELSEVIER_API_KEY:
        dotenv.set_key('./app/main.env', 'ELSEVIER_API_KEY', ELSEVIER_API_KEY)
    if PDF_FOLDER:
        dotenv.set_key('./app/main.env', 'PDF_FOLDER', PDF_FOLDER)
    if BIBTEX_FOLDER:
        dotenv.set_key('./app/main.env', 'BIBTEX_FOLDER', BIBTEX_FOLDER)

    st.success('API Keys are set. Restart the application!')
    time.sleep(1)
    st.empty()
# show an alert if the api keys are set

if os.getenv('ENV') == 'DEV':
    print('\n\t\t------------------'
          '\n\t\t--- DONE SETUP ---'
          '\n\t\t-------------------\n')