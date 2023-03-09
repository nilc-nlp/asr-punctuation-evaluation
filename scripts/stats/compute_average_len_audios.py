import statistics as stat
import soundfile as sf
import sys 
import os

root_dir = sys.argv[1]

durations = []

for root, subfolders, files in os.walk(root_dir):
    for f in os.listdir(root):
        if f.endswith('wav'):
            fp =os.path.join(root,f)
            a = sf.SoundFile(fp)
            d = a.frames / a.samplerate
            print(d)
            durations.append(d)

print('Mean:', sum(durations)/len(durations))
print(stat.stdev(durations))
