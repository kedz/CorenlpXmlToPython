import xmltodict

  
class Document:
    def __init__(self, f):
        self.sentences = []

        self._ingest(f)

    def _ingest(self, f):
        xml = xmltodict.parse(f)['root']['document']
        for s in xml['sentences']['sentence']:
            self.sentences.append(Sentence(s))

class Sentence:
    def __init__(self, xml):
        self.tokens = []
        for token in xml['tokens']['token']:
            self.tokens.append(Token(token))
            
class Token:
    def __init__(self, xml):
        self.word = xml['word'] 
