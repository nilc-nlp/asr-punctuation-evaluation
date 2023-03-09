import os
import statistics


def get_stats_of_files(directory):
    sentences_len_words = []
    sentences_len_char = []
    sentences_len_tokens = []
    sentences_len_tokens_wp = []
    turns_len_words = []
    turns_len_char = []
    turns_len_tokens = []
    turns_len_tokens_wp = []
    for root, _, files in os.walk(directory):
        for f in files:
            if f.endswith('txt'):
                fp = os.path.join(root, f)
                with open(fp) as txt:
                    turns_len_words.append(0)
                    turns_len_char.append(0)
                    turns_len_tokens.append(0)
                    turns_len_tokens_wp.append(0)
                    for line in txt:
                        sentence = line

                        for c in [',', ';', '!', '?', '...', '.', ':']:
                            sentence = sentence.replace(c, f' {c} ')
                        tokens = sentence.rstrip().split()
                        sentences_len_tokens.append(len(tokens))
                        turns_len_tokens[-1] += len(tokens)

                        for c in [',', ';', '!', '?', '...', '.', ':']:
                            sentence = sentence.replace(c, '')
                        tokens_wp = words = sentence.rstrip().split()
                        sentences_len_tokens_wp.append(len(tokens_wp))
                        sentences_len_words.append(len(words))
                        turns_len_words[-1] += len(words)
                        turns_len_tokens_wp[-1] += len(tokens_wp)

                        len_char = len(''.join(line.rstrip().split()))
                        sentences_len_char.append(len_char)
                        turns_len_char[-1] += len_char
    
    return sentences_len_tokens, sentences_len_tokens_wp, sentences_len_words, sentences_len_char, turns_len_tokens, \
        turns_len_tokens_wp, turns_len_words, turns_len_char


if __name__ == '__main__':
    import sys
    root_dir = sys.argv[1]

    sentences_len_tokens, sentences_len_tokens_wp, sentences_len_words, sentences_len_char, turns_len_tokens, \
        turns_len_tokens_wp, turns_len_words, turns_len_char = get_stats_of_files(root_dir)
    
    print('Total sentences:', len(sentences_len_words))
    print('Total turns:', len(turns_len_words))
    print('Words:', sum(sentences_len_words))
    print('Tokens:', sum(sentences_len_tokens))
    print('Tokens (w/ punct):', sum(sentences_len_tokens_wp))
    print('Chars:', sum(sentences_len_char))
    
    print('Sentence Mean words:', sum(sentences_len_words)/len(sentences_len_words))
    print('Sentence Std words:', statistics.stdev(sentences_len_words))
    print('Sentence Mean chars:', sum(sentences_len_char)/len(sentences_len_char))
    print('Sentence Std chars:', statistics.stdev(sentences_len_char))
    print('Sentence Mean Tokens:', sum(sentences_len_tokens)/len(sentences_len_tokens))
    print('Sentence Std Tokens:', statistics.stdev(sentences_len_tokens))

    print('Turn Mean words:', sum(turns_len_words)/len(turns_len_words))
    print('Turn Std words:', statistics.stdev(turns_len_words))
    print('Turn Mean chars:', sum(turns_len_char)/len(turns_len_char))
    print('Turn Std chars:', statistics.stdev(turns_len_char))
    print('Turn Mean tokens:', sum(turns_len_tokens)/len(turns_len_tokens))
    print('Turn Std tokens:', statistics.stdev(turns_len_tokens))
    print('Turn (w/ punct) Mean tokens:', sum(turns_len_tokens_wp)/len(turns_len_tokens_wp))
    print('Turn (w/ punct) Std tokens:', statistics.stdev(turns_len_tokens_wp))
