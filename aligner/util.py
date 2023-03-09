import re

from num2words import num2words 


class PhraseTuple:
    """
    A tuple of a phrase and its normalized version.
    """
    ALPHABET = "abcdefghijklmnopqrstuvwxyzçãàáâêéíóôõũúû\-\n/\\ "

    def __init__(self, phrase, order=None):
        self.order = order
        self._phrase = phrase.replace("...", '=')
        self._normalized_phrase = PhraseTuple.normalize(phrase.replace("...", '='))

    @property
    def phrase(self):
        return self._phrase.replace('=', '...')
        
    @property
    def normalized_phrase(self):
        return self._normalized_phrase.replace('=', '...')

    def contains_num(s):
        return any(i.isdigit() for i in s)
    
    def normalize(phrase):
        phrase = phrase.lower()

        new_words = []
        for word in phrase.split():
            word = re.sub("\d+[%]", lambda x: x.group()+" por cento", word)
            word = re.sub("%", "", word)
            word = re.sub("\d+[o]{1}", lambda x: num2words((x.group()
                                                            [:-1]), to='ordinal', lang='pt_BR'), word)
            ref = word
            word = re.sub("\d+[a]{1}", lambda x: num2words((x.group()
                                                            [:-1]), to='ordinal', lang='pt_BR'), word)
            if word != ref:
                segs = word.split(' ')
                word = ''
                for seg in segs:
                    word = word + seg[:-1] + 'a' + ' '
                word = word[:-1]

            if PhraseTuple.contains_num(word):
                segs = re.split("[?.!\s]", word)
                word = ''
                for seg in segs:
                    if seg.isnumeric():
                        seg = num2words(seg, lang='pt_BR')
                    word = word + seg + ' '
                word = word[:-1]
            new_words.append(word)
        
        phrase = ' '.join(new_words)

        phrase = re.sub("[^{}]".format(PhraseTuple.ALPHABET), ' ', phrase)
        phrase = re.sub('\-+', " ", phrase)
        phrase = re.sub(' +', ' ', phrase)
        phrase = phrase.strip()

        return phrase

    def __eq__(self, o: object) -> bool:
        return type(o) == PhraseTuple and o.phrase == self.phrase

    def __hash__(self):
        return hash((self.order, self.phrase, self.normalized_phrase))
    
    def __len__(self):
        return min(len(self.normalized_phrase), len(self.phrase))

    def remove_char(self, first_or_last='first', keep_last_punct=True):
        phrase = self._phrase
        if first_or_last == 'first' and len(self._phrase) >= 1:
            phrase = self._phrase[1:]
        if first_or_last == 'last' and len(self._phrase) >= 1:
            i = -1
            phrase = self._phrase[:i]
            while keep_last_punct and len(phrase) > (i*-1) and phrase[i] in ['?', '.', '.', '=']:
                i -= 1
            phrase = phrase[:i]
        return PhraseTuple(phrase, order=self.order)

    def remove_word(self, first_or_last='first'):
        tokens = self._phrase.split()
        if first_or_last == 'first' and len(tokens) >= 1:
            phrase = ' '.join(tokens[1:])
        elif first_or_last == 'last' and len(tokens) >= 1:
            phrase = ' '.join(tokens[:-1])            
        return PhraseTuple(phrase, order=self.order)

    def remove_first(self):
        return self.remove_char('first')

    def remove_last(self, keep_last_punct=True):
        return self.remove_char('last', keep_last_punct=keep_last_punct)

    def remove_first_word(self):
        return self.remove_word('first')

    def remove_last_word(self):
        return self.remove_word('last')

    def __repr__(self):
        return f"<phrase={self.phrase}, normalized_phrase={self.normalized_phrase}>"
    
    def __str__(self):
        return self.__repr__()