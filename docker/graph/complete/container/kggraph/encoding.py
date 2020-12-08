import boto3
import numpy as np
import json
import re
import sys
print("sys path is {}".format(sys.path))
from fastHan import FastHan
import marisa_trie
s3client = boto3.client('s3')
Bucket = 'autorec'

class Vocab:
    def __init__(self, vocab_file = None):
        self.token_to_idx = {}
        if vocab_file == None:
            s3client.download_file(Bucket, 'vocab.json', 'vocab.json')
            vocab_file = 'vocab.json'
        self.idx_to_token = ['<unk>'] + json.load(open(vocab_file,'r'))
        for i, token in enumerate(self.idx_to_token):
            self.token_to_idx[token] = i
        self.unk = 0
    def __len__(self):
        return len(self.idx_to_token)

    def __getitem__(self, tokens):
        if not isinstance(tokens, (list, tuple)):
            return self.token_to_idx.get(tokens, self.unk)
        return [self.__getitem__(token) for token in tokens]

    def to_tokens(self, indices):
        if not isinstance(indices, (list, tuple)):
            return self.idx_to_token[indices]
        return [self.idx_to_token[index] for index in indices]
    
class encoding:
    def __init__(self, kg):
        self.kg = kg
        self.trie = marisa_trie.Trie(list(kg.entity_industry))
        self.vocab = Vocab()
        self.model=FastHan()
    def __getitem__(self, text):
        seg, ner_gen, ner_indu = self.word_parser(text)
        return self.get_encoding(seg, ner_gen, ner_indu)
    def word_parser(self, text):
        seg = [str(word).strip() for word in self.model(text)[0] if len(str(word).strip())!=0]
        ner_pre = self.model(text, target="NER")[0]
        ner_gen = []
        word_pos = [0]
        for word in seg:
            word_pos.append(len(word) + word_pos[-1])
        for n in ner_pre:
            for j in re.finditer(str(n), ''.join(seg)):
                start, end = None, None
                for i in range(len(word_pos)-1):
                    if j.span()[0] == word_pos[i]:
                        start = i
                    if j.span()[1] == word_pos[i+1]:
                        end = i+1
                if start!=None and end != None:
                    ner_gen.append((start, end))
        ner_indu = self.get_industry_entities(seg)
        return seg, ner_gen, ner_indu
    def get_industry_entities(self, sentence):
        entities = []
        i = 0
        while i < len(sentence):
            for j in range(i+1, len(sentence)+1):
                keyword_prefix = self.trie.keys(''.join(sentence[i:j]))
                if len(keyword_prefix) == 0:
                    if ''.join(sentence[i:j-1]) in self.trie:
                        entities.append((i, j-1))
                    if j-1 == i:
                        i = j
                    else:
                        i = j-1
                    break
                if j == len(sentence):
                    if ''.join(sentence[i:j]) in self.trie:
                        entities.append((i, j))
                    i = j
                    break
        return entities
    def get_encoding(self, seg, ner_gen, ner_indu):
        max_len = 16
        word_encoding = self.vocab[seg]
        word_encoding = word_encoding[:max_len] + [0] * (max_len - len(word_encoding))
        # 精确匹配到的行业实体
        entity_encoding = [0] * max_len

        for n in ner_indu:
            n_s = ''
            for _ in range(n[0], n[1]):
                n_s += seg[_]
            e_id = self.kg.entity_to_idx[n_s]
            for _ in range(n[0], n[1]):
                if _ < max_len:
                    entity_encoding[_] = e_id

        # NER模型得到的实体            
        flag = [0] * max_len
        for n in ner_gen:
            n_s = ''
            for _ in range(n[0], n[1]):
                n_s += seg[_]
            if n_s in self.kg.entity_to_idx:
                e_id = self.kg.entity_to_idx[n_s]
                for _ in range(n[0], n[1]):
                    if _ < max_len:
                        flag[_] = e_id

        # 合并两种不同方法获取到的实体
        for j in range(len(entity_encoding)):
            if entity_encoding[j] == 0 and flag[j] != 0:
                entity_encoding[j] = flag[j]

        return word_encoding, entity_encoding