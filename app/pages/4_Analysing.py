import os
import time
import dotenv
dotenv.load_dotenv('./app/main.env')
import streamlit as st
from multiprocessing import Pool
from app.src.data_pipeline import warehouse_pipeline
from app.src.gemini_abstract import gemini_grade
from app.src.keyword_group import KeywordGroup
from app.src.utils import load_keywords, load_search_files, load_gemini

if 'running_ai_filtering' not in st.session_state:
    st.session_state.running_ai_filtering = False

st.markdown('### AI Filtering')
keywords = load_keywords()
if not keywords:
    st.error('No keywords found. Please add some key group in the Keywords page')
    st.stop()

action_cols = st.columns([3, 1])
selected_search_keyword:KeywordGroup = action_cols[0].selectbox('Select a keyword group', keywords, index = None)
overwrite = st.toggle('Overwrite existing grades', value=False)
action_cols[1].write(f"\n")
cmd_filter = action_cols[1].button('Filter Papers', disabled=st.session_state['running_ai_filtering'],
                       on_click=(lambda: st.session_state.update(running_ai_filtering=True)))

if cmd_filter:
    with st.status('Filtering papers', expanded=True) as status:
        st.write("This will take a while...")
        st.write(f"Check at the command line interface the progress bars")
        st.write(f"You will get a toast notification when the process is complete")
        # load json file
        if selected_search_keyword:
            keywords = [selected_search_keyword]
        for key in keywords:
            if not gemini_grade(key, overwrite):
                st.toast("Error grading the papers. Check if there is context or searches")

        st.session_state['running_ai_filtering'] = False

        if not st.session_state['running_ai_filtering']:
            status.update(label="Filter complete!", state="complete", expanded=False)
        st.rerun()
elif st.session_state['running_ai_filtering']:
    with st.spinner('Filtering papers... check the cmd line', _cache=True):
        time.sleep(5)

if os.getenv('ENV') == 'DEV':
    print('\n\t\t----------------------'
          '\n\t\t--- DONE ANALYSING ---'
          '\n\t\t----------------------\n')