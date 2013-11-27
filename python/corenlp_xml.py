import xml.etree.ElementTree as ET

class Document:
    def __init__(self, f):
        self.sentences = []
        self._ingest(f)

    def _ingest(self, f):
        tree = ET.parse(f)
        #root = tree.getroot()
        sentences = tree.findall('//sentences/sentence')
        for s in sentences:
            self.sentences.append(Sentence(s))
                        

class Sentence:
    def __init__(self, sentence):
        self.tokens = []
        self.typed_deps = set()
        deps = sentence.findall('.//dependencies')[2]
        tokens = sentence.findall('.//token')
        for t in tokens:
            self.tokens.append(Token(t))
        self._build_deps(deps)
            
    def space_sep_str(self):
        str_buff = self.tokens[0].word
        for t in self.tokens[1:]:
            str_buff += ' ' + t.word
        return str_buff

    def _build_deps(self, deps):
        for dep in deps:
            for arg in dep:
                
                if arg.tag == 'governor':
                    gov_idx = int(arg.get('idx')) - 1
                if arg.tag == 'dependent':
                    dep_idx = int(arg.get('idx')) - 1
                    
            dtype = dep.get('type')
            self.typed_deps.add(Dependency(dtype, gov_idx, dep_idx, self))
            
class Token:
    def __init__(self, token):
        self.word = None
        self.char_offset_start = None
        self.char_offset_end = None
        self.pos = None
        self.lem = None
        self.ne = None

        for child in token:
            if child.tag == 'word':
                self.word = child.text
            elif child.tag == 'CharacterOffsetBegin':
                self.char_offset_start = int(child.text)
            elif child.tag == 'CharacterOffsetEnd':
                self.char_offset_end = int(child.text)
            elif child.tag == 'POS':
                self.pos = child.text
            elif child.tag == 'lemma':
                self.lem = child.text
            elif child.tag == 'NER':
                self.ne = child.text    

class Dependency:
    def __init__(self, dtype, gov_idx, dep_idx, sentence):
        self.type = dtype
        self.gov_idx = gov_idx
        self.dep_idx = dep_idx
        self.gov = sentence.tokens[gov_idx]
        self.dep = sentence.tokens[dep_idx]
    def __str__(self):
        return '({}:{} <- {} -- {}:{})'.format(self.dep_idx, self.dep.word, self.type, self.gov_idx, self.gov.word) 
        
