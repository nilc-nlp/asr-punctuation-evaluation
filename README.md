# ASR Punctuation Evaluation

Paper: coming soon.

This repository contains the code for ASR punctuation evaluation on non aligned texts. 

In this repository, we provide the code for the evaluation of the punctuation of the Whisper ASR output of portuguese audios (MuPe samples). We provide the links of the videos below for reproduction. The code is created to process the MuPe dataset, but can be easily adapted to other datasets with minor changes.

## Data Preparation for Punctuation Analysis

For punctuation analysis, we processed the automatic transcription and aligned it with the original samples of MuPe, our reference dataset. We chose to diarize the original audios to further improve the quality of the alignment process as we can work with smaller segments of audio. After the diarization, we generate the automatic transcription using the Whisper ASR. 

We also performed other preprocessing steps in both original and automatic transcription texts, creating a list of segments in which each segment ends with a punctuation. We chose to do this preprocessing to improve the robustness of the aligner and also to facilitate the punctuation analysis, since all segments end with a punctuation, which can be used to compare whether the automatically and manually generated punctuation match. After the preprocessing step, we performed the alignment.

### Steps to prepare the data for punctuation analysis

1. Download the MuPe samples (videos.txt), and convert the audios to 16khz mono wav files. The manual transcriptions will be made available soon.

2. Diarize the audios using diarize.py script.

3. Trancribe the audios. We provide a script to run the Whisper ASR in the scripts folder. You can also use any other ASR of your choice. Whisper can be easily installed using the instructions in the following link: https://github.com/openai/whisper. We provide an example of the script in the scripts folder (run_whisper.sh).

4. Preprocess the manual and asr transcriptions using the scripts preprocess_manual.py and preprocess_asr.py in the scripts folder. For punctuation analysis, we recommend split the sentences in segments that end with any punctuation. To compute statistics for the whole sentence, you can split the sentences in segments that end with some complete idea punctuation (. ? ! and ...).

5. Run the aligner with aligner/main.py. We provide an example in the scripts folder (align_sentences.sh).

```bash
  python aligner/main.py reference.txt asr_transcriptions.txt \
    --output-preliminary-csv "aligns_${min_sim}_${min_seq_sim}_${min_str_sim}_${max_wer}_${pa}_${ps}_${a}/${tuple[0]}/prel.csv" \
    --output-csv "aligns_${min_sim}_${min_seq_sim}_${min_str_sim}_${max_wer}_${pa}_${ps}_${a}/${tuple[0]}/final.csv" \
    --decimal-csv , \
    --min-similarity ${min_sim} \
    --min-seq-similarity ${min_seq_sim} \
    --min-str-similarity ${min_str_sim} \
    --max-wer ${max_wer} \
    -pa ${pa} \
    -ps ${ps} \
    -a ${a} \
    -l INFO 
```

Obs: we replaced the punctuation mark ... with = in all scripts to avoid confusions with the . punctuation mark.

### Run the punctuation analysis

After the alignment, we can run the punctuation analysis and compute the statistics. The punctuation analysis is performed using the script punctuation_analysis.py in the scripts folder by providing the directory path to the aligned files.

## Links of the videos

```
https://www.youtube.com/watch?v=C7vg-vfdGxo
https://www.youtube.com/watch?v=cxPEBWsVxLc
https://www.youtube.com/watch?v=nCPO__rTdnM
https://www.youtube.com/watch?v=w3EyLFJaII8
https://www.youtube.com/watch?v=Z0IQv9BDfSE
https://www.youtube.com/watch?v=zbiXSNOIafs
https://www.youtube.com/watch?v=8aSgYKEuiUI
https://www.youtube.com/watch?v=EAcPf_JhR_4
https://www.youtube.com/watch?v=Gze7DS6HQeU
https://www.youtube.com/watch?v=1bdU86705yw
```

## Acknowledgements

This work is part of a Technology Transfer Agreement among Museum of Person (MuPe), Instituto de Ciências Matemáticas e de Computação da Universidade de São Paulo (ICMC/USP) and Federal University of Goiás. This
work was carried out at the Center for Artificial Intelligence (C4AI-USP), with support by the São Paulo Research Foundation (FAPESP grant #2019/07665-4) and by the IBM Corporation. We also thank the support of the Centro de Excelência em Inteligência Artificial (CEIA) funded by the Goiás State Foundation (FAPEG grant #201910267000527). This project was also supported by the Ministry of Science, Technology and Innovation, with resources of Law No. 8.248, of October 23, 1991, within the scope of PPI-SOFTEX, coordinated by Softex and published Residence in TIC 13, DOU 01245.010222/2022-44.
