if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', "--files", nargs='+')
    files = parser.parse_args().files

    align_done_percs = []
    for f in files:
        with open(f, 'r') as infile:
            for line in infile:
                if 'ALIGNMENT DONE: ' in line:
                     align_done_percs.append(float(line.split('ALIGNMENT DONE: ')[-1].split('%')[0]))
    print(sum(align_done_percs)/len(align_done_percs))