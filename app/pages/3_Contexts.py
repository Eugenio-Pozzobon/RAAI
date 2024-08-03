import streamlit as st
import time
from app.src.utils import *

# load keywords
st.markdown(f'### Context Management')

keywords = load_keywords()
if not keywords:
    st.error('No keywords found. Please add some key group in the Keywords page')
    st.stop()

selected_keyword = st.selectbox('Select the keyword for update the context', keywords)
context = load_context(selected_keyword)
context = st.text_area(label='Context', value=context, height=200)
if st.button('Update Context'):
    # open if does not exist
    file_name = selected_keyword.default_keywords_filename()
    with open(f'./app/_contexts/{file_name}.txt', 'w') as f:
        f.write(context)
    st.success('Context updated')
    time.sleep(1)
    st.rerun()

if os.getenv('ENV') == 'DEV':
    print('\n\t\t---------------------'
          '\n\t\t--- DONE CONTEXTS ---'
          '\n\t\t---------------------\n')