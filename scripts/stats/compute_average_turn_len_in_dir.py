import os
import sys
import statistics

def read_files(directory):
    turn_len = []
    for root, _, files in os.walk(directory):
        for f in files:
            if f.endswith('txt'):
                fp = os.path.join(root, f)
                with open(fp) as txt:
                    turn = []
                    for line in txt:
                        turn.append(len(line.rstrip()))
                    if len(turn) > 0:
                        turn_len.append(sum(turn))
    return turn_len

if __name__ == '__main__':
    turn_len = read_files(sys.argv[1])
    print('Total turns:', len(turn_len))
    print('Mean:', sum(turn_len)/len(turn_len))
    print('Std:', statistics.stdev(turn_len))