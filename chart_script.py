
# Create a detailed flowchart for the voice-to-SQL pipeline
diagram_code = """
flowchart TD
    A[Microphone Input] --> B[sounddevice Capture<br/>30ms blocks]
    B --> C[DeepFilterNet Denoising]
    C --> D[Silero VAD]
    D --> E{Speech<br/>Detected?}
    E -->|No| F[Continue Buffering]
    F --> D
    E -->|Yes| G[Audio Buffer<br/>Accumulation]
    G --> H[Silence Detection<br/>0.6s threshold]
    H --> I[Faster Whisper<br/>Transcription<br/>large-v3]
    I --> J[Confidence Filter<br/>avg_logprob,<br/>no_speech_prob]
    J --> K{High<br/>Confidence?}
    K -->|No| L[Discard]
    K -->|Yes| M[FastAPI<br/>/generate_sql endpoint]
    M --> N[Schema Detection<br/>Commerce vs HR]
    N --> O[Role-Based Filtering]
    O --> P[Ollama LLM Call]
    P --> Q[SQL Validation]
    Q --> R{Validation<br/>Success?}
    R -->|No| S[Retry with Feedback]
    S --> P
    R -->|Yes| T[SQLite Query<br/>Execution]
    T --> U[Results Display<br/>terminal or web UI]
"""

# Create the mermaid diagram using the helper function
create_mermaid_diagram(diagram_code, 'voice_to_sql_pipeline.png', 'voice_to_sql_pipeline.svg', width=1400, height=2000)
