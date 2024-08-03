import os
import sys


def startup_app():

    required_files = {'./app/_searches/_gemini.json':'',
                    './app/_contexts/_keywords_grouping.txt': '',
                    './app/main.env': """GEMINI_API_KEY = ''\nIEEE_API_KEY = ''\nELSEVIER_API_KEY = ''\nENV = 
'LIVE'\nPDF_FOLDER = './pdfs'\nBIBTEX_FOLDER = './bibtex'""",
                      }

    if not os.path.exists('./pdfs'):
        os.mkdir('./pdfs')

    if not os.path.exists('./bibtex'):
        os.mkdir('./bibtex')

    if not os.path.exists('./app/_contexts'):
        os.mkdir('./app/_contexts')


    if not os.path.exists('./app/_searches'):
        os.mkdir('./app/_searches')

    for folder in os.listdir('./app/data_lake'):
        if os.path.isdir(f'./app/data_lake/{folder}'):
            if not os.path.exists(f'./app/data_lake/{folder}/searches'):
                os.mkdir(f'./app/data_lake/{folder}/searches')

    for req_file in required_files:
        if not os.path.exists(req_file):
            with open(req_file, 'w') as f:
                f.write(required_files[req_file])

