import os

from app.src.keyword import Keyword


keywords_grouping_paths = [
    'app/_contexts/'
    'app/_searches/'
    'app/data_lake/*/searches/'
]
class KeywordGroup:
    def __init__(self):
        self.keywords: list[Keyword] = []
        self.file_name: str = ''

    def add_keyword(self, keyword: Keyword) -> None:
        self.keywords.append(keyword)

    def get_keywords(self) -> list[str]:
        return [k.nome for k in self.keywords]

    def default_keywords_filename(self) -> str:
        self.file_name = '_'.join([k.path() for k in self.keywords])
        return self.file_name

    def load_keywords_by_filename(self, filename: str) -> 'KeywordGroup':
        self.keywords = [Keyword().from_path(k) for k in filename.split('_')]
        return self

    def load_keywords_by_names(self, names: list[str]) -> 'KeywordGroup':
        self.keywords = [Keyword().from_path(k) for k in names]
        return self

    def load_from_string(self, string: str) -> 'KeywordGroup':
        self.keywords = [Keyword().from_path(k) for k in string.split(',')]
        # trim the strings
        for k in self.keywords:
            k.nome = k.nome.strip()
        return self


    def delete(self) -> None:
        for path in keywords_grouping_paths:
            if '*' in path:
                for folder in os.listdir(path.split('*')[0]):
                    if os.path.exists(f"{path.split('*')[0]}{folder}{path.split('*')[1]}/{self.file_name}.txt"):
                        os.remove(f"{path.split('*')[0]}{folder}{path.split('*')[1]}/{self.file_name}.txt")

            elif os.path.exists(f'{path}{self.file_name}.txt'):
                os.remove(f'{path}{self.file_name}.txt')

        self.keywords = []
        self.file_name = ''



    def __str__(self):
        return ', '.join([k.nome for k in self.keywords])

