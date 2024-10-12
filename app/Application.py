# build the streamlit application
import json
import subprocess

import dotenv
import numpy as np

# todo: get a doi by the title article if it is downloaded.
# suggest new keywords search based on the metadata of each paper


# _. execute gemini s2 a chatbot retrieving any paper
import streamlit as st
import pandas as pd

from app.data_lake.crossref.crossref_api import search_with_doi
from app.src.utils import *

pd.set_option('future.no_silent_downcasting', True)
import os

from app.src.reviews import get_all_highlights, get_all_reviews
# LOAD DOT ENV
from dotenv import load_dotenv
import time


def make_clickable(link):
    # target _blank to open new window
    # extract clickable text to display for your link
    text = "LINK"
    return f'<a href="{link}">{text}</a>'


load_env_variables()
# create a page with a nov bar
st.set_page_config(page_title='RAAI', page_icon='🧠', layout='wide')

head_cols = st.columns([6, 1])
head_cols[0].markdown('### 🧠 RAAI: Research Assistant based on AI')

if head_cols[1].button('Reload all data'):
    st.cache_data.clear()
    st.info('Data reloading...')
    time.sleep(.25)
    st.rerun()

# add tab for each feature
tabs = ['Overview', 'Papers', 'Add']  # 'Search Keywords', 'Provide Context'
keywords = load_keywords()

df_gemini = load_gemini()

try:
    df_searches_review = merge_data(pd.DataFrame(load_all_searches()), df_gemini, pd.DataFrame(get_all_reviews()))

    df_searches_review = df_searches_review.drop_duplicates(subset=['title'])
    # df_searches_review = load_bibtex(df_searches_review)
    df_searches_review['citation_key'] = ''
except:
    df_searches_review = pd.DataFrame()

if df_searches_review.empty:
    st.warning('No data available. '
               'Please check the welcome page, setup the application, '
               'and run the data mining pipeline')
    st.stop()

tabs = st.tabs(tabs)
with tabs[0]:
    # dash with statistics
    filters = st.columns([2, 3])
    grade = filters[0].multiselect(
        "Select the AI grade",
        [5, 4, 3, 2, 1],
        [5, 4], key='grade_1')
    keyword: KeywordGroup = filters[1].selectbox('Select the keyword', keywords, index=None, key='keyword_1')

    df = df_searches_review.copy()
    df = df[df['grade'].isin(grade)] if grade else df
    df = df[df['keywords'] == str(keyword)] if keyword else df
    total_articles = len(df)
    total_articles_reviewed = len(df[df['has_review'] == True])
    total_articles_read = len(df[df['has_read'] == True])
    total_downloaded = len(df[df['has_file'] == True])

    metrics_cols = st.columns(4)
    metrics_cols[0].metric('Papers', total_articles)
    metrics_cols[1].metric('Downloaded', total_downloaded)
    metrics_cols[2].metric('Has read', total_articles_read)
    metrics_cols[3].metric('Reviewed', total_articles_reviewed)

    # warns if there is article without grade
    if df_searches_review[df_searches_review['grade'].isnull()].shape[0]:
        st.warning('There are articles without grade')
        # offer a button to nagivate to the page to grade the articles
        if st.button('Grade Articles'):
            st.switch_page('pages/4_Analysing.py')

with tabs[1]:
    # TOGGLE TO FILTER IF HAS REVIEW
    toggles = {
        'With Reviews': {
            'filter': 'has_review',
            'value': True
        },
        'Has Downloaded': {
            'filter': 'has_file',
            'value': True
        },
        'Has Read': {
            'filter': 'has_read',
            'value': True
        },

    }

    display_highlights = False
    cols = st.columns([2, 2, 1, 1])
    keyword = cols[0].selectbox('Select the keyword', keywords, key='keyword_2', index=None)
    sources = cols[1].multiselect('Select the source', ['arxiv', 'ieee', 'elsevier'], ['arxiv', 'ieee', 'elsevier'])
    publication_types = df_searches_review['publication_type'].unique()
    publication_types = [pub for pub in publication_types if pub]
    publication_type = cols[2].multiselect('Select the publication type', publication_types)
    sort_by = cols[3].selectbox('Sort by', ['grade', 'title', 'publication_date', 'cited_by'], index=1)

    filter_cols = st.expander("Additional Filters").columns(2)
    grade = filter_cols[0].multiselect(
        "Select the AI grade",
        [5, 4, 3, 2, 1],
        [5, 4], key='grade_2')

    filters = filter_cols[0].multiselect('Filter Papers', list(toggles.keys()),
                                         key='filter_toggles')
    search = filter_cols[1].text_input('Search by article title or doi')

    excludes = filter_cols[1].multiselect('Exclude Papers', list(toggles.keys()),
                                          key='excluder_toggles')

    df = df_searches_review.copy()
    # filter if the df sources is in the sources
    df = df[df['source'].apply(lambda x: any([s in x for s in sources]))] if sources else df
    df = df[df['publication_type'].isin(publication_type)] if publication_type else df
    df['source'] = df['source'].apply(lambda x: [x] if type(x) == str else x)

    df['has_review'] = df['has_review'].fillna(False)
    df['has_file'] = df['has_file'].fillna(False)
    df['has_read'] = df['has_read'].fillna(False)

    df = df[df['keywords'] == str(keyword)] if keyword else df
    df = df[df['grade'].isin(grade)] if grade else df
    df['doi'] = df['doi'].apply(lambda x: x if x.startswith('http') else f"https://doi.org/{x}")

    for f in filters:
        df = df[df[toggles[f]['filter']] == toggles[f]['value']]

    for e in excludes:
        df = df[df[toggles[e]['filter']] != toggles[e]['value']]

    filter_with_file = 'Has Downloaded' in filters


    # duplicated = df[df.duplicated(subset=['title'])]
    # if not duplicated.empty:
    #     st.warning('There are duplicated titles')
    #     st.dataframe(duplicated[['title', 'doi']], hide_index=True, use_container_width=True)

    # make publication_date a datetime and handle each row individually
    def search_articles_in_db(search):
        df_searching = df_searches_review.copy()
        return df_searching[df_searching['title'].str.contains(search, case=False) |
                            df_searching['doi'].str.contains(search, case=False)]


    df = search_articles_in_db(search) if search else df
    for index, row in df.iterrows():
        if row['publication_date']:
            try:
                # if there is '-' just one time, split and get the last part
                cnt = row['publication_date'].count('-')
                if cnt != 1:
                    df.at[index, 'publication_date'] = pd.to_datetime(row['publication_date']).strftime('%Y-%m-%d')
                else:
                    df.at[index, 'publication_date'] = pd.to_datetime(row['publication_date'].split('-')[1]).strftime(
                        '%Y-%m-%d')

            except:
                if os.getenv('ENV') == 'DEV':
                    print(f"Error in pubdate: {row['publication_date']}")
                df.at[index, 'publication_date'] = ''

        else:
            df.at[index, 'publication_date'] = ''

    df = df.sort_values(by=sort_by, ascending=True if sort_by == 'title' else False)
    # print the df line by line, with buttons to open doi and file
    if df.empty:
        st.error('No articles available for this query')

    if not df.empty:
        st.write(f'Displaying {len(df)} articles:')
        for index, row in df.iterrows():
            def open_file(path=row['absolute_path']):
                print(f'Opening {path}')
                if os.name == 'posix':
                    os.system(f'open "{path}"')
                elif os.name == 'nt':
                    subprocess.call(["start", path], shell=True)
                else:
                    print('OS not supported for opening File')


            reviews = '\n'.join(row['review']) if filter_with_file and row['review'] else ''
            # abstract if filter_without_file
            grade = f"**AI Grade: {row['grade']}**"

            text = f"Abstract - {row['abstract']}" if not filter_with_file else f"Reviews - {reviews}" if reviews else ''
            container = st.container(border=True)

            c = container.columns([5, 1])
            pub_type = f"- {row['publication_type']}" if row['publication_type'] else ''
            c[0].markdown(f"**TITLE: {row['title'].strip()}{pub_type}**")
            stat_cols = c[0].columns([1, 2, 1, 1])
            pub_date = row['publication_date']
            stat_cols[0].markdown(grade)
            stat_cols[1].markdown(f"**Publication Date: {pub_date}**")
            cited_by = row['cited_by'] if row['cited_by'] and row['cited_by'] != np.nan else 0
            stat_cols[2].markdown(f"**Cited by: {cited_by:.0f}**")
            stat_cols[3].markdown(f"**Sources: {','.join(row['source'])}**")
            # c[0].markdown()
            if row['citation_key']:
                cite_as = r"\cite{" + row['citation_key'] + "}"
                c[1].code(cite_as, language='text')
            else:
                c[1].info('No citation key')

            cols = container.columns([10, 1])
            cols[0].markdown(text)
            if reviews == '' and row['has_read']:
                cols[0].error(f"Missing review for this article")
            elif reviews == '' and not row['has_read']:
                cols[0].warning(f"Article not read yet")

            # copy to clipboard button for citation_key
            cols[1].button('Open File', on_click=open_file, key=(index + 1), disabled=not row['has_file'])
            cols[1].link_button('Open DOI', row['doi'], disabled=not row['doi'])

            if display_highlights:
                container.write('**Highlights:**')
                container.json(get_all_highlights(row['absolute_path']), expanded=False)


def search_articles_in_db(df, search):
    df = df[df['title'].str.contains(search, case=False) | df['doi'].str.contains(search, case=False)]
    return df


with tabs[2]:
    # allow the user to add a new paper to the database
    st.markdown('#### Add a new paper')
    st.write('Add a new paper to the database, informing the DOI and the grade that specify the relevance of the '
             'article for your research')
    input_cols = st.columns([4, 2])
    new_doi = input_cols[0].text_input('DOI')
    user_grade = input_cols[1].number_input('Specify the grade', min_value=1, max_value=5, value=4)
    new_doi_keyword = st.selectbox('Select the keyword group', keywords, key='keyword_3', index=None)

    # find info about the doi using cross ref
    if st.button('Search with DOI') and new_doi and user_grade and new_doi_keyword:
        df = search_articles_in_db(df_searches_review, new_doi)
        if not df.empty:
            st.error('DOI already in the database')
        else:
            new_article = search_with_doi(new_doi, user_grade, new_doi_keyword)
            if new_article:
                # write 'title', 'abstract', 'DOI'
                st.write(new_article['title'])
                st.write(new_article['doi'])
                st.success('DOI found')
            else:
                st.error('DOI not found')
        # st.rerun()



if os.getenv('ENV') == 'DEV':
    print('\n\t\t------------------------'
          '\n\t\t--- DONE APPLICATION ---'
          '\n\t\t------------------------\n')
