import os
import sys
import statistics

def count_tokens_in_files(directory):
    for root, _, files in os.walk(directory):
        for f in files:
            if f.endswith('txt'):
                fp = os.path.join(root, f)
                with open(fp) as txt:
                    for line in txt:
                        line = line.replace('...', '=')
                        for c in [',', ';', '!', '?', '=', '.', ':']:
                            line = line.replace(c, f' {c} ')
                        line = ' '.join(line.split()).rstrip()
                        yield line.rstrip()

if __name__ == '__main__':
    asr_transcriptins_dir = sys.argv[1]
    manual_transcriptions_dir = sys.argv[2]

    words_count_asr = dict()
    for line in count_tokens_in_files(asr_transcriptins_dir):
        for word in line.split():
            word = word.lower()
            if word in words_count_asr:
                words_count_asr[word] += 1
            else:
                words_count_asr[word] = 1
    words_count_asr['...'] = words_count_asr['=']
    del words_count_asr['=']

    words_count_manual = dict()
    for line in count_tokens_in_files(manual_transcriptions_dir):
        for word in line.split():
            word = word.lower()
            if word in words_count_manual:
                words_count_manual[word] += 1
            else:
                words_count_manual[word] = 1
    words_count_manual['...'] = words_count_manual['=']
    del words_count_manual['=']
                
    words_count = dict()
    for word in set(words_count_asr.keys()).intersection(set(words_count_manual.keys())):
        words_count[word] = {
            'asr': words_count_asr[word],
            'manual': words_count_manual[word]
        }
    
    for word in words_count:
        if words_count[word]["asr"] > 1 and words_count[word]["manual"] > 1:
            print(f'{word}|{words_count[word]["asr"]}|{words_count[word]["manual"]}')