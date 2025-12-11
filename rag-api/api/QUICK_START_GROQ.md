# Quick Start: Using Groq API (Free & Fast)

## Step 1: Get Your Free Groq API Key

1. Visit: https://console.groq.com/
2. Sign up (free, no credit card required)
3. Go to **API Keys** section
4. Click **Create API Key**
5. Copy the key (starts with `gsk_...`)

## Step 2: Set the API Key

**Option A: Environment Variable (Recommended)**
```bash
export GROQ_API_KEY="your-api-key-here"
```

**Option B: Add to your shell profile**
```bash
echo 'export GROQ_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc
```

## Step 3: Install Dependencies

```bash
cd rag-api/api
pip3 install -r requirements_api.txt
```

## Step 4: Start the RAG API

```bash
python3 rag_api.py
```

The API will automatically detect Groq and use it as the default LLM provider.

## Step 5: Test It

Open your browser to: http://localhost:8000

The UI will automatically use Groq for fast responses!

## Why Groq?

- ⚡ **Very Fast**: Optimized hardware for LLM inference
- 🆓 **Free Tier**: Generous free limits
- 🔧 **Easy Setup**: Just set one environment variable
- 📊 **Reliable**: No local setup or model downloads needed

## Troubleshooting

**"No LLM provider available"**
- Make sure `GROQ_API_KEY` is set: `echo $GROQ_API_KEY`
- Restart the API server after setting the key

**"Error calling Groq API"**
- Check your API key is valid at https://console.groq.com/
- Make sure you're connected to the internet

**Still using Ollama?**
- The API prefers Groq if available
- Check `/health` endpoint to see which providers are available

