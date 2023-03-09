import sys
import os

# recursively read all files in a directory
def read_files(directory):
    for root, subfolders, files in os.walk(directory):
        for f in files:
            if f.endswith('txt'):
                fp = os.path.join(root, f)
                with open(fp) as txt:
                    for line in txt:
                        yield line.rstrip()

if __name__ == '__main__':
    input_dir = sys.argv[1]  # directory with text files
    
    total = 0    
    punctuation = {p: 0 for p in [',', ';', '!', '?', '=', '.', ':']}
    for line in read_files(input_dir):
        line = line.replace('...', '=')
        for c in line:
            if c in [',', ';', '!', '?', '=', '.', ':']:
                punctuation[c] += 1
    print(punctuation)