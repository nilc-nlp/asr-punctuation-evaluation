import sys 
import os
from scipy.io import wavfile 
from pyannote.audio import Pipeline

AUTH_TOKEN = None
assert AUTH_TOKEN is not None, "Please set your HuggingFace auth token"

pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization",
                                    use_auth_token=AUTH_TOKEN)

def diarize_audio(audio_path, out_dir=None, num_speakers=None, keep_turn=False, min_sec=0.5, max_sec=None):
    sr, audio = wavfile.read(audio_path)
    diarization = pipeline(audio_path, num_speakers=num_speakers)
    
    start_frames, end_frames = None, None
    last_spk = None
    i = 0
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        spk = speaker   
        if out_dir is None:
            out_dir = spk
        os.makedirs(out_dir, exist_ok=True)

        print(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker: {spk}")
        
        if keep_turn:
            if not start_frames:
                start_frames = int(turn.start)
            if not last_spk:
                last_spk = spk
            if spk == last_spk:
                end_frames = int(sr*turn.end)
            else:
                i+=1
                if min_sec is not None and (end_frames - start_frames)/sr < min_sec:
                    print(f"skipping {turn.start:.1f}s stop={turn.end:.1f} because it is too short")
                    continue
                if max_sec is not None and (end_frames - start_frames)/sr > max_sec:
                    print(f"skipping {turn.start:.1f}s stop={turn.end:.1f} because it is too long")
                    continue
                
                wavfile.write(os.path.join(out_dir, f"{i:04}-{last_spk}.wav"), sr, audio[start_frames:end_frames])

                last_spk = spk
                start_frames = int(sr*turn.start)
                end_frames = int(sr*turn.end)
        else:
            wavfile.write(os.path.join(out_dir, f"{i:04}-{spk}.wav"), sr, audio[int(sr*turn.start):int(sr*turn.end)])
            i+=1


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser("Diarize audio file")
    parser.add_argument("audio_path", type=str, help="Path to audio file")
    parser.add_argument("--min-sec", type=float, default=0.5)
    parser.add_argument("--max-sec", type=float, default=None)
    parser.add_argument("--num_speakers", type=int, default=2, help="Number of speakers")
    args = parser.parse_args()

    diarize_audio(args.audio_path, args.out_dir, args.num_speakers, min_sec=args.min_sec, max_sec=args.max_sec, keep_turn=True)
