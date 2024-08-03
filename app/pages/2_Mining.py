import json
import os
import time

import pandas as pd
import streamlit as st
from multiprocessing import Pool

from app.src.data_pipeline import warehouse_pipeline
from app.src.gemini_abstract import gemini_grade
from app.src.utils import data_lake_pipeline, load_keywords, load_search_files, get_stats_from_data_lake

if 'running_mining' not in st.session_state:
    st.session_state.running_mining = False

st.markdown('### Data Mining Pipelines')
keywords = load_keywords()

if not keywords:
    st.error('No keywords found. Please add some key group in the Keywords page')
    st.stop()

try: data_lake_df = get_stats_from_data_lake(keywords)
except: data_lake_df = pd.DataFrame()

search_filters = st.columns([2, 2, 1])
selected_search_keyword = search_filters[0].selectbox('Select a keyword group', keywords, index=None)
all_bibs = ['IEEE', 'arXiv', 'Elsevier']
bibs = search_filters[1].multiselect('Select the source databases', all_bibs, all_bibs)

searching_action = 'Search Papers for all keywords' if not selected_search_keyword else 'Search Papers for selected keyword'


run_lake = st.toggle('run lake pipeline', value=True) if os.getenv('ENV') == 'DEV' else True

search_filters[2].write(f"\n")
start_mining = search_filters[2].button('Search Papers', disabled=st.session_state['running_mining'],
                         on_click=(lambda: st.session_state.update(running_mining=True)))

if start_mining:
    with st.status('Searching papers', expanded=True) as status:
        st.write("This will take a while...")
        st.write(f"Check at the command line interface the progress bars")
        if start_mining:
            if selected_search_keyword:
                data_lake_pipeline(selected_search_keyword, bibs)
                warehouse_pipeline(selected_search_keyword)
                st.session_state['running_mining'] = False
            else:
                for keyword in keywords:
                    if run_lake:
                        data_lake_pipeline(keyword, bibs)
                    warehouse_pipeline(keyword)

                st.session_state['running_mining'] = False

        if not st.session_state['running_mining']:
            status.update(label="Download complete!", state="complete", expanded=False)
        st.rerun()

elif st.session_state['running_mining']:
    with st.spinner('Downloading papers... check the cmd line', _cache=True):
        time.sleep(5)

if not data_lake_df.empty:
    st.markdown('___\n\n##### Data Lake Statistics:')
    st.dataframe(data_lake_df, use_container_width=True, hide_index=True)

if os.getenv('ENV') == 'DEV':
    print('\n\t\t-------------------'
          '\n\t\t--- DONE MINING ---'
          '\n\t\t-------------------\n')