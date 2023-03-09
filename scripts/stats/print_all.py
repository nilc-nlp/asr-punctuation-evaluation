import os
import sys
import statistics

def read_files(directory):
    for root, subfolders, files in os.walk(directory):
        for f in files:
            if f.endswith('txt'):
                fp = os.path.join(root, f)
                with open(fp) as txt:
                    for line in txt:
                        for c in [',', ';', '!', '?', '...', '.', ':']:
                            line = line.replace(c, f' {c} ')
                        line = ' '.join(line.split()).rstrip()
                        yield line.rstrip()

if __name__ == '__main__':
    for line in read_files(sys.argv[1]):
        print(line)