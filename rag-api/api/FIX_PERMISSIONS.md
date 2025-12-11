# Fix Ollama Permissions

## Problem

The Ollama binary is not executable, causing "Permission denied" errors.

## Solution

Run this command in your terminal (you'll be prompted for your password):

```bash
sudo chmod +x /Applications/Ollama.app/Contents/Resources/ollama
```

Or use the provided script:

```bash
cd rag-api/api
./fix_ollama_permissions.sh
```

## Verify

After fixing permissions, test:

```bash
ollama --version
```

If it works, you should see the version number.

## Then Start the Server

Once permissions are fixed, start the API server:

```bash
ollama serve
```

Keep that terminal open - the server runs in the foreground.

## Alternative: Direct Path

If the symlink still doesn't work, you can use the direct path:

```bash
/Applications/Ollama.app/Contents/Resources/ollama serve
```

