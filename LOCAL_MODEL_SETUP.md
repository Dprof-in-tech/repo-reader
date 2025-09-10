# GPT OSS 20B Local Model Setup

This guide explains how to integrate the official GPT OSS 20B model locally with your repository analyzer, while keeping OpenAI as a fallback.

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   cd api
   pip install -r requirements.txt
   ```

2. **Download GPT OSS 20B Model** (Choose one option)
   
   **Option A: HuggingFace CLI (Recommended)**
   ```bash
   pip install -U huggingface_hub
   huggingface-cli download openai/gpt-oss-20b --include "original/*" --local-dir ./models/gpt-oss-20b/
   ```
   
   **Option B: Direct from HuggingFace Hub** (No download needed)
   ```bash
   # Just set the model path to the HF repo name
   echo 'CHATGPT_OSS_MODEL_PATH=openai/gpt-oss-20b' >> .env
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your model path
   ```

4. **Verify Setup**
   ```bash
   python setup_local_model.py --verify-only
   ```

## 🔧 Configuration

### Environment Variables

```bash
# Required: Path to your local model
CHATGPT_OSS_MODEL_PATH=./models/chatgpt-oss-20b.gguf

# Optional: OpenAI fallback
OPENAI_API_KEY=your_key_here

# Performance tuning (optional)
LOCAL_MODEL_GPU_LAYERS=35      # Number of layers to run on GPU
LOCAL_MODEL_THREADS=8          # CPU threads to use
LOCAL_MODEL_BATCH_SIZE=512     # Batch size for processing
LOCAL_MODEL_CONTEXT_SIZE=4096  # Context window size
```

### Model Selection Priority

The system automatically chooses models in this order:
1. **Local ChatGPT OSS 20B** (if available)
2. **OpenAI GPT-5-nano** (fallback)
3. **Static generation** (if both fail)

## 🎯 Usage

The integration is transparent - no code changes needed! The system will:

- **Prefer local model** for quiz generation and code analysis
- **Automatically fallback** to OpenAI if local model fails
- **Log model usage** for monitoring

### Manual Model Selection

```python
from api.llm_manager import HybridLLMManager

# Create manager
llm = HybridLLMManager(
    local_model_path="./models/chatgpt-oss-20b.gguf",
    openai_api_key="your_key"
)

# Use local model preferentially
response = llm.invoke(messages, prefer_local=True)

# Force cloud model
response = llm.invoke(messages, prefer_local=False)
```

## 📊 Performance Comparison

| Model | Cost | Speed | Quality | Context |
|-------|------|-------|---------|---------|
| ChatGPT OSS 20B (Local) | Free | Fast* | Good | 4K |
| GPT-5-nano (Cloud) | $$$ | Fast | Excellent | 128K |

*Speed depends on your hardware

## 🛠 Hardware Requirements

### Minimum Requirements
- **RAM**: 16GB system RAM
- **Storage**: 15GB free space
- **CPU**: Modern multi-core processor

### Recommended for Best Performance
- **GPU**: NVIDIA RTX 3080+ with 12GB+ VRAM
- **RAM**: 32GB system RAM
- **CPU**: 8+ core processor
- **Storage**: SSD with 25GB+ free space

## 🔍 Troubleshooting

### Common Issues

1. **"Model failed to load"**
   - Check model file exists and isn't corrupted
   - Ensure sufficient RAM/VRAM
   - Try reducing `LOCAL_MODEL_GPU_LAYERS`

2. **"Slow inference"**
   - Increase `LOCAL_MODEL_GPU_LAYERS` if you have GPU
   - Adjust `LOCAL_MODEL_THREADS` to match your CPU cores
   - Consider using a smaller quantized model (q4_0 instead of q8_0)

3. **"Out of memory"**
   - Reduce `LOCAL_MODEL_CONTEXT_SIZE`
   - Use a more compressed model variant
   - Reduce `LOCAL_MODEL_BATCH_SIZE`

### Performance Tuning

For **CPU-only** systems:
```bash
LOCAL_MODEL_GPU_LAYERS=0
LOCAL_MODEL_THREADS=8
LOCAL_MODEL_BATCH_SIZE=256
```

For **GPU-accelerated** systems:
```bash
LOCAL_MODEL_GPU_LAYERS=35
LOCAL_MODEL_THREADS=4
LOCAL_MODEL_BATCH_SIZE=512
```

## 🔐 Privacy Benefits

Running locally means:
- ✅ **No data sent to external APIs**
- ✅ **Complete privacy for your code analysis**
- ✅ **No rate limits or API costs**
- ✅ **Works offline**

## 📈 Monitoring

Check model status:
```bash
curl http://localhost:5000/api/llm-status
```

Response:
```json
{
  "local_model": {
    "available": true,
    "type": "ChatGPT OSS 20B"
  },
  "cloud_model": {
    "available": true,
    "type": "GPT-5-nano"
  },
  "has_fallback": true
}
```

## 🤝 Contributing

Found an issue or want to improve the local model integration? 
- Check our troubleshooting section
- Submit issues with model logs
- Share your performance optimizations!