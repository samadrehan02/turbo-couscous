
# Create updated README with voice features
readme_v2 = """# 🎤 Voice-Enabled Text-to-SQL Assistant

A production-grade FastAPI application that converts **natural language questions into SQL queries** using local LLMs via Ollama. Now featuring **real-time voice input** powered by Faster Whisper ASR, web UI, and ngrok deployment for public access.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)
![Whisper](https://img.shields.io/badge/Whisper-large--v3-orange)

## 🌟 Features

### Core Capabilities
- **Natural Language to SQL**: Convert questions like "Show me customers from India" into executable SQL
- **🎙️ Real-Time Voice Input**: Speak your queries using Faster Whisper with VAD and denoising
- **🌐 Web UI**: Modern HTML/CSS interface with voice recording
- **🚀 Public Access**: Deploy with ngrok for remote access
- **Role-Based Access Control**: Three-tier access (Admin, Sales, Ops) with schema filtering
- **Multi-Schema Support**: Separate schemas for Commerce (Customers, Orders, Shippings) and HR (Employees, Departments)
- **Database Integration**: SQLite database with query execution and result display
- **Session Management**: Cookie-based sessions with 15-minute TTL and conversation history
- **Intelligent Intent Detection**: Routes queries to SQL generation, chat, or explanation modes
- **Fuzzy Matching**: Handles typos and synonyms using rapidfuzz
- **Validation & Auto-fixing**: Multi-layer SQL validation with automatic error correction
- **Retry Mechanism**: Feedback loop sends validation errors back to LLM for correction

### Voice Processing Pipeline
- **Faster Whisper large-v3**: High-accuracy speech recognition
- **Silero VAD**: Voice activity detection to filter silence
- **DeepFilterNet**: Audio denoising for clear transcription
- **Real-time Processing**: 30ms audio blocks with streaming transcription

## 📊 Architecture

The system now includes a complete voice-to-SQL pipeline with web interface and public deployment capabilities.

### Voice Processing Flow

```
Microphone Input
    ↓
Audio Capture (sounddevice)
    ↓
DeepFilterNet Denoising
    ↓
Silero VAD (Voice Detection)
    ↓
Faster Whisper Transcription
    ↓
Text-to-SQL API
    ↓
SQL Execution
    ↓
Results Display
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running
- Llama model downloaded (e.g., `dolphin3:8b`)
- CUDA-compatible GPU (recommended for voice features)
- Microphone access

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/voice-sql-assistant.git
cd voice-sql-assistant
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up database**
```bash
sqlite3 database.sqlite < setup.sql
```

4. **Start Ollama server**
```bash
ollama serve
ollama pull dolphin3:8b
```

5. **Run the application**
```bash
python server_ollama.py
```

The server will start at `http://127.0.0.1:9000`

6. **Access the Web UI**
Open your browser to `http://127.0.0.1:9000`

### Deploy with ngrok (Optional)

```bash
ngrok http 9000
```

Copy the public URL and share with others for remote access.

## 💡 Usage

### Web Interface

1. Open `http://127.0.0.1:9000` in your browser
2. Select your role (admin/sales/ops)
3. Click the microphone icon or type your question
4. View generated SQL and query results in real-time

### Voice Mode (Command Line)

```bash
python live_asr.py
```

**Speak naturally:**
- "Show me all customers from India"
- "List orders above 1000"
- "Display delivered shipments"

The system will:
1. Transcribe your speech
2. Generate SQL
3. Execute the query
4. Display results

### API Endpoint

**POST** `/generate_sql`

**Request Body:**
```json
{
  "question": "Show me customers from USA who bought laptops",
  "role": "admin"
}
```

**Response:**
```json
{
  "sql": "SELECT Customers.customer_id, Customers.first_name, Customers.last_name FROM Customers JOIN Orders ON Customers.customer_id = Orders.customer_id WHERE Customers.country = 'USA' AND Orders.item LIKE '%laptop%';",
  "results": [
    {"customer_id": 2, "first_name": "Emily", "last_name": "Clark"},
    {"customer_id": 21, "first_name": "Daniel", "last_name": "Smith"}
  ]
}
```

## 🔐 Role-Based Access

| Role | Commerce Schema | HR Schema |
|------|-----------------|-----------|
| **Admin** | Full access (Customers, Orders, Shippings) | Full access (Employees, Departments) |
| **Sales** | Customers (limited), Orders | ❌ No access |
| **Ops** | Customer IDs, Shippings | ❌ No access |
| **HR User** | ❌ No access | Employees, Departments |

## 🛠️ Configuration

### Environment Variables

```bash
export OLLAMA_URL="http://127.0.0.1:11434/api/generate"
export MODEL_NAME="dolphin3:8b"
export DB_PATH="database.sqlite"
```

### Voice Configuration (live_asr.py)

```python
MODEL_SIZE = "large-v3"          # Whisper model
SAMPLE_RATE = 16000              # Audio sample rate
MIN_SPEECH_SEC = 0.5             # Minimum speech duration
SILENCE_END_SEC = 0.6            # Silence threshold
MIN_AVG_LOGPROB = -0.6           # Confidence threshold
```

## 📁 Project Structure

```
voice-sql-assistant/
├── server_ollama.py              # Main FastAPI server
├── live_asr.py                   # Voice input script
├── client.py                     # Database execution client
├── schemas.py                    # Multi-schema definitions
├── router.py                     # Schema router
├── setup.sql                     # Database initialization
├── database.sqlite               # SQLite database
├── requirements.txt              # Python dependencies
├── static/
│   └── voice.html               # Web UI
├── docs/
│   ├── architecture_diagram.png
│   ├── voice_pipeline.png
│   └── EXAMPLES.md
└── tests/
    └── test_server.py
```

## 🔧 Key Components

### Voice Processing (`live_asr.py`)

**Whisper Model**: `large-v3` for high-accuracy transcription [web:33][web:35]
**VAD**: Silero VAD detects speech vs silence [web:39][web:42]
**Denoising**: DeepFilterNet removes background noise
**Streaming**: Real-time processing with 30ms audio blocks

Features:
- Confidence filtering (avg_logprob, no_speech_prob)
- Automatic speech segmentation
- Silence detection and trimming
- CUDA acceleration support

### Multi-Schema Support (`schemas.py`)

Two independent schemas:
- **Commerce**: Customer orders and shipping
- **HR**: Employee and department management

Dynamic schema detection based on keywords in the question [file:32].

### Database Client (`client.py`)

Safe SQL execution with:
- Read-only enforcement (blocks INSERT, UPDATE, DELETE)
- Connection pooling with SQLite
- Result limiting (100 rows max)
- Row dictionary conversion [file:27]

### Web UI (`static/voice.html`)

- Voice recording with MediaRecorder API
- Real-time transcription display
- SQL result visualization
- Responsive design

## 🧪 Testing

### Test Voice Input
```bash
python live_asr.py
# Speak: "Show customers from India"
```

### Test API
```bash
curl -X POST http://127.0.0.1:9000/generate_sql \\
  -H "Content-Type: application/json" \\
  -d '{
    "question": "Show all customers",
    "role": "admin"
  }'
```

### Run Unit Tests
```bash
pytest tests/test_server.py
```

## 🐛 Known Limitations

- Voice mode requires CUDA GPU (CPU fallback available but slower)
- SQLite doesn't support concurrent writes
- Session storage is in-memory (lost on restart)
- Microphone selection hardcoded (device index 1)
- ngrok free tier has connection limits

## 🚀 Future Enhancements

- [ ] Speaker identification for multi-user sessions
- [ ] Query result visualization (charts/graphs)
- [ ] Voice output with TTS (text-to-speech)
- [ ] PostgreSQL/MySQL support
- [ ] WebSocket for streaming transcription
- [ ] Mobile app integration
- [ ] Advanced analytics dashboard
- [ ] Multi-language support

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for local LLM serving
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [Faster Whisper](https://github.com/SYSTRAN/faster-whisper) for high-speed ASR [web:33]
- [Silero VAD](https://github.com/snakers4/silero-vad) for voice activity detection [web:39]
- [DeepFilterNet](https://github.com/Rikorose/DeepFilterNet) for audio denoising
- [ngrok](https://ngrok.com/) for public tunneling [web:38]
- [sqlparse](https://github.com/andialbrecht/sqlparse) for SQL validation
- [rapidfuzz](https://github.com/maxbachmann/RapidFuzz) for fuzzy string matching

---

**Built with ❤️ for production ML applications**
"""

with open('README_v2.md', 'w') as f:
    f.write(readme_v2)

print("✅ Created updated README_v2.md")
