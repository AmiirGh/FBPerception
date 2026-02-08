import os
import json
import difflib
from vosk import Model, KaldiRecognizer
from pydub import AudioSegment

# =========================
# مسیرها
# =========================
MODEL_PATH = r"C:\Users\ghaza\Desktop\model-fa"
AUDIO_FILE = r"C:\Users\ghaza\Desktop\command.m4a"
FFMPEG_PATH = r"C:\Users\ghaza\Desktop\ffmpeg"
OUTPUT_FILE = r"C:\Users\ghaza\Desktop\output_commands2.txt"

os.environ["PATH"] += os.pathsep + FFMPEG_PATH

SAMPLE_RATE = 16000

# =========================
# مپینگ پایه
# =========================
DEGREES = {
    "یک": 1, "دو": 2, "سه": 3, "چهار": 4,
    "پنج": 5, "شش": 6, "هفت": 7, "هشت": 8
}

LEVELS = {
    "نزدیک": 1,
    "وسط": 2,
    "متوسط": 2,
    "دور": 3
}

ALL_DEGREE_KEYS = list(DEGREES.keys())
ALL_LEVEL_KEYS = list(LEVELS.keys())

# =========================
# fuzzy match
# =========================
def closest_word(word, candidates, cutoff=0.6):
    match = difflib.get_close_matches(word, candidates, n=1, cutoff=cutoff)
    return match[0] if match else None

# =========================
# بارگذاری مدل
# =========================
model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, SAMPLE_RATE)
rec.SetWords(True)

# =========================
# خواندن فایل صوتی
# =========================
audio = AudioSegment.from_file(AUDIO_FILE)
audio = audio.set_channels(1)
audio = audio.set_frame_rate(SAMPLE_RATE)
audio = audio.set_sample_width(2)

raw_audio = audio.raw_data

# =========================
# تشخیص گفتار
# =========================
results = []
for i in range(0, len(raw_audio), 4000):
    chunk = raw_audio[i:i + 4000]
    if rec.AcceptWaveform(chunk):
        results.append(json.loads(rec.Result()))
results.append(json.loads(rec.FinalResult()))

# =========================
# استخراج کلمات
# =========================
words = []
for r in results:
    if "result" in r:
        words.extend(r["result"])

# =========================
# ساخت جفت‌ها (اجباری)
# =========================
output_lines = []
used = [False] * len(words)

pair_index = 1

for i, w in enumerate(words):
    if used[i]:
        continue

    # پیدا کردن Degree
    deg_word = closest_word(w["word"], ALL_DEGREE_KEYS)
    if not deg_word:
        continue

    degree_val = DEGREES[deg_word]
    start_time = w["start"]

    # جستجوی Level بعدی (تا 3 کلمه جلوتر)
    level_val = 2  # پیش‌فرض = متوسط
    end_time = w["end"]

    for j in range(i + 1, min(i + 4, len(words))):
        lvl_word = closest_word(words[j]["word"], ALL_LEVEL_KEYS)
        if lvl_word:
            level_val = LEVELS[lvl_word]
            end_time = words[j]["end"]
            used[j] = True
            break

    used[i] = True

    pair_code = f"{degree_val}{level_val}"

    line = (
        f"{pair_index}. {pair_code} | "
        f"start: {start_time:.2f} | end: {end_time:.2f}"
    )

    output_lines.append(line)
    pair_index += 1

# =========================
# ذخیره خروجی
# =========================
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for line in output_lines:
        f.write(line + "\n")

print("✅ پردازش انجام شد")
print(f"📄 خروجی ذخیره شد در:\n{OUTPUT_FILE}")
