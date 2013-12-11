import xml.etree.ElementTree as ET
from os.path import exists
from collections import defaultdict

class Document:
    def __init__(self, fname_or_string, coref=False, parse=False, basic_deps=False, collapsed_deps=False, collapsed_ccproc_deps=True):
        self.fname = None
        self.sentences = []
        self.coref = []
        self._rep_str = None

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

    def __getitem__(self, index):
        return self.sentences[index]

    def __iter__(self):
        return iter(self.sentences)

    def __len__(self):
        return len(self.sentences)
    
    def __nonzero__(self):
        return True                        

    def __str__(self):
        if self._rep_str:
            return self._rep_str
        else:
            buf = ''
            for s in self:
                buf += str(s) + '\n' 
            self._rep_str = buf
            return self._rep_str

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
        
        self._dep_graph = None

        tokens = sentence.findall('.//token')
        for token in tokens:
            word = None
            char_offset_start = None
            char_offset_end = None
            pos = None
            lem = None
            ne = None
            for child in token:
                if child.tag == 'word':
                    word = child.text
                elif child.tag == 'CharacterOffsetBegin':
                    char_offset_start = int(child.text)
                elif child.tag == 'CharacterOffsetEnd':
                    char_offset_end = int(child.text)
                elif child.tag == 'POS':
                    pos = child.text
                elif child.tag == 'lemma':
                    lem = child.text
                elif child.tag == 'NER':
                    ne = child.text    
            self.tokens.append(Token(word,
                                     char_offset_start,
                                     char_offset_end,
                                     pos,
                                     lem,
                                     ne))
        
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
    

    def get_dependency_graph(self):        
        if self._dep_graph:
            return self._dep_graph
        else:
            self._dep_graph = DependencyGraph(self.deps)
            return self._dep_graph

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
    def __str__(self):
        return self.space_sep_str()        
                
class Token:
    def __init__(self,
                 word,
                 char_offset_start=None,
                 char_offset_end=None,
                 pos=None,
                 lem=None,
                 ne = None):
        self.word = word.encode('utf-8')
        self.char_offset_start = char_offset_start
        self.char_offset_end = char_offset_end
        self.pos = pos
        self.lem = lem.encode('utf-8')
        self.ne = ne
        self.coref_chain = None
        self.deps = []

    def __str__(self):
        return self.word

class Dependency:
    def __init__(self, dtype, gov_idx, dep_idx, sentence):
        self.type = dtype
        self.gov_idx = gov_idx
        self.dep_idx = dep_idx
        if dtype == 'root':
            self.gov = Token('ROOT', lem='root')
        else:
            self.gov = sentence.tokens[gov_idx]
        self.dep = sentence.tokens[dep_idx]
        self.gov.deps.append(self)
        
        self._resolve_cycle()

    def _resolve_cycle(self):        
        #for sibling in self.gov.deps:
        for child in self.dep.deps:
            if child.dep_idx == self.gov_idx:
                if 'conj' in child.type:
                    self.dep.deps.remove(child)      
    #def iterate_filtered_arcs(self, good_types):
    
    def __iter__(self):
        yield self
        token = self.dep
        for dep in sorted(token.deps, key=lambda d: d.dep_idx):
            for child in dep:
                yield child    

    def filter_iterator(self, filter_func):
        for rel in self:
            if filter_func(rel):
                yield rel 

    def __str__(self):
        return '({}:{} <- {} -- {}:{})'.format(self.dep_idx, self.dep, self.type, self.gov_idx, self.gov) 

class DependencyGraph:
    def __init__(self, deps):
        self._type = defaultdict(list)
        self._list = deps
        self.root = None 
        for dep in deps:
            if dep.type == 'root':
                self.root = dep
            self._type[dep.type].append(dep)
    #    self._build_graph(self.root)
    
    def __getitem__(self, index):
        return self._type[index]    

    def __iter__(self):
        if self.root:
            return iter(self.root)
        else:
            return iter([])

    def filter_iterator(self, filter_func):
        if self.root:
            for rel in self.root.filter_iterator(filter_func):
                yield rel
    
    def to_ipython(self):
        import pygraphviz as pgv
        G=pgv.AGraph()
        
        for dep in self._list:
            G.add_edge('{}: {}'.format(dep.gov_idx, dep.gov), '{}: {}'.format(dep.dep_idx, dep.dep), label=dep.type)

        G.layout(prog='dot')
        G.draw('/tmp/deptree.png')
        from IPython.display import Image
        return Image(filename='/tmp/deptree.png')
           
    
    #def _build_graph(self, dep):
    #    token = dep.dep
     #   for      
