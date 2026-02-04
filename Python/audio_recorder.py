import sounddevice as sd
import pandas as pd
from scipy.io.wavfile import write
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
    experiment_phase = 1
    subject_name, subject_id = read_subject_info()
    record_audio(f"audio_{subject_name}_{subject_id}_{experiment_phase}.wav", duration=5) # 12 minutes (each part of the experiment is 12 minute long)



