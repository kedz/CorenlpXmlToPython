from collections import defaultdict
from math import log
import numpy as np

class Corpus:
    def __init__(self, docs):
    
        self.docs = docs
        self._wc_map = []
        self._tot_wc = []
        self._df = defaultdict(int)
        self.vocab = set()
        self.ndocs = len(docs)
        self._vectors = None
        
        for doc in docs:
            tot_wc, wc_map = count_words(doc)
            self._wc_map.append(wc_map)
            self._tot_wc.append(tot_wc)
            
        for wc_map in self._wc_map:
            for k in wc_map.keys():
                self._df[k] += 1
                self.vocab.add(k)

    def tf(self, w, doc_index, normalized=True):
            freq = self._wc_map[doc_index][w]
            if normalized:
                freq /= float(self._tot_wc[doc_index])
            return freq
    def idf(self, w):
        return log(self.ndocs) - log(self._df[w])

    def tfidf(self, w, doc_index, normalized=True):
        return self.tf(w, doc_index, normalized=normalized) * self.idf(w)


    def vectors(self):
        if not self._vectors:
            nwords = len(self.vocab)
            svocab = sorted(list(self.vocab))
            data = np.zeros([self.ndocs, nwords])
             
            for doc_index, doc in enumerate(self.docs):
                for word_index, w in enumerate(svocab):
                    data[doc_index, word_index] = self.tfidf(w, doc_index)
            self._vectors = data            

        return self._vectors

            
def count_words(doc):
    tot_wc = 0
    wc_map = defaultdict(int)    
    for s in doc:
        for w in s:
            wc_map[w.lem.lower()] += 1
            tot_wc += 1
    return (tot_wc, wc_map)

 
