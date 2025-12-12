# Setting Up Groq API for Faster Evaluations

The Syntheverse PoD system uses Groq API for fast LLM responses. Currently, Ollama is being used as a fallback, which is slower and can timeout.

## Quick Setup

1. **Get a free Groq API key:**
   - Visit: https://console.groq.com/
   - Sign up (free)
   - Create an API key

2. **Set the environment variable:**
   ```bash
   export GROQ_API_KEY="your-api-key-here"
   ```

3. **Make it permanent (add to ~/.bashrc or ~/.zshrc):**
   ```bash
   echo 'export GROQ_API_KEY="your-api-key-here"' >> ~/.bashrc
   source ~/.bashrc
   ```

4. **Restart the services:**
   ```bash
   bash stop_all_services.sh
   bash start_all_services.sh
   ```

5. **Verify Groq is available:**
   ```bash
   curl http://localhost:8000/health | python3 -m json.tool | grep groq
   ```
   Should show: `"groq": "available"`

## Why Groq?

- **Fast**: Responses in 2-5 seconds vs 60-120 seconds with Ollama
- **Free**: Generous free tier
- **Reliable**: No timeouts on complex queries
- **Recommended**: Default LLM for Syntheverse PoD evaluations

## Troubleshooting

If Groq still shows as unavailable:
1. Check the key is set: `echo $GROQ_API_KEY`
2. Verify the key is valid at https://console.groq.com/
3. Check RAG API logs: `tail -f /tmp/syntheverse_rag_api.log`
4. Restart services after setting the key

