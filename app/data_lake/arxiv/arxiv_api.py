import json
from datetime import datetime
from alive_progress import alive_bar, alive_it
import arxiv

def search_arxiv(keywords: list[str]) -> None:
    """
    Search arXiv for articles with the given keywords.
    Save the results in a JSON file.
    """
    big_slow_client = arxiv.Client(
        page_size=100,
        delay_seconds=3.0,
        num_retries=3
    )

    # For advanced query syntax documentation, see the arXiv API User Manual:
    # https://arxiv.org/help/api/user-manual#query_details

    results_json = []
    query = " AND ".join(keywords) if len(keywords) > 1 else keywords[0]
    print(f"\nSearching arXiv for: {query}\n...")

    for result in big_slow_client.results(arxiv.Search(query=query)):
        dict = vars(result)
        for key in dict:
            if isinstance(dict[key], datetime):
                dict[key] = str(dict[key])
            elif isinstance(dict[key], list):
                for i, item in enumerate(dict[key]):
                    if isinstance(item, arxiv.Result.Author):
                        dict[key][i] = item.name

        if not dict['doi']:
            dict['doi'] = f"arXiv.{dict['entry_id'].split('/')[-1].split('v')[0]}"

        dict.pop('links')
        # print(dict['title'][:50] + '...')
        results_json.append(dict)

    for article in results_json:
        article['abstract'] = article['summary']
        article['publication_date'] = article['published']
        article['cited_by'] = None
        article['publication_type'] = None#article['published']

    searche_file = '_'.join(keywords).replace(' ', '-') + '.json'
    print(f"Saving search results in: {searche_file}\n\n")
    with open(f'./app/data_lake/arxiv/searches/{searche_file}', 'w') as f:
        json.dump({'articles': results_json}, f, indent=4)


if __name__ == '__main__':
    search_arxiv(['Losses', 'Photovoltaic Systems'])