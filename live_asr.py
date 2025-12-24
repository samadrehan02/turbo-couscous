import os
os.environ["CUDA_VISIBLE_DEVICES"] = ""
from client import execute_sql

import sounddevice as sd
import numpy as np
import torch
from faster_whisper import WhisperModel
import queue
import requests
from df.enhance import enhance, init_df

torch.set_num_threads(1)

NL_SQL_ENDPOINT = "http://192.168.137.1:9000/generate_sql"
NL_SQL_ROLE = "admin"

def on_final_transcript(text: str):
    text = text.strip()
    if not text:
        return

    print("\n[VOICE QUERY]")
    print(text)

    try:
        r = requests.post(
            NL_SQL_ENDPOINT,
            json={
                "question": text,
                "role": NL_SQL_ROLE
            },
            timeout=10
        )
        r.raise_for_status()
        data = r.json()

        if data.get("intent") != "sql":
            print("\n[NL→SQL RESPONSE]")
            print(data)
            return

        sql = data["sql"]

        print("\n[SQL]")
        print(sql)

        rows = execute_sql(sql)

        print("\n[RESULTS]")
        if not rows:
            print("(no rows)")
        else:
            for row in rows:
                print(row)

    except Exception as e:
        print("\n[ERROR]")
        print(e)


SAMPLE_RATE = 16000
BLOCK_DURATION = 0.03

MODEL_SIZE = "large-v3"

MIN_SPEECH_SEC = 0.5
MAX_SPEECH_SEC = 30.0

MIN_AVG_LOGPROB = -0.6
MAX_NO_SPEECH_PROB = 0.6

VAD_WINDOW_SEC = 0.4
SILENCE_END_SEC = 0.6

MAX_SAMPLES = int(SAMPLE_RATE * MAX_SPEECH_SEC)

sd.default.samplerate = SAMPLE_RATE
sd.default.channels = 1
sd.default.device = (1, None)

audio_q = queue.Queue(maxsize=30)

whisper = WhisperModel(
    MODEL_SIZE,
    device="cuda",
    compute_type="float16"
)

df_model, df_state, _ = init_df()

vad_model, utils = torch.hub.load(
    "snakers4/silero-vad",
    "silero_vad",
    trust_repo=True
)
(get_speech_timestamps, _, _, _, _) = utils


def audio_callback(indata, frames, time_info, status):
    if status:
        print(status)

    raw = indata.copy().flatten().astype(np.float32)

    try:
        audio_q.put_nowait(raw)
    except queue.Full:
        pass


def is_confident_segment(seg) -> bool:
    if seg.avg_logprob < MIN_AVG_LOGPROB:
        return False
    if seg.no_speech_prob > MAX_NO_SPEECH_PROB:
        return False
    return True


buffer = np.zeros(0, dtype=np.float32)
vad_buffer = np.zeros(0, dtype=np.float32)

was_speaking = False
silence_samples = 0

print("Speak now...")

with sd.InputStream(
    callback=audio_callback,
    blocksize=int(SAMPLE_RATE * BLOCK_DURATION),
):
    while True:
        raw = audio_q.get()

        audio_t = torch.from_numpy(raw).unsqueeze(0)
        with torch.no_grad():
            denoised_t = enhance(df_model, df_state, audio_t)

        audio_vad = denoised_t.squeeze(0).numpy()
        audio_raw = raw

        volume = np.max(np.abs(audio_raw))
        print(f"\rMic level: {volume:.3f}", end="")

        vad_buffer = np.concatenate([vad_buffer, audio_vad])
        max_vad_len = int(SAMPLE_RATE * VAD_WINDOW_SEC)
        if len(vad_buffer) > max_vad_len:
            vad_buffer = vad_buffer[-max_vad_len:]

        speech = get_speech_timestamps(
            torch.from_numpy(vad_buffer),
            vad_model,
            sampling_rate=SAMPLE_RATE,
            threshold=0.2
        )

        if speech:
            buffer = np.concatenate([buffer, audio_raw])
            was_speaking = True
            silence_samples = 0

            if len(buffer) >= MAX_SAMPLES:
                segments, _ = whisper.transcribe(
                    buffer,
                    beam_size=5,
                    condition_on_previous_text=False,
                    temperature=0.0,
                    no_speech_threshold=0.6,
                )

                texts = [
                    seg.text for seg in segments
                    if is_confident_segment(seg)
                ]

                if texts:
                    on_final_transcript(" ".join(texts))
                else:
                    print("\n[discarded low-confidence audio]")

                buffer = np.zeros(0, dtype=np.float32)
                was_speaking = False

        else:
            if not was_speaking:
                continue

            silence_samples += len(audio_raw)

            if silence_samples < SAMPLE_RATE * SILENCE_END_SEC:
                continue

            was_speaking = False
            silence_samples = 0

            if len(buffer) < SAMPLE_RATE * MIN_SPEECH_SEC:
                buffer = np.zeros(0, dtype=np.float32)
                continue

            segments, _ = whisper.transcribe(
                buffer,
                beam_size=5,
                condition_on_previous_text=False,
                temperature=0.0,
                no_speech_threshold=0.6,
            )

            texts = [
                seg.text for seg in segments
                if is_confident_segment(seg)
            ]

            if texts:
                on_final_transcript(" ".join(texts))
            else:
                print("\n[discarded low-confidence audio]")

            buffer = np.zeros(0, dtype=np.float32)
