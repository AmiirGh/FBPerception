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
OUTPUT_FILE = r"C:\Users\ghaza\Desktop\output_commands.txt"

os.environ["PATH"] += os.pathsep + FFMPEG_PATH
SAMPLE_RATE = 16000

# =========================
# مپینگ
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

ALL_DEG = list(DEGREES.keys())
ALL_LVL = list(LEVELS.keys())

# =========================
# fuzzy helper (خیلی شُل)
# =========================
def fuzzy(word, choices, cutoff=0.45):
    m = difflib.get_close_matches(word, choices, n=1, cutoff=cutoff)
    return m[0] if m else None

# =========================
# بارگذاری مدل
# =========================
model = Model(MODEL_PATH)
rec = KaldiRecognizer(model, SAMPLE_RATE)
rec.SetWords(True)

# =========================
# آماده‌سازی صوت
# =========================
audio = AudioSegment.from_file(AUDIO_FILE)
audio = audio.set_channels(1).set_frame_rate(SAMPLE_RATE).set_sample_width(2)
raw = audio.raw_data

# =========================
# تشخیص گفتار
# =========================
results = []
for i in range(0, len(raw), 4000):
    if rec.AcceptWaveform(raw[i:i+4000]):
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
# ساخت جفت‌ها (Aggressive)
# =========================
pairs = []
last_degree = 1  # پیش‌فرض
used = [False] * len(words)

for i, w in enumerate(words):
    if used[i]:
        continue

    word = w["word"]
    start = w["start"]
    end = w["end"]

    deg_key = fuzzy(word, ALL_DEG)
    lvl_key = fuzzy(word, ALL_LVL)

    degree = None
    level = None

    if deg_key:
        degree = DEGREES[deg_key]
        last_degree = degree
    if lvl_key:
        level = LEVELS[lvl_key]

    # اگر Degree پیدا شد → دنبال Level نزدیکش بگرد
    if degree is not None:
        level = 2  # پیش‌فرض متوسط
        for j in range(i+1, len(words)):
            if words[j]["start"] - start > 2:
                break
            lk = fuzzy(words[j]["word"], ALL_LVL)
            if lk:
                level = LEVELS[lk]
                end = words[j]["end"]
                used[j] = True
                break

    # اگر فقط Level بود
    if degree is None and level is not None:
        degree = last_degree

    if degree is not None and level is not None:
        pairs.append((degree, level, start, end))
        used[i] = True

# =========================
# اگر هنوز خالی بود → حدس اجباری
# =========================
if not pairs and words:
    for w in words:
        pairs.append((last_degree, 2, w["start"], w["end"]))

# =========================
# ذخیره خروجی
# =========================
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for idx, (d, l, s, e) in enumerate(pairs, 1):
        f.write(f"{idx}. {d}{l} | start: {s:.2f} | end: {e:.2f}\n")

print("🔥 پردازش تمام شد (Aggressive Mode)")
print(f"📄 خروجی:\n{OUTPUT_FILE}")


