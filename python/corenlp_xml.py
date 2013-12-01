import xml.etree.ElementTree as ET
from os.path import exists

class Document:
    def __init__(self, fname_or_string, coref=False, parse=False, basic_deps=False, collapsed_deps=False, collapsed_ccproc_deps=True):
        self.fname = None
        self.sentences = []
        self.coref = []

        if exists(fname_or_string):
            tree = ET.parse(fname_or_string)
        else:
            tree = ET.fromstring(fname_or_string)
        
        sentences = tree.findall('.//sentences/sentence')
        for s in sentences:
            self.sentences.append(Sentence(s, parse=parse, basic_deps=basic_deps, collapsed_deps=collapsed_deps, collapsed_ccproc_deps=collapsed_ccproc_deps))

        if coref:
            coref_chains = tree.findall('.//coreference/coreference') 
            print len(coref_chains)
            for coref_chain in coref_chains:
                self.coref.append(CorefChain(coref_chain, self))

        tree = None

    def __iter__(self):
        return iter(self.sentences)

                        

class CorefChain:
    def __init__(self, coref_el, doc):
        #mentions = coref_el.findall('//mention')
        self.mentions = []
        for mention in coref_el:
            
            for t in mention:
                if t.tag == 'sentence':
                    sent = int(t.text) - 1
                if t.tag == 'start':
                    start = int(t.text) - 1
                if t.tag == 'end':
                    end = int(t.text) - 1
                if t.tag == 'head':
                    head = int(t.text) - 1
            self.mentions.append(Mention(sent, start, end, head))
            doc.sentences[sent].tokens[head].coref_chain = self
        
            

class Mention:
    def __init__(self, sentence, start, end, head):
        self.sent = sentence
        self.start = start
        self.end = end
        self.head = head


class Sentence:
    def __init__(self, sentence, parse=False, basic_deps=False, collapsed_deps=False, collapsed_ccproc_deps=True):
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
        
        parse_str = sentence.findall('.//parse')
        if parse:
            from nltk.tree import Tree
        self.parse = Tree(parse_str[0].text) if parse else None




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
        self.coref_chain = None

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
        
