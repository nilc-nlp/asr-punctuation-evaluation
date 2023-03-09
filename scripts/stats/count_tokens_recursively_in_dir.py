import os
import sys


def read_text_files(directory, separate_punctuation=True):
    for root, _, files in os.walk(directory):
        for f in files:
            if f.endswith('txt'):
                fp = os.path.join(root, f)
                with open(fp) as txt:
                    for line in txt:
                        line = line.replace('...', '=')
                        if separate_punctuation:
                            for c in [',', ';', '!', '?', '=', '.', ':']:
                                line = line.replace(c, f' {c} ')
                        line = ' '.join(line.split()).rstrip()
                        yield line.rstrip()

if __name__ == '__main__':
    tokens_count = dict()
    for line in read_text_files(sys.argv[1]):
        for token in line.split():
            token = token.lower()
            if token in tokens_count:
                tokens_count[token] += 1
            else:
                tokens_count[token] = 1
    
    tokens_count['...'] = tokens_count['=']
    del tokens_count['=']

    # sort dict by value
    tokens_count = {k: v for k, v in sorted(tokens_count.items(), key=lambda item: item[1], reverse=True)}
    for token, count in tokens_count.items():
        print(f'{token}|{count}')
