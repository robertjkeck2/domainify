import itertools
import json

import nltk
from nltk.corpus import brown, cmudict


class WordMaker(object):
    def __init__(self):
        self.dict = cmudict.dict()
        self.allowed_pos = [
            'JJ',
            'NN',
            'NNS',
        ]
        self.common = []
        with open('common.txt', 'r') as infile:
            words = infile.readlines()
        for word in words:
            stripped_word = str(word).rstrip('\n\r')
            self.common.append(stripped_word)

    def create_double_word(self, used):
        combos = []
        double_words = itertools.combinations(used, 2)
        for word in double_words:
            combos.append(word[0] + word[1] + '.com')
        with open('doubleword_output.json', 'w') as outfile:
            outfile.write(json.dumps(combos))
        return combos

    def search_words(self, syllables=1, starting_with=None, min_length=1):
        overlap = []
        print('Filtering parts of speech')
        allowed_words = self._filter_pos()
        print('{} words found.'.format(len(allowed_words)))
        starts_text = ''
        if starting_with:
            starts_text = 'starting with {}'.format(starting_with)
        print('Getting words with {} syllables '.format(syllables) + starts_text)
        found_words = self._get_n_syllable_words(syllables, starting_with, min_length)
        for word in found_words:
            if word in allowed_words:
                overlap.append(word)
        print('{} words found.'.format(len(overlap)))
        print('Filtering unused/rare words.')
        used = self._filter_used(overlap)
        print('{} words found.'.format(len(used)))
        with open('search_output.json', 'w') as outfile:
            outfile.write(json.dumps(used))
        return used

    def _filter_pos(self):
        try:
            with open('filtered_pos.json', 'r') as infile:
                allowed = json.load(infile)
        except Exception as err:
            allowed = []
            for word in self.dict:
                tokenized = nltk.word_tokenize(word)
                tagged = nltk.pos_tag(tokenized)
                if tagged[0][1] in self.allowed_pos:
                    allowed.append(word)
            with open('filtered_pos.json', 'w') as outfile:
                outfile.write(json.dumps(allowed))
        return allowed

    def _filter_used(self, found):
        used = []
        for word in found:
            if word in self.common:
                used.append(word)
        return used

    def _get_n_syllable_words(self, n=1, starting_with=None, min_length=1):
        found = []
        for word in self.dict:
            is_match = False
            syllables = [len(list(y for y in x if y[-1].isdigit())) for x in self.dict[word.lower()]]
            if syllables[0] == n:
                is_match = True
            if starting_with and starting_with != word[0]:
                is_match = False
            if len(word) < min_length:
                is_match = False
            if is_match:
                found.append(word)
        return found

if __name__ == '__main__':
    maker = WordMaker()
    used = maker.search_words(syllables=4, min_length=3)
    maker.create_double_word(used)
