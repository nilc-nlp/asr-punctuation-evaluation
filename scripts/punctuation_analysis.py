if __name__ == '__main__':
    import argparse
    from sklearn.metrics import f1_score

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', "--alignment-files", nargs='+')
    parser.add_argument('-o', "--output-csv", required=True)
    args = parser.parse_args()

    total = 0
    correct = 0
    y_true = []
    y_pred = []

    summary = {
        p: {"tp": 0, "fp": 0, "fn": 0, "tn": 0, "f1": None, "f1-macro": None} 
        for p in [',', ';', '!', '?', '=', '.', ':']
    }
    with open(args.output_csv, 'w') as outfile:
        print("human", "asr", "expected", "pred", "correct", sep='|', file=outfile)
        for f in args.alignment_files:
            with open(f, 'r') as infile:
                next(infile) 
                for line in infile:
                    _, sentence, _, target, _, score, levenshtein, lcsstr, lcsseq, ratcliff_obershelp, wer = line.rstrip().split('|')
                    sentence = sentence.rstrip()  # manual
                    target = target.rstrip()  # asr
                    sentence = sentence.replace('...', '=')
                    target = target.replace('...', '=')
                    
                    if len(sentence) > 0 and len(target) > 0:
                        expected_punt = sentence[-1]   
                        pred_punct = target[-1]        
                        if pred_punct not in summary.keys(): 
                            continue
                        y_true.append(expected_punt)
                        y_pred.append(pred_punct)

                        total += 1
                        if expected_punt==pred_punct: 
                            correct += 1
                        for p in summary.keys():
                            if p == expected_punt and p==pred_punct:
                                summary[p]["tp"] += 1
                            elif p != expected_punt and p!=pred_punct:
                                summary[p]["tn"] += 1
                            elif p == expected_punt and p!=pred_punct:
                                summary[p]["fn"] += 1
                            elif p != expected_punt and p==pred_punct:
                                summary[p]["fp"] += 1

                        sentence = sentence.replace('=', '...')
                        target = target.replace('=', '...')
                        print(sentence, target, expected_punt, pred_punct, expected_punt==pred_punct, sep='|', file=outfile)

    for p in summary.keys():
        print("CLASS", p, "- TP:", summary[p]["tp"])
        print("CLASS", p, "- TN:", summary[p]["tn"])
        print("CLASS", p, "- FP:", summary[p]["fp"])
        print("CLASS", p, "- FN:", summary[p]["fn"])
        if (summary[p]["tp"] + summary[p]["fp"]) > 0:
            print("Precision:", summary[p]["tp"] / (summary[p]["tp"] + summary[p]["fp"]))
        if (summary[p]["tp"] + summary[p]["fn"]) > 0:
            print("Recall:", summary[p]["tp"] / (summary[p]["tp"] + summary[p]["fn"]))
    
    print("==========================================================================================")
    for p in [',', ';', '!', '?', '=', '.', ':']:
        y_c_true = [1 if p==y else 0 for y in y_true]
        y_c_pred = [1 if p==y else 0 for y in y_pred]
        print("CLASS", p, "- F1:", f1_score(y_c_true, y_c_pred, average='binary'))
        print("CLASS", p, "- F1 MICRO:", f1_score(y_c_true, y_c_pred, average='micro'))
        print("CLASS", p, "- F1 MACRO:", f1_score(y_c_true, y_c_pred, average='macro'))

    y_c_true = [1 if y in [',', ';', ':'] else 0 for y in y_true]
    y_c_pred = [1 if y in [',', ';', ':'] else 0 for y in y_pred]
    print("CLASS PAUSING - F1:", f1_score(y_c_true, y_c_pred, average='binary'))
    print("CLASS PAUSING - F1 MICRO:", f1_score(y_c_true, y_c_pred, average='micro'))
    print("CLASS PAUSING - F1 MACRO:", f1_score(y_c_true, y_c_pred, average='macro'))

    y_c_true = [1 if y in ['?', '!', '.'] else 0 for y in y_true]
    y_c_pred = [1 if y in ['?', '!', '.'] else 0 for y in y_pred]
    print("CLASS CI - F1:", f1_score(y_c_true, y_c_pred, average='binary'))
    print("CLASS CI - F1 MICRO:", f1_score(y_c_true, y_c_pred, average='micro'))
    print("CLASS CI - F1 MACRO:", f1_score(y_c_true, y_c_pred, average='macro'))

    print("F1:", f1_score(y_true, y_pred, average='micro'))
    print("F1 MACRO:", f1_score(y_true, y_pred, average='macro'))
    