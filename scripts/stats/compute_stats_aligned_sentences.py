import statistics as stat
import sys 

sentences = []
with open(sys.argv[1]) as f:
    next(f)
    for line in f:
        sentence = line.rstrip().split('|')[1]
        sentences.append(len(sentence))

print('Mean:', sum(sentences)/len(sentences))
print(stat.stdev(sentences))
