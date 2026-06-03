import sounddevice as sd
import pandas as pd
from scipy.io.wavfile import write
import sys
def record_audio(filename, duration, samplerate=44100, channels=1):
    print(f"Recording {filename}")
    audio_data = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=channels, dtype='int16')
    sd.wait()
    write(filename,samplerate,audio_data)
    print(f"Saved {filename}")

def read_subject_info():
    df = pd.read_excel('subject_info.xlsx')
    subject_name = df.loc[df['Subject_Info'] == 'name', 'Value'].values[0]
    subject_id = df.loc[df['Subject_Info'] == 'ID', 'Value'].values[0]
    print(subject_name, subject_id)
    return subject_name, subject_id

if __name__ == "__main__":

#____CHANGE THE FOLLOWING LINE ONLY___________#
    experiment_phase = 1
    if len(sys.argv) > 1:
        experiment_phase = int(sys.argv[1])
    else:
        experiment_phase = 10 # invalid value

    print(experiment_phase)
    subject_name, subject_id = read_subject_info()
    if experiment_phase == 1:
        duration =  72*10+10
    else: # phase 2 or 3
        duration = 72*10  # for phase 1, we need 10 more seconds so that we capture the last command
                          # 72 is for 72 intervals each 10 seconds
    if experiment_phase >= 1:
        record_audio(f"audio_{subject_name}_{subject_id}_{experiment_phase}.wav", duration=duration) # 12 minutes (each part of the experiment is 12 minute long)



