import os
import re
import logging
from dataclasses import dataclass

from tqdm import tqdm
from textdistance import * 
from jiwer import wer as _wer

from align import Aligner, Align
from util import PhraseTuple


class ContextAligner(Aligner):

    def __init__(self, 
                 sentences: list, 
                 targets: list, 
                 min_similarity=0,
                 min_seq_similarity=0.5,
                 min_str_similarity=0.5,
                 max_wer=50,
                 prefix_postfix_length_acceptance=10,
                 prefix_postfix_sim_acceptance=0.15,
                 seq_sim_f=lcsseq.normalized_similarity,
                 str_sim_f=levenshtein.normalized_similarity,
                 alpha=0.5):
        """
        ContextAligner is a class that aligns a list of sentences to a list of targets.
        It is used to align the sentences in a document to the targets in a document.

        Parameters
        ----------
        sentences : list
            A list of sentences to align
        targets : list
            A list of targets to align to
        min_similarity : float, optional
            The minimum similarity between a sentence and a target, by default 0
        min_seq_similarity : float, optional
            The minimum sequence similarity between a sentence and a target, by default 0.5
        min_str_similarity : float, optional
            The minimum string similarity between a sentence and a target, by default 0.5
        max_wer : int, optional
            The maximum word error rate between a sentence and a target, by default 50  
        prefix_postfix_length_acceptance : int, optional
            The maximum length of the prefix and postfix of a sentence and a target, by default 10
        prefix_postfix_sim_acceptance : float, optional
            The minimum similarity of the prefix and postfix of a sentence and a target, by default 0.15
        seq_sim_f : function, optional
            The sequence similarity function to use, by default lcsseq.normalized_similarity
        str_sim_f : function, optional
            The string similarity function to use, by default levenshtein.normalized_similarity
        alpha : float, optional
            The weight of the sequence similarity function, by default 0.5
        """
        super().__init__()
        self.context = targets 
        self.sentences = self._construct_phrase_tuples(sentences)
        self.targets = self._construct_phrase_tuples(targets)
        self.min_similarity = min_similarity 
        self.min_seq_similarity = min_seq_similarity
        self.min_str_similarity = min_str_similarity 
        self.prefix_postfix_length_acceptance = prefix_postfix_length_acceptance if prefix_postfix_length_acceptance else 1000
        self.prefix_postfix_sim_acceptance = prefix_postfix_sim_acceptance if prefix_postfix_sim_acceptance else 1000
        self.seq_sim_f = seq_sim_f
        self.str_sim_f = str_sim_f
        self.max_wer = max_wer if max_wer else 1000
        self.alpha = alpha
        self._construct_preliminary_aligns()

    def wer(*args): 
        try:
            return _wer(*args)
        except:
            return 1

    def inverse_wer_score(s1, s2):
        return 1-wer(s1, s2)

    def compute_prefix_postfix_similarity(self, s1: str, s2: str):
        pre = prefix.similarity(s1, s2)
        post = postfix.similarity(s1, s2)
        return (pre+post)/2, pre, post

    def compute_normalized_prefix_postfix_similarity(self, s1: str, s2: str):
        pre = prefix.normalized_similarity(s1, s2)
        post = postfix.normalized_similarity(s1, s2)
        return (pre+post)/2, pre, post

    def compute_similarity(self, s1: str, s2: str):
        return (((self.alpha)*self.seq_sim_f(s1, s2)) + 
               ((1-self.alpha)*self.str_sim_f(s1, s2)))

    def _construct_preliminary_aligns(self):
        logging.info("Constructing preliminary alignments")
        for i, sentence in tqdm(enumerate(self.sentences)):
            _, closest, str_sim = self.find_best_candidate(sentence)
            wer = ContextAligner.wer(sentence.normalized_phrase, closest.normalized_phrase)
            if closest is not None and str_sim >= self.min_str_similarity and wer <= self.max_wer:
                sim = self.compute_similarity(sentence.normalized_phrase, closest.normalized_phrase)
                self._add_align(sentence, closest, i, sim)
        for sentence in self.sentences:
            if sentence not in [a.sentence for a in self]:
                logging.info(f"Sentence {str(sentence)[:255]} ignored from alignments because it did not "
                             f"found a closest candidate.")

    def _add_align(self,
                   sentence: PhraseTuple, 
                   target: PhraseTuple, 
                   order: int,
                   sim: float, 
                   replace_if_sim_is_better=True):
        if not sim >= self.min_similarity:
            return
        
        logging.debug(f"\t\n{target.normalized_phrase}\t\n{sentence.normalized_phrase}\t\n{sim}")
        if sentence in self._aligns:
            if replace_if_sim_is_better:
                if sim > self._aligns[sentence].sim:
                    self._aligns[sentence] = Align(order, sentence, target, sim)
            else:
                raise Exception(f"The sentence \"{sentence}\" was already aligned to "
                                f"\"{self._aligns[sentence]}\"")
        else:
            self._aligns[sentence] = Align(order, sentence, target, sim)

    def _construct_phrase_tuples(self, phrases):
        return [PhraseTuple(p, i) for i, p in enumerate(phrases)]

    def find_best_candidate(self, sentence):
        best_sim = 0
        best_candidate = None
        index = None
        for i, target in enumerate(self.targets):
            str_sim = self.str_sim_f(target.normalized_phrase, sentence.normalized_phrase)
            print(sentence, target, str_sim)
            if str_sim > best_sim:
                best_sim = str_sim
                index = i
                best_candidate = target
        return (index, best_candidate, best_sim)
    
    def _context_aligner(self, reference: PhraseTuple, context: PhraseTuple, keep_phrase: PhraseTuple=None):
        """
        This function does not change the reference, only the context.
        The context is modified to match the reference.
        Returns a PhraseTuple of the generated target.
        If keep_phrase is not None, will stop aligning when the target context match the provided phrase.
        """
        final = PhraseTuple(context.phrase, order=context.order)
        best_sim = sim = self.compute_similarity(reference.phrase, final.phrase)
        prefix_postfix_sim, prefix_sim, postfix_sim = self.compute_normalized_prefix_postfix_similarity(
            reference.normalized_phrase, final.normalized_phrase
        )
        prefix_postfix_len, prefix_len, postfix_len = self.compute_prefix_postfix_similarity(
            reference.normalized_phrase, final.normalized_phrase
        )

        temp = PhraseTuple(final.phrase, order=final.order)
        while len(temp) > 0:
            prefix_postfix_sim, prefix_sim, postfix_sim = self.compute_normalized_prefix_postfix_similarity(
                reference.normalized_phrase, final.normalized_phrase
            )
            prefix_postfix_len, prefix_len, postfix_len = self.compute_prefix_postfix_similarity(
                reference.normalized_phrase, final.normalized_phrase
            )
            logging.debug(f"reference:{reference.phrase}\nfinal:{final.phrase}\n\tsim:{sim}"
                            f"\n\tbest_sim:{best_sim}\n\tprefix_sim:{prefix_sim}\n\tpostfix_sim:{postfix_sim}")
                            
            if prefix_len > postfix_len:
                temp = temp.remove_last_word()
            else:
                temp = temp.remove_first_word()
            
            sim = self.compute_similarity(
                reference.normalized_phrase, temp.normalized_phrase
            ) 
            if sim > best_sim:
                final = temp
                best_sim = sim

        return final, best_sim

    def _create_context_window(self, reference: str, text: str, word_gap=5, remove_from_text=[]):
        for segment in remove_from_text:
            text = text.replace(segment.phrase, '')

        best_sim = 0
        best_context = text
        
        words = text.split()
        ref_size = len(reference.split())
        word_gap = min(word_gap, ref_size)
        for w in range(word_gap, len(words)-word_gap, 1):
            segment = ' '.join(words[w-word_gap:w+ref_size+word_gap])
            sim = self.compute_similarity(reference.lower(), segment.lower())
            if sim > best_sim:
                best_sim = sim
                best_context = segment

        return best_context, best_sim

    def context_aligner(self, 
                        max_iter=2, 
                        initial_k_context=1, 
                        k_context_step=2, 
                        skip_aligned=False, 
                        create_context_window=False):     
        """
        Context aligner algorithm.
        1. Find the best candidate for each sentence.
        2. Create a context window around the best candidate.
        3. Align the sentence with the context window.
        4. If the alignment is good, add it to the aligned sentences.
        5. Repeat until no more sentences can be aligned.
        6. Increase the context window size and repeat.
        7. Repeat until max_iter is reached.

        Parameters
        ----------
        max_iter : int, optional
            Maximum number of iterations, by default 2
        initial_k_context : int, optional
            Initial context window size, by default 1
        k_context_step : int, optional
            Context window size step, by default 2
        skip_aligned : bool, optional
            Skip already aligned sentences, by default False
        create_context_window : bool, optional
            Create context window around the best candidate, by default False
        """   
        aligned_sentences = set()
        i = 0
        k_context = initial_k_context
        mean_sim = None 

        for i in range(max_iter):
            mean_sim = sum([a.sim for a in self])/len(self.sentences) if len(self) > 0 else 0

            logging.info(
                f"Iteration {i+1} "
                f"Total aligned: {len(self)}/{len(sentences)} "
                f"| Mean Similarity: {mean_sim:0.4f}"
            )

            for sentence in self.sentences:
                if skip_aligned and sentence in aligned_sentences:
                    continue

                j, _bc, _sim = self.find_best_candidate(sentence)
                
                c_text = ' '.join([
                    *[t.phrase for t in self.targets[max(0, j-k_context):j]],
                    self.targets[j].phrase,
                    *[t.phrase for t in self.targets[j+1:min(len(self.targets)-1, j+k_context)]]
                ])
                if create_context_window:
                    context, c_sim = self._create_context_window(sentence.phrase, c_text)
                else:
                    context = c_text
                found_target, sim = self._context_aligner(sentence, PhraseTuple(context, j))
                seq_similarity = self.seq_sim_f(sentence.normalized_phrase, found_target.normalized_phrase)
                str_similarity = self.str_sim_f(sentence.normalized_phrase, found_target.normalized_phrase)
                wer = ContextAligner.wer(sentence.normalized_phrase, found_target.normalized_phrase)

                if (sim >= self.min_similarity and 
                    seq_similarity >= self.min_seq_similarity and 
                    str_similarity >= self.min_str_similarity and 
                    wer <= self.max_wer):
                    aligned_sentences.add(sentence)
                    self._add_align(sentence, found_target, self.sentences.index(sentence), sim)

            k_context+=k_context_step
             
        return self, mean_sim

    def __call__(self):
        self.context_aligner()
        return self


