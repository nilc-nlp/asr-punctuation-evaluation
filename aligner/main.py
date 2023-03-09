import logging

from context_aligner import ContextAligner
from util import PhraseTuple

if __name__ == "__main__":
    import time
    import argparse
    import pandas as pd
    from tabulate import tabulate

    parser = argparse.ArgumentParser("Context aligner", help="Aligns sentences with a target text")
    parser.add_argument("sentences_file", help="File with sentences to align")
    parser.add_argument("--target-texts", required=True, nargs='+', help="Target texts to search and align with the best match")
    parser.add_argument("--output-preliminary-csv", default="preliminary_aligns.csv", help="Output file for preliminary alignments")
    parser.add_argument("--output-csv", default="final_aligns.csv", help="Output file for final alignments")
    parser.add_argument("--decimal-csv", default=',', help="Decimal separator for csv output")
    parser.add_argument('-l', "--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO")
    parser.add_argument("--min-similarity", type=float, default=0.5, help="Minimum similarity to consider a sentence aligned")
    parser.add_argument("--min-seq-similarity", type=float, default=0.5, help="Minimum sequence similarity to consider a sentence aligned")
    parser.add_argument("--min-str-similarity", type=float, default=0.5, help="Minimum string similarity to consider a sentence aligned")
    parser.add_argument("--max-wer", type=float, default=0.5, help="Maximum word error rate to consider a sentence aligned")
    parser.add_argument('-pa', "--prefix-postfix-length-acceptance", type=int, default=None, help="Acceptance of prefix and postfix length (in tokens) to consider a sentence aligned")
    parser.add_argument('-ps', "--prefix-postfix-sim-acceptance", type=float, default=None, help="Acceptance of prefix and postfix similarity (percentage) to consider a sentence aligned")
    parser.add_argument('-a', "--alpha", type=float, default=0.5, help="Alpha parameter for score calculation")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level, format='%(asctime)s - %(name)s - %(levelname)s: %(message)s')

    with open(args.sentences_file) as txt:
        sentences = [s.strip() for s in txt.readlines()]
        sentence_doc = PhraseTuple(' '.join(sentences))
        
    logging.info("Finding best text to align")
    best_sim, target_file = None, None
    for tfp in args.target_texts:
        with open(tfp) as tf:
            t_lines = [s.strip() for s in tf.readlines()]
            text = PhraseTuple(' '.join(t_lines))
            logging.info(f"\tComparing {tfp}")
            sim =  levenshtein.normalized_similarity(text.normalized_phrase, sentence_doc.normalized_phrase)
            logging.info(f"\tSim: {sim}")
            if best_sim is None:
                best_sim = sim
                targets = t_lines
            elif sim > best_sim:
                best_sim = sim
                targets = t_lines
    logging.info("Finding best text to align - Done")
    logging.debug(f" \n{sentences} \n--------------------------------------------------------- \n{targets}")
    if args.log_level == 'DEBUG':
        input("Press enter to continue...")

    aligner = ContextAligner(
        sentences, targets, 
        min_similarity=args.min_similarity,
        min_seq_similarity=args.min_seq_similarity,
        min_str_similarity=args.min_str_similarity,
        max_wer=args.max_wer,
        prefix_postfix_length_acceptance=args.prefix_postfix_length_acceptance,
        prefix_postfix_sim_acceptance=args.prefix_postfix_sim_acceptance,
        alpha=args.alpha
    )
    
    preliminary_aligns = []
    for align in aligner:
        preliminary_aligns.append({
            "order": str(align.order),
            "sentence": align.sentence.phrase,
            "norm_sentence": align.sentence.normalized_phrase,
            "target": align.target.phrase,
            "norm_target": align.target.normalized_phrase,
            "score": align.sim,
            "levenshtein": levenshtein.normalized_similarity(align.sentence.normalized_phrase, align.target.normalized_phrase),
            "lcsstr": lcsstr.normalized_similarity(align.sentence.normalized_phrase, align.target.normalized_phrase),
            "lcsseq": lcsseq.normalized_similarity(align.sentence.normalized_phrase, align.target.normalized_phrase),
            "ratcliff_obershelp": ratcliff_obershelp.normalized_similarity(align.sentence.normalized_phrase, align.target.normalized_phrase),
            "wer": ContextAligner.wer(align.sentence.normalized_phrase, align.target.normalized_phrase)
        })
    if len(preliminary_aligns) > 0:
        preliminary_aligns_pd = pd.DataFrame(preliminary_aligns)

        perc = len(aligner)/len(aligner.sentences)*100
        print(f"{'='*45} PRELIMINARY ALIGNS {'='*45}")
        print(tabulate(preliminary_aligns_pd.describe(), headers='keys', tablefmt='psql', maxcolwidths=45))
        preliminary_aligns_pd.loc["AVG"] = preliminary_aligns_pd.mean(numeric_only=True)
        preliminary_aligns_pd.to_csv(
            args.output_preliminary_csv,  
            sep='|',
            decimal=args.decimal_csv,
            index=False
        )
        print(f"ALIGNMENT DONE: {perc:.2f}%")

    if args.log_level == 'DEBUG':
        input("Press enter to continue...")

    st = time.time()
    alignments, mean_sim = aligner.context_aligner(skip_aligned=False)
    end = time.time()

    aligns = []
    for align in aligner:
        aligns.append({
            "order": str(align.order),
            "sentence": align.sentence.phrase,
            "norm_sentence": align.sentence.normalized_phrase,
            "target": align.target.phrase,
            "norm_target": align.target.normalized_phrase,
            "score": align.sim,
            "levenshtein": levenshtein.normalized_similarity(align.sentence.normalized_phrase, align.target.normalized_phrase),
            "lcsstr": lcsstr.normalized_similarity(align.sentence.normalized_phrase, align.target.normalized_phrase),
            "lcsseq": lcsseq.normalized_similarity(align.sentence.normalized_phrase, align.target.normalized_phrase),
            "ratcliff_obershelp": ratcliff_obershelp.normalized_similarity(align.sentence.normalized_phrase, align.target.normalized_phrase),
            "wer": ContextAligner.wer(align.sentence.normalized_phrase, align.target.normalized_phrase)
        })
        
    if len(aligns) > 0:
        aligns_pd = pd.DataFrame(aligns)
        print(f"{'='*45} FINAL ALIGNS {'='*45}")
        print(tabulate(aligns_pd.describe(), headers='keys', tablefmt='psql', maxcolwidths=45))
        aligns_pd.loc["AVG"] = aligns_pd.mean(numeric_only=True)
        aligns_pd.to_csv(
            args.output_csv,  
            sep='|',
            decimal=args.decimal_csv,
            index=False
        )

        perc = len(aligner)/len(aligner.sentences)*100
        print(f"TOTAL ALIGNMENT TIME: {end-st}")
        print(f"ALIGNMENT DONE: {perc:.2f}%")
