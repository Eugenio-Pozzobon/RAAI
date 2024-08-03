import json
import os

import numpy as np
import pandas as pd
import streamlit as st
import bibtexparser

from app.data_lake.elsevier.elsevier_api import search_elsevier
from app.src.bibtex import get_bibtex_entry, entries_to_str
from app.src.keyword_group import KeywordGroup


def load_env_variables():
    from dotenv import load_dotenv
    load_dotenv("./app/main.env")
    # print all env variables
    # for k, v in os.environ.items():
    #     print(f'{k}: {v}')


def load_search_files() -> list[str]:
    import os
    files = os.listdir(f'./app/_searches/')
    files = [file for file in files if file.endswith('.json')]
    files = [file for file in files if not file.startswith('_')]
    return files


def load_bibtex(df_articles: pd.DataFrame) -> pd.DataFrame:
    print('Loading bibtex')
    cache = {}
    bibtex_file = f"{os.getenv('BIBTEX_FOLDER')}/bibtex.bib"

    if df_articles.empty:
        return df_articles

    if os.path.exists(bibtex_file):
        with open(bibtex_file, 'r') as f:
            bibtex_str = f.read()
        bibdb = bibtexparser.loads(bibtex_str)
        cache = {entry['doi'].lower(): entry for entry in bibdb.entries}
        # print(f'Cache loaded: {cache}')

    df = df_articles[df_articles['has_file'] == True].copy()

    df = df[df['doi'].apply(lambda x: x.lower() not in cache.keys())]

    # print(df)
    if df.empty:
        df_articles['citation_key'] = ''
        return df_articles

    df['bibtex'] = df['doi'].apply(get_bibtex_entry)
    df = df.dropna(subset=['bibtex'])
    bibtex_str = entries_to_str(df['bibtex'].values.tolist())
    with open(bibtex_file, 'a') as f:
        f.write(bibtex_str)

    # return the citation key within df_articles
    df_articles['citation_key'] = df_articles['doi'].apply(
        lambda x: cache[x.lower()]['ID'] if x.lower() in cache.keys() else '')
    return df_articles


def load_search_json(file) -> list[dict[str, str]]:
    data = json.load(open(f'./app/_searches/{file}', 'r'))
    return data['articles']


def load_context(keyword: KeywordGroup) -> str:
    file = keyword.default_keywords_filename() + '.txt'
    if os.path.exists(f'./app/_contexts/{file}'):
        with open(f'./app/_contexts/{file}', 'r') as f:
            data = f.read()
            return data
    return None


def load_keywords() -> list[KeywordGroup]:
    with open('./app/_contexts/_keywords_grouping.txt', 'r') as f:
        keywords = f.read().split('\n')
    for k in keywords:
        if k == '':
            keywords.remove(k)

    keywords = [KeywordGroup().load_from_string(k) for k in keywords]
    return keywords


@st.cache_data()
def load_all_searches():
    # for each json file in searches, load the json file and merge all
    # return the merged json file
    json_files = load_search_files()
    all_searches = []
    for file in json_files:
        s = load_search_json(file)
        # append the file keywords to the searches
        keywords = (file.replace('.json', '').replace('_', ', ')
                    .replace('-', ' '))
        for search in s:
            all_searches.append(search)
        all_searches += s
    # remove duplicates by doi
    # force cited by as type int
    for search in all_searches:
        search['cited_by'] = int(search['cited_by']) if 'cited_by' in search and search['cited_by'] else 0

    # filtered_searches = [dict(t) for t in {tuple(d.items()) for d in all_searches}]
    return all_searches


def escape_special_chars(title):
    return (title
            .replace('_', '').replace('.', '').replace('(', '').replace(')', '')
            .replace('[', '[').replace(']', '').replace('{', '').replace('}', '').replace('|', '')
            .replace('*', '*').replace('+', '').replace('?', '').replace('^', '').replace('$', '')
            .replace('.', '.').replace(',', '').replace(':', '').replace(';', '').replace('!', ''))


@st.cache_data()
def merge_data(df_searches, df_gemini, df_reviews):
    if df_reviews.empty:
        df_reviews = pd.DataFrame(columns=['title', 'doi', 'file', 'folder', 'absolute_path',
                                           'review', 'has_review', 'has_file', 'has_read'])

    # drop keywords from gemini
    df_gemini = df_gemini.drop(columns=['keywords'])
    # print(df_searches.head(2).to_string(), df_gemini.head(2).to_string(), df_reviews.head(2).to_string())
    # print all cols
    # print("Gemini: ", df_gemini.columns)
    # print("Searches: ", df_searches.columns)
    # print("Reviews: ", df_reviews.columns)
    # MAKE TITLE UPPER
    df_reviews['title'] = df_reviews['title'].str.upper()
    df_searches['title'] = df_searches['title'].str.upper()
    df_searches['title_escaped'] = df_searches['title'].apply(escape_special_chars)
    df_reviews['doi'] = df_reviews['title'].apply(
        lambda x: df_searches[df_searches['title_escaped'].str.contains(x)]['doi'].values[0] if not
        df_searches[df_searches['title_escaped'].str.contains(x)]['doi'].empty else '')
    # df_reviews['doi'] = df_reviews['title'].apply(lambda x: df_searches[df_searches['title_escaped'].str.contains(x)]['doi'].values[0] if not df_searches[df_searches['title_escaped'].str.contains(x)]['doi'].empty else '')
    # drop title
    df_searches = df_searches.drop(columns=['title_escaped'])
    df_reviews = df_reviews.drop(columns=['title'])
    df = df_searches.merge(df_reviews, left_on='doi', right_on='doi', how='outer')
    df = df.drop(columns=['file', 'folder'])
    # filter where title is null

    df = df.drop(columns=[col for col in df.columns if 'gemini' in col])
    df = df.rename(columns={'grade': 'user_grade'})
    df = df.merge(df_gemini, left_on='doi', right_on='doi', how='outer')
    # make any "grade" col as a one col
    # df['grade'] = df['grade'].fillna(df['gemini_grade'])

    df = df[df['title'].notnull()]

    df = df.rename(columns={'gemini-1.5-flash-latest_grade': 'grade'})
    df = df.drop(columns=[col for col in df.columns if 'justification' in col])
    # there are duplicated grade cols with same name, merge all into one
    try:
        df['grade'] = np.where(df['user_grade'].isnull(), df['grade'], df['user_grade'])
        df = df.drop(columns=['user_grade'])
    except:
        pass

    return df


def list_search_file_names(sync_folder='./app/_searches'):
    return os.listdir(sync_folder)


def list_context_file_names(context_folder='./app/_contexts'):
    return os.listdir(context_folder)


def sync_files():
    search_files = list_search_file_names()
    context_files = list_context_file_names()
    # filter the extension from filename
    search_files = [file.split('.')[0] for file in search_files]
    context_files = [file.split('.')[0] for file in context_files]

    for search_file in search_files:
        if search_file not in context_files:
            with open(f"{search_file}.txt", 'w') as f:
                f.write('')


from app.data_lake.ieee.ieee import search_ieee
from app.data_lake.arxiv.arxiv_api import search_arxiv
from app.data_lake.crossref.crossref_api import search_crossref
import time


def data_lake_pipeline(keys: KeywordGroup, bibs):
    print(f"Data Lake Pipeline: {keys}")
    search_ieee(keys.get_keywords()) if 'IEEE' in bibs else None
    search_arxiv(keys.get_keywords()) if 'arXiv' in bibs else None
    search_elsevier(keys.get_keywords()) if 'Elsevier' in bibs else None
    time.sleep(2)


def get_stats_from_data_lake(keywords: list[KeywordGroup]):
    data_lake_data = []
    for keyword_group in keywords:
        for folder in os.listdir('./app/data_lake'):
            if not os.path.isdir(f"./app/data_lake/{folder}/searches"):
                continue
            file = f"{keyword_group.default_keywords_filename()}.json"
            if not os.path.exists(f"./app/data_lake/{folder}/searches/{file}"):
                continue
            with open(f"./app/data_lake/{folder}/searches/{file}", 'r') as f:
                data = json.load(f)
                total_records = len(data['articles'])
                data_lake_data.append({
                    'keyword group': ', '.join(keyword_group.get_keywords()),
                    'source': folder,
                    'records': total_records
                })
    data_lake_df = pd.DataFrame(data_lake_data)
    # pivot the source to be the columns
    data_lake_df = data_lake_df.pivot(index='keyword group', columns='source', values='records').fillna(0)
    # reset index and make the keygroup a list of itens
    data_lake_df = data_lake_df.reset_index()
    data_lake_df['keyword group'] = data_lake_df['keyword group'].apply(lambda x: x.split(', ') if x else [])
    return data_lake_df


def load_gemini():
    try:
        return pd.DataFrame(json.load(open('./app/_searches/_gemini.json'))['articles'])
    except:
        return pd.DataFrame()
