# Quick Reference Card (v2.0 - Voice Edition)

## Voice Mode

### Start Voice Client
```bash
python live_asr.py
```

### Voice Commands
- **Speak naturally:** "Show me customers from India"
- **Aggregations:** "How many orders per customer?"
- **Filters:** "List orders above 1000 dollars"
- **Joins:** "Show customers who bought laptops"

### Voice Output
```
Mic level: 0.156

[VOICE QUERY]
show me customers from india

[SQL]
SELECT ...

[RESULTS]
{...}
```

## Web UI

### Access
```
http://127.0.0.1:9000
```

### Controls
- 🎤 Click microphone to record
- 📝 Type in text box
- 🔄 Select role dropdown
- ✅ Submit button

## API Endpoint

**POST** `/generate_sql`

```bash
curl -X POST http://127.0.0.1:9000/generate_sql \
  -H "Content-Type: application/json" \
  -d '{
    "question": "YOUR QUESTION",
    "role": "admin"
  }'
```

## Roles & Access

| Role | Commerce | HR |
|------|----------|-----|
| `admin` | Full | Full |
| `sales` | Limited | ❌ |
| `ops` | Shipping only | ❌ |
| `hr_user` | ❌ | Full |

## Schemas

### Commerce
- Customers (customer_id, first_name, last_name, age, country)
- Orders (order_id, item, amount, customer_id)
- Shippings (shipping_id, order_id, status_text)

### HR
- Employees (employee_id, name, age, department_id)
- Departments (department_id, department_name)

## Commands

### Start Server
```bash
python server_ollama.py
```

### Initialize Database
```bash
sqlite3 database.sqlite < setup.sql
```

### Deploy with ngrok
```bash
ngrok http 9000
```

### Run Tests
```bash
pytest tests/
```

## Configuration

### Environment Variables
```bash
export OLLAMA_URL="http://127.0.0.1:11434/api/generate"
export MODEL_NAME="dolphin3:8b"
export DB_PATH="database.sqlite"
```

### Voice Settings (live_asr.py)
```python
MODEL_SIZE = "large-v3"        # Whisper model
SAMPLE_RATE = 16000            # Audio sample rate
MIN_SPEECH_SEC = 0.5           # Min speech duration
SILENCE_END_SEC = 0.6          # Silence threshold
```

### Microphone Device
```python
sd.default.device = (1, None)  # Device index
```

## Common Patterns

### Voice Query
Speak: "Show customers older than 40 from USA"

### Follow-up
First: "Show customers who bought laptops"  
Then: "Only those from USA"

### Aggregation
"Total orders per customer"

### Chat Mode
"Hello, how are you?"

### Explain Mode
First: (generates SQL)  
Then: "Explain this query"

## Response Types

### SQL Intent
```json
{
  "sql": "SELECT ...",
  "results": [...]
}
```

### Chat Intent
```json
{
  "message": "Hello! ...",
  "intent": "chat"
}
```

### Explain Intent
```json
{
  "message": "This query ...",
  "intent": "explain"
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Ollama not running | `ollama serve` |
| Model not found | `ollama pull dolphin3:8b` |
| Mic not detected | Check device index |
| CUDA error | Use CPU mode |
| Low audio quality | Reduce background noise |
| Slow transcription | Use smaller model or GPU |

## Performance

### Voice Pipeline (GPU)
- Transcription: 1-2s
- SQL generation: 2-5s
- Total: 5-8s

### Voice Pipeline (CPU)
- Transcription: 8-12s
- Total: 15-20s

## Python Client

```python
import requests

url = "http://127.0.0.1:9000/generate_sql"

response = requests.post(url, json={
    "question": "Show customers",
    "role": "admin"
})

print(response.json())
```

## Database Queries

```python
from client import execute_sql

rows = execute_sql("SELECT * FROM Customers LIMIT 10;")
for row in rows:
    print(row)
```

## Special Commands

- `"reset"` - Clear session
- `"explain"` - Explain last SQL
- Conversational text - Chat mode
- Schema keywords - SQL mode

## URLs

- **Local server:** http://127.0.0.1:9000
- **API docs:** http://127.0.0.1:9000/docs
- **ngrok (example):** https://abc123.ngrok.io

## File Locations

- Server: `server_ollama.py`
- Voice: `live_asr.py`
- Database: `database.sqlite`
- Web UI: `static/voice.html`
- Logs: `server_debug.log`

## Dependencies

```bash
pip install -r requirements.txt
```

**Key packages:**
- faster-whisper==1.0.3
- fastapi==0.104.1
- torch==2.1.0
- sounddevice==0.4.6
