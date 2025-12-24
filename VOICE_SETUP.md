# Voice Feature Setup Guide

## Prerequisites

### 1. GPU Setup (Recommended)

**Check CUDA availability:**
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

If `False`, install CUDA-compatible PyTorch:
```bash
pip install torch==2.1.0+cu118 torchaudio==2.1.0+cu118 --index-url https://download.pytorch.org/whl/cu118
```

**For CPU-only (slower):**
Edit `live_asr.py`:
```python
whisper = WhisperModel(
    MODEL_SIZE,
    device="cpu",
    compute_type="int8"  # Change from float16
)
```

### 2. Microphone Setup

**List available devices:**
```bash
python -c "import sounddevice as sd; print(sd.query_devices())"
```

**Output example:**
```
0 Built-in Microphone (default)
1 USB Audio Device
2 Virtual Audio Cable
```

**Set your device in `live_asr.py`:**
```python
sd.default.device = (1, None)  # Use device 1
```

### 3. Install Voice Dependencies

```bash
pip install -r requirements_v2.txt
```

**For ARM/M1 Mac:**
```bash
# Install Homebrew dependencies first
brew install portaudio

# Then install Python packages
pip install sounddevice faster-whisper deepfilternet
```

## Testing Components

### Test 1: Microphone Input
```python
import sounddevice as sd
import numpy as np

def test_mic():
    print("Recording 3 seconds...")
    audio = sd.rec(int(3 * 16000), samplerate=16000, channels=1)
    sd.wait()
    print(f"Captured {len(audio)} samples")
    print(f"Max volume: {np.max(np.abs(audio)):.3f}")

test_mic()
```

### Test 2: Faster Whisper
```python
from faster_whisper import WhisperModel

model = WhisperModel("base", device="cpu")
segments, info = model.transcribe("test_audio.wav")

for seg in segments:
    print(f"[{seg.start:.2f}s - {seg.end:.2f}s] {seg.text}")
```

### Test 3: Silero VAD
```python
import torch

model, utils = torch.hub.load("snakers4/silero-vad", "silero-vad", trust_repo=True)
get_speech_timestamps, _, _, _, _ = utils

audio = torch.randn(1, 16000)  # 1 second of random audio
speech = get_speech_timestamps(audio, model, sampling_rate=16000)
print(f"Speech segments: {speech}")
```

## Running Voice Mode

### Option 1: Standalone Voice Client
```bash
python live_asr.py
```

**Expected output:**
```
Speak now...
Mic level: 0.142

[VOICE QUERY]
show me customers from india

[SQL]
SELECT Customers.customer_id, Customers.first_name, Customers.last_name 
FROM Customers WHERE Customers.country = 'India';

[RESULTS]
{'customer_id': 1, 'first_name': 'Aarav', 'last_name': 'Sharma'}
{'customer_id': 22, 'first_name': 'Priya', 'last_name': 'Iyer'}
...
```

### Option 2: Web UI with Voice
1. Start server: `python server_ollama.py`
2. Open `http://127.0.0.1:9000`
3. Click microphone icon
4. Allow browser microphone access
5. Speak your query

## Configuration Tuning

### For Noisy Environments
```python
# Increase VAD threshold
threshold=0.3  # Default: 0.2

# Require longer speech
MIN_SPEECH_SEC = 1.0  # Default: 0.5
```

### For Faster Response
```python
# Use smaller model
MODEL_SIZE = "base"  # Default: large-v3

# Reduce beam size
beam_size=1  # Default: 5
```

### For Better Accuracy
```python
# Stricter confidence filtering
MIN_AVG_LOGPROB = -0.4  # Default: -0.6
MAX_NO_SPEECH_PROB = 0.4  # Default: 0.6
```

## Troubleshooting

### Issue: "CUDA out of memory"
**Solution:** Use smaller model or CPU mode:
```python
MODEL_SIZE = "medium"  # or "base"
device="cpu"
```

### Issue: Microphone not detected
**Solution:** Check permissions and device index:
```bash
# Linux
sudo usermod -a -G audio $USER

# macOS
System Preferences → Security & Privacy → Microphone

# Windows
Settings → Privacy → Microphone
```

### Issue: Poor transcription quality
**Solution:** Check audio quality:
```python
# Add this in live_asr.py to save audio
import wave
with wave.open('debug.wav', 'wb') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(16000)
    wf.writeframes((buffer * 32767).astype(np.int16).tobytes())
```

Listen to `debug.wav` to verify audio quality.

### Issue: Slow transcription
**Solution:** Profile your setup:
```python
import time

start = time.time()
segments, _ = whisper.transcribe(buffer)
print(f"Transcription took: {time.time() - start:.2f}s")
```

- CPU: 5-10 seconds (expected)
- GPU: 1-2 seconds (expected)

## ngrok Public Deployment

### 1. Install ngrok
```bash
# Download from https://ngrok.com/download
# Or use snap (Linux)
sudo snap install ngrok

# Or homebrew (Mac)
brew install ngrok
```

### 2. Authenticate
```bash
ngrok config add-authtoken YOUR_TOKEN
```

Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken

### 3. Start Tunnel
```bash
ngrok http 9000
```

**Output:**
```
Forwarding  https://abc123.ngrok.io -> http://localhost:9000
```

### 4. Update Endpoint
In `live_asr.py`, change:
```python
NL_SQL_ENDPOINT = "https://abc123.ngrok.io/generate_sql"
```

### 5. Share URL
Send `https://abc123.ngrok.io` to others for remote access.

**Security Note:** Anyone with the URL can access your app. Use ngrok's authentication features for production.

## Production Recommendations

### 1. Use Redis for Sessions
```python
import redis
SESSION_MEMORY = redis.Redis(host='localhost', port=6379, decode_responses=True)
```

### 2. Add Authentication
```python
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/generate_sql")
async def generate_sql(q: Query, token: str = Depends(security)):
    # Verify token
    pass
```

### 3. Rate Limiting
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/generate_sql")
@limiter.limit("10/minute")
async def generate_sql(request: Request, q: Query):
    pass
```

### 4. Monitor Performance
```python
import logging

logging.basicConfig(
    filename="voice_metrics.log",
    format="%(asctime)s - Transcription: %(duration)s - SQL: %(sql_time)s"
)
```

## Performance Benchmarks

| Component | CPU (i7) | GPU (RTX 3060) |
|-----------|----------|----------------|
| Faster Whisper (large-v3) | 8-12s | 1-2s |
| Silero VAD | <10ms | <5ms |
| DeepFilterNet | 30-50ms | 10-15ms |
| SQL Generation | 2-5s | 2-5s |
| **Total (voice → result)** | ~15-20s | ~5-8s |

## Resources

- [Faster Whisper Docs](https://github.com/SYSTRAN/faster-whisper)
- [Silero VAD Tutorial](https://github.com/snakers4/silero-vad)
- [DeepFilterNet Paper](https://github.com/Rikorose/DeepFilterNet)
- [ngrok Documentation](https://ngrok.com/docs)
