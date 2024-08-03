import json
import os
import alive_progress
import google.generativeai as genai
import sys
import time
from dotenv import load_dotenv

from app.src.keyword_group import KeywordGroup
from app.src.utils import load_search_files, load_search_json, load_context, load_keywords

load_dotenv("./app/main.env")


# load dot env
def setup_google_gemini():
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    # Set up the model
    generation_config = {
      "temperature": 0,
      "top_p": 0.95,
      "top_k": 64,
      "max_output_tokens": 4096,
    }

    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
    ]
    # models = genai.list_models()
    # import pprint
    # pprint.pprint(models)
    # for model in genai.list_models():
    #     pprint.pprint(model)
    # exit()
    # model_name = "gemini-1.0-pro-latest"
    # model_name = "gemini-1.5-pro-latest"
    model_name = "gemini-1.5-flash-latest"
    model = genai.GenerativeModel(model_name=model_name,
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)
    return model, model_name


def gemini_grade(keyword: KeywordGroup, overwrite=False):
    file_name = keyword.default_keywords_filename() + '.json'
    model, model_name = setup_google_gemini()
    max_requests_per_minute = 15 if os.getenv('ENV') == 'LIVE' else None
    gemini_file = '_gemini.json'
    try:cache = json.load(open(f'./app/_searches/{gemini_file}', 'r'))['articles']
    except:cache = []

    # load all keywords. Filter any article in cache that has not any keyword
    keys = load_keywords()
    for c in cache:
        if c['keywords'] not in [k.default_keywords_filename() for k in keys]:
            cache.remove(c)

    if os.getenv('ENV') == 'DEV':
        print(f'\nProcessing Gemini Grade: {file_name}')

    research_context = load_context(keyword)
    if research_context == '' or research_context is None:
        print(f'\tNo context for {file_name}')
        return None

    articles = load_search_json(file_name)
    for article in alive_progress.alive_it(articles):

        if f'{model_name}_grade' in article.keys():
            article['keywords'] = file_name.split('.')[0]

        if article['doi'] in [a['doi'] for a in cache] and not overwrite:
            article[f'{model_name}_grade'] = [a[f'{model_name}_grade'] for a in cache if a['doi'] == article['doi']][0]
            article[f'{model_name}_justification'] = [a[f'{model_name}_justification'] for a in cache if a['doi'] ==
                                                      article['doi']][0]
            article['keywords'] = file_name.split('.')[0]
            continue

        if not f'{model_name}_grade' in article.keys():

            prompt_parts = [
                f"You are a phd researcher. + {research_context}"
                "Given the following article title and abstract, classify it "
                "within a grade from 1 to 5, where 5 is an article that I must read to make my systematic review, and 1 means that "
                "the article does not contribute to my research. Give a short answer, returning a json with the grade "
                "as a integer number and the justification as a string."
                # "{'grade': integer value here, 'justification': 'Your justification here.'}"
                "The justification must be clear and objective. "
                f". Title: {article['title']}, Abstract: {article['abstract']}",
            ]

            response = model.generate_content(prompt_parts)
            try:
                response_json = json.loads(response.text.strip()[3:-3].replace('json', ''))
                article[f'{model_name}_grade'] = response_json['grade']
                article[f'{model_name}_justification'] = response_json['justification']
                article['keywords'] = file_name.split('.')[0]
            # print(article['title'], article[f'{model_name}_grade'], article[f'{model_name}_justification'])
            except Exception as e:
                print(f"\tError grading article {article['title']}: {e}"
                      f"\nWait to finish the pipeline and try again later.")
                continue

            if max_requests_per_minute:
                time.sleep(60 / max_requests_per_minute)

        # save each one as a cache
        # extend cache with the article
        if overwrite:
            cache = [a for a in cache if a['doi'] != article['doi']]

        appended = {
            'doi': article['doi'],
            'keywords': article['keywords'],
            f'{model_name}_grade': article[f'{model_name}_grade'],
            f'{model_name}_justification': article[f'{model_name}_justification']
        }
        cache.append(appended)
        with open(f'./app/_searches/{gemini_file}', 'w') as f:
            json.dump({'articles': cache}, f, indent=4)

    return True

    # filter all keys to be only grade, justification, doi and keys
    # articles = [{k: v for k, v in a.items() if k in ['doi', 'keywords', f'{model_name}_grade',
    #                                                  f'{model_name}_justification']} for a in articles]
    #
    # with open(f'./app/_searches/{gemini_file}', 'w') as f:
    #     json.dump({'articles': articles}, f, indent=4)