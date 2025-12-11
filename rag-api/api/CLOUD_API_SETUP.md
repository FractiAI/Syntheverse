# Cloud API Setup Guide

The RAG API now supports cloud-based LLM APIs as an alternative to local Ollama. This provides faster, more reliable responses.

## Recommended: Groq API (Fast & Free)

**Why Groq?**
- ⚡ Very fast inference (optimized hardware)
- 🆓 Free tier available
- 🔧 Simple API (OpenAI-compatible)
- 📊 Good for RAG applications

### Setup Steps:

1. **Get a free API key:**
   - Visit: https://console.groq.com/
   - Sign up (free, no credit card required)
   - Go to API Keys section
   - Create a new API key
   - Copy the key

2. **Set the API key:**
   ```bash
   export GROQ_API_KEY="your-api-key-here"
   ```
   
   Or create a `.env` file in `rag-api/api/`:
   ```
   GROQ_API_KEY=your-api-key-here
   ```

3. **Start the RAG API:**
   ```bash
   cd rag-api/api
   python3 rag_api.py
   ```

4. **Use in the UI:**
   - Select `llm_model: "groq"` in the dropdown
   - Or it will auto-detect if `GROQ_API_KEY` is set

## Alternative: Hugging Face Inference API (Free)

**Why Hugging Face?**
- 🆓 Completely free for many models
- 🎯 Wide selection of models
- 🔓 Open source models

### Setup Steps:

1. **Get a free token:**
   - Visit: https://huggingface.co/settings/tokens
   - Sign up (free)
   - Create a new token (read access)
   - Copy the token

2. **Set the token:**
   ```bash
   export HUGGINGFACE_API_KEY="your-token-here"
   ```

3. **Use in the UI:**
   - Select `llm_model: "huggingface"` in the dropdown

## Available Models

### Groq Models:
- `llama-3.1-8b-instant` (recommended - fast)
- `llama-3.1-70b-versatile` (more capable)
- `mixtral-8x7b-32768` (good for long context)

### Hugging Face Models:
- `mistralai/Mistral-7B-Instruct-v0.2`
- `meta-llama/Llama-2-7b-chat-hf`
- `google/flan-t5-large`

## Configuration

The API will automatically use:
1. Groq if `GROQ_API_KEY` is set
2. Hugging Face if `HUGGINGFACE_API_KEY` is set (and Groq is not)
3. Ollama as fallback (if running locally)

You can also specify in the API request:
```json
{
  "query": "your question",
  "llm_model": "groq"  // or "huggingface" or "ollama"
}
```

## Cost Comparison

- **Groq**: Free tier includes generous limits
- **Hugging Face**: Free for inference (rate limited)
- **Ollama**: Free but requires local setup and can be slow

## Troubleshooting

### Groq API Key Error
- Make sure `GROQ_API_KEY` environment variable is set
- Check the key is valid at https://console.groq.com/

### Hugging Face Rate Limit
- Free tier has rate limits
- Consider using Groq for faster, unlimited requests

### Model Not Found
- Check model name is correct
- For Hugging Face, ensure model supports text generation

