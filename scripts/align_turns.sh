set -e
set -x

manual_root_dir=$1
asr_root_dir=$2

IFS="|"

declare -a elems=(
  "manual.txt|transcription.txt"  # Example, replace with your own
)

min_sim=0.25
min_seq_sim=0.0
min_str_sim=0.0
max_wer=0.99
pa=15
ps=0.3
a=0.5

for elem in "${elems[@]}"; do
  read -a tuple <<< "$elem"
  echo ${tuple[0]} ${tuple[1]}

  mkdir -p "aligns_${min_sim}_${min_seq_sim}_${min_str_sim}_${max_wer}_${pa}_${ps}_${a}/${tuple[0]}"

  python aligner/main.py $manual_root_dir/${tuple[0]} $asr_root_dir/${tuple[1]} \
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
    -l INFO \
  > "aligns_${min_sim}_${min_seq_sim}_${min_str_sim}_${max_wer}_${pa}_${ps}_${a}/${tuple[0]}/out.txt" &

done
