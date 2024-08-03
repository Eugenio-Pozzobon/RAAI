import streamlit as st
import time
from app.src.utils import *
def update_keywords(keywords: [KeywordGroup]):
    with open('./app/_contexts/_keywords_grouping.txt', 'w') as f:
        for key in keywords:
            f.write(str(key) + '\n')

# delete any keyword file in searches
def delete_searches(keyword: KeywordGroup):
    for file in load_search_files():
        if keyword.default_keywords_filename() in file:
            os.remove(f'./app/_searches/{file}')
            print(f"Deleted {file}")

    for lake in os.listdir('./app/data_lake/'):
        for file in os.listdir(f'./app/data_lake/{lake}'):
            if keyword.default_keywords_filename() in file:
                os.remove(f'./app/data_lake/{lake}/{file}')
                print(f"Deleted {file}")

keywords = load_keywords()

st.markdown('### Keywords')
add_cols = st.columns([3, 1])
new_keyword = add_cols[0].text_input('keywords separated by comma "," ', key='new_keyword')
add_cols[1].write(f"\n")
add = add_cols[1].button('➕ Add', key='add_keyword_button')
if add:
    keywords.append(KeywordGroup().load_from_string(new_keyword))
    update_keywords(keywords)
    st.rerun()

for i, key in enumerate(keywords):
    card = st.container()
    cols = card.columns([4, 1])
    cols[0].markdown(f'**{i+1}.** {key}')
    delete = cols[1].button('❌', key=key)
    if delete:
        keywords.remove(key)
        delete_searches(key)
        update_keywords(keywords)
        st.rerun()


if os.getenv('ENV') == 'DEV':
    print('\n\t\t---------------------'
          '\n\t\t--- DONE KEYWORDS ---'
          '\n\t\t----------------------\n')
