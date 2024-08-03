from crossref.restful import Works
import json
from alive_progress import alive_it

def search_crossref(keywords: list[str]) -> None:
    works = Works()

    query = '+'.join(keywords)
    w = works.query(query)

    search = []
    for i in alive_it(w):
        search.append(i)

    search_file = '_'.join(keywords).replace(' ', '-') + '.json'
    print(f"Saving search results in: {search_file}\n\n")
    with open(f'./searches/{search_file}', 'w') as f:
        json.dump(search, f, indent=4)

def search_with_doi(doi: str, grade:int, keyword:str) -> dict:
    works = Works()
    w = works.doi(doi)
    new_article = {}
    new_article['doi'] = w['DOI']
    new_article['abstract'] = None
    new_article['title'] = w['title'][0]
    new_article['cited_by'] = w['is-referenced-by-count']
    new_article['publication_type'] = w['type']
    new_article['grade'] = grade
    new_article['justification'] = 'Grade informed by user'
    new_article['keywords'] = keyword
    new_article['source'] = [w['publisher']]

    search_file = f'user.json'
    cache = []
    try:
        cache = json.load(open(f'./app/_searches/{search_file}', 'r'))['articles']
        if new_article['doi'] in [c['doi'] for c in cache]:
            print(f"Article {new_article['DOI']} already in user cache")
            return new_article
    except:
        pass
    cache.append(new_article)
    print(f"Saving search results in: {search_file}\n\n")
    with open(f'./app/_searches/{search_file}', 'w') as f:
        json.dump({
            'articles': cache
        }, f, indent=4)

    return new_article

if __name__ == '__main__':
    search_crossref(['Soiling', 'Photovoltaic Systems'])

