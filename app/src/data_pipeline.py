# for each search folder inside each folder of ./data_lake, load the JSON files
# for each json file, keep DOI, title, abstract, pdf_url, publication_date, and source
import os
import json
import sys

from app.src.keyword_group import KeywordGroup

sys.path.append(os.getenv('CWD'))

# TODO:             search['keywords'] = keywords

def filter_duplicated_dois(search_articles):
    dois = [a['doi'] for a in search_articles]
    # identify duplicated dois
    duplicated_dois = [d for d in dois if dois.count(d) > 1]
    # print(f"\tDuplicated DOIs: {duplicated_dois}\n")
    duplicated_searches = [a for a in search_articles if a['doi'] in duplicated_dois]
    # drop duplicated dois from search_articles
    search_articles = [a for a in search_articles if a['doi'] not in duplicated_dois]
    # join the source key for duplicated dois
    for d in duplicated_dois:
        sources = [a['source'] for a in duplicated_searches if a['doi'] == d]
        sources = [s for sublist in sources for s in sublist]
        for s in duplicated_searches:
            if s['doi'] in [a['doi'] for a in search_articles]:
                continue
            if s['doi'] == d:
                s['source'] = sources
                search_articles.append(s)

    return search_articles

def warehouse_pipeline(keyword_group:KeywordGroup):
    print(f"\nProcessing Data for: {keyword_group.get_keywords()}")
    key_file = keyword_group.default_keywords_filename()
    search_articles = []
    for folder in os.listdir('./app/data_lake'):
        if not os.path.isdir(f"./app/data_lake/{folder}/searches"):
            continue
        file = f"{key_file}.json"
        if not os.path.exists(f"./app/data_lake/{folder}/searches/{file}"):
            continue
        with open(f"./app/data_lake/{folder}/searches/{file}", 'r') as f:
            data = json.load(f)
            # print(f"\nProcessing Warehouse Pipeline: {file}")
            for article in data['articles']:
                keywords = key_file.replace('_', ', ').replace('-', ' ')
                a = {
                    'doi': article['doi'] if 'doi' in article else None,
                    'title': article['title'] if 'title' in article else None,
                    'abstract': article['abstract'] if 'abstract' in article else None,
                    'source': [f"{folder}"],
                    'cited_by': article['cited_by'] if 'cited_by' in article else None,
                    'publication_date': article['publication_date'] if 'publication_date' in article else None,
                    'publication_type': article['publication_type'] if 'publication_type' in article else None,
                    'keywords': keywords,
                }
                search_articles.append(a)

    # check for duplicated DOI in the search, and join the source key
    search_articles = filter_duplicated_dois(search_articles)

    json_articles = {
        "articles": search_articles
    }
    with open(f'./app/_searches/{key_file}.json', 'w') as f:
        json.dump(json_articles, f, indent=4)