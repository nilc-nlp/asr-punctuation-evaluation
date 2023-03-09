echo "Transcribing audio files in current directory..."
gpu=$1

for d in */ ; do 
    echo "${d}" 
    if [[ -d "${d}" ]]; then
        cd "${d}"
        CUDA_VISIBLE_DEVICES=$gpu whisper *.wav \
            --model large \
            --language pt \
            --temperature 0.15 \
            --no_speech_threshold 0.6 \
            --condition_on_previous_text True  
        cd ..
    fi
done