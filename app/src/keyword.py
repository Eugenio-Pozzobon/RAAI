class Keyword:

    def __init__(self):
        self.nome:str = ''

    def path(self) -> str:
        return self.nome.replace(' ', '-')

    def from_path(self, path) -> 'Keyword':
        self.nome = path.replace('-', ' ')
        return self
