import json
import os
import sys
# if app is not a folder in the root of the project, change the path
if 'app' not in os.listdir():
    os.chdir('../../../')
from app.src.utils import load_search_json, load_env_variables
from app.data_lake.ieee.xplore_api import XPLORE

load_env_variables()

def search_ieee(query_texts: list[str]):

    print(f'Running IEEE search for {query_texts}')

    query = XPLORE(os.getenv('IEEE_API_KEY'))
    query.queryText(" AND ".join(query_texts))

    file_name = "_".join(query_texts) + '.json'
    file_name = file_name.replace(' ', '-')
    cache = []
    if os.path.exists(f'./app/data_lake/ieee/searches/{file_name}'):
        cache = json.load(open(f'./app/data_lake/ieee/searches/{file_name}', 'r'))['articles']
        article_length = len(cache)
        query.startRecord = article_length

        if os.getenv('ENV') == 'DEV':
            print(f'\tCache length: {article_length}')

    # query.insertionEndDate('2024-05-15')
    query.maximumResults(100)
    query.dataType('json')
    query.dataFormat('object')
    # qry = query.callAPI(debugModeOff=False)
    # print('query', qry)
    try:
        data = query.callAPI()
        # print('data', data)
    except Exception as e:
        print('\tError:', e)
        return
    print('\tTotal found records:', data['total_records'])
    if data['total_records'] == 0:
        print('\tNo records found')
        return

    # inside the list of articles, in data, add eugenio and gemini columns
    articles = data['articles']
    # check if all cache has doi
    # drop any article in cache that has not doi
    non_doi_articles = len([article for article in articles if 'doi' not in article])
    articles = [article for article in articles if 'doi' in article]
    if cache:
        articles = [article for article in articles if article['doi'] not in [c['doi'] for c in cache]]

    cache.extend(articles)
    map_repeater = {
        'total_records': 0,
        'cnt': 0,
    }
    if (len(cache) + non_doi_articles) < (data['total_records']//100)*100:
        while (len(cache) + non_doi_articles) < (data['total_records']//100)*100:
            try:
                query.startRecord = len(cache) + non_doi_articles
                data = query.callAPI()
                articles = data['articles']
                non_doi_articles += len([article for article in articles if 'doi' not in article])
                articles = [article for article in articles if 'doi' in article]
                articles = [article for article in articles if article['doi'] not in [c['doi'] for c in cache]]
                cache.extend(articles)


                if map_repeater['total_records'] == len(cache) + non_doi_articles:
                    map_repeater['cnt'] += 1
                    if map_repeater['cnt'] > 2:
                        break
                else:
                    map_repeater['total_records'] = len(cache) + non_doi_articles
                    map_repeater['cnt'] = 1
                if os.getenv('ENV') == 'DEV':
                    print('\tTotal records:', len(cache) + non_doi_articles)

            except Exception as e:
                if os.getenv('ENV') == 'DEV':
                    print('\tError:', e)
    else:
        if os.getenv('ENV') == 'DEV':
            print('\tCache already complete. Total records:', len(cache) + non_doi_articles)



    for article in cache:
        article['publication_type'] = article['content_type'] if 'content_type' in article else None
        article['cited_by'] = article['citing_paper_count'] + article['citing_patent_count'] if 'citing_paper_count' in article else None

    with open(f'./app/data_lake/ieee/searches/{file_name}', 'w') as f:
        # add cache as list of articles
        cache = {'articles': cache}
        json.dump(cache, f, indent=4)

    print('\tTotal articles:', len(cache['articles']))


if __name__ == '__main__':
    search_ieee(query_texts = ["Soiling", "Photovoltaic systems", "Machine Learning"])