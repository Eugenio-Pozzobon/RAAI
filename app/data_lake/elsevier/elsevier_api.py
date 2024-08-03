import os

import alive_progress
from elsapy.elsclient import ElsClient
from elsapy.elsprofile import ElsAuthor, ElsAffil
from elsapy.elsdoc import FullDoc, AbsDoc
from elsapy.elssearch import ElsSearch
import json


def search_elsevier(querys: list[str]):
    # load cache
    file_namw = f'./app/data_lake/elsevier/searches/{"_".join(querys).replace(" ", "-")}.json'

    cache = json.load(open(file_namw, 'r'))['articles'] if os.path.exists(file_namw) else []
    for i, c in enumerate(cache):
        c['index'] = i
        c['cited_by'] = int(c['cited_by'])

    max_index = max([c['index'] for c in cache]) if cache else 0
    start = f'&start={max_index}'

    client = ElsClient('02f9855a70a9e8aac0aee98548696454', num_res=200)
    print("Searching Elsevier for ", querys)
    doc_srch = ElsSearch(' AND '.join(querys) + start, 'scopus') # sciencedirect
    doc_srch.execute(client, get_all=True,
                     fields=['pii', 'prism:doi', 'dc:title', 'prism:publicationName'
                             'prism:aggregationType', 'citedby-count', 'subtypeDescription',
                             'prism:coverDate'])

    print(f"\tElsevier found {len(doc_srch.results)} results")

    articles_with_abstract = []
    cnt = len(cache)
    for article in alive_progress.alive_it(doc_srch.results):
        doi_doc = FullDoc(sd_pii=article['pii']) if 'pii' in article else FullDoc(doi=article['prism:doi']) if (
                'prism:doi' in article) else None
        if doi_doc and doi_doc.read(client) and (article['prism:doi'] not in [c['doi'] for c in cache]):
            doi_doc.write()
            new_elsevier_article = {}
            new_elsevier_article['abstract'] = doi_doc.data['coredata']['dc:description'] if ('dc:description' in doi_doc.data['coredata']) else None
            new_elsevier_article['title'] = doi_doc.data['coredata']['dc:title'] if 'dc:title' in doi_doc.data['coredata'] else None
            new_elsevier_article['source'] = doi_doc.data['coredata']['prism:publicationName'] if 'prism:publicationName' in doi_doc.data['coredata'] else None
            new_elsevier_article['doi'] = doi_doc.data['coredata']['prism:doi'] if 'prism:doi' in doi_doc.data['coredata'] else None
            new_elsevier_article['publication_type'] = doi_doc.data['coredata']['aggregationType'] if 'aggregationType' in doi_doc.data['coredata'] else None
            new_elsevier_article['publication_date'] = doi_doc.data['coredata']['prism:coverDate'] if 'prism:coverDate' in doi_doc.data['coredata'] else None
            new_elsevier_article['cited_by'] = article['citedby-count'] if 'citedby-count' in article else None
            new_elsevier_article['index'] = cnt
            cnt += 1
            if new_elsevier_article['abstract']:
                articles_with_abstract.append(new_elsevier_article)
        # else:
            # print(f"Error reading document {article['prism:doi']}")

    cache.extend(articles_with_abstract)
    all = [article for article in cache if article['doi']]

    with open(file_namw, 'w') as f:
        json.dump({'articles': all}, f, indent=4)
