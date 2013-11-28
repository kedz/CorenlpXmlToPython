import xml.etree.ElementTree as ET

class Document:
    def __init__(self, fname, basic_deps=False, collapsed_deps=False, collapsed_ccproc_deps=True):
        self.fname = fname
        self.sentences = []
        
        tree = ET.parse(fname)
        sentences = tree.findall('//sentences/sentence')
        for s in sentences:
            self.sentences.append(Sentence(s, basic_deps=basic_deps, collapsed_deps=collapsed_deps, collapsed_ccproc_deps=collapsed_ccproc_deps))


    def __iter__(self):
        return iter(self.sentences)

                        

class Sentence:
    def __init__(self, sentence, basic_deps=False, collapsed_deps=False, collapsed_ccproc_deps=True):
        self.tokens = []
        
        self.basic_deps = set() if basic_deps else None
        self.coll_deps = set() if collapsed_deps else None
        self.coll_ccp_deps = set() if collapsed_ccproc_deps else None
        
        self.deps = self.basic_deps if basic_deps else None
        self.deps = self.coll_deps if collapsed_deps else None
        self.deps = self.coll_ccp_deps if collapsed_ccproc_deps else None
        
        tokens = sentence.findall('.//token')
        for t in tokens:
            self.tokens.append(Token(t))
        
        deps_types = sentence.findall('.//dependencies')
        for deps in deps_types:
            if deps.get('type') == 'basic-dependencies' and basic_deps:
                self._build_deps(deps, self.basic_deps)
            if deps.get('type') == 'collapsed-dependencies' and collapsed_deps:
                self._build_deps(deps, self.coll_deps)
            if deps.get('type') == 'collapsed-ccprocessed-dependencies' and collapsed_ccproc_deps:
                self._build_deps(deps, self.coll_ccp_deps)
    
        

    def __iter__(self):
        return iter(self.tokens)
            
    def space_sep_str(self):
        str_buff = self.tokens[0].word
        for t in self.tokens[1:]:
            str_buff += ' ' + t.word
        return str_buff

    def _build_deps(self, deps, deps_set):
                
        for dep in deps:
            for arg in dep:
                
                if arg.tag == 'governor':
                    gov_idx = int(arg.get('idx')) - 1
                if arg.tag == 'dependent':
                    dep_idx = int(arg.get('idx')) - 1
                    
            dtype = dep.get('type')
            deps_set.add(Dependency(dtype, gov_idx, dep_idx, self))
        
                
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
        
