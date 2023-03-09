import os
import argparse
import librosa
import numpy as np
from scipy.io import wavfile
from tqdm import tqdm
from glob import glob


def downsample(wav_path):
    if os.path.exists(wav_path):
        wav, _ = librosa.load(wav_path, sr=args.sr)
        wav, _ = librosa.effects.trim(wav, top_db=20)
        peak = np.abs(wav).max()
        if peak > 1.0:
            wav = 0.98 * wav / peak
        save_path = wav_path.replace(args.in_dir, args.out_dir)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        wavfile.write(
            save_path,
            args.sr,
            (wav * np.iinfo(np.int16).max).astype(np.int16)
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-sr", "--sample-rate", type=int, default=16000, help="sampling rate")
    parser.add_argument("-i", "--in-dir", type=str, help="path to source dir", required=True)
    parser.add_argument("-o", "--out-dir", type=str, help="path to target dir", required=True)
    args = parser.parse_args()

    filenames = glob(f'{args.in_dir}/**/*.wav', recursive=True)
    for filename in tqdm(filenames):
        downsample(filename)
