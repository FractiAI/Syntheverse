# API Development Standards

## Flask API (PoC API)

### Structure
- Use Flask blueprints for route organization
- Separate route handlers from business logic
- Use Flask-CORS for cross-origin requests
- Implement proper error handling

### Route Patterns
```python
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/endpoint', methods=['GET'])
def get_endpoint():
    try:
        # Business logic
        result = process_request()
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
```

### Error Handling
- Return consistent error response format
- Use appropriate HTTP status codes
- Include error messages for debugging
- Log errors server-side

### Request Validation
- Validate all inputs
- Use secure filename handling (`werkzeug.utils.secure_filename`)
- Validate file types and sizes
- Sanitize user inputs

### Response Format
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message"
}
```

## FastAPI (RAG API)

### Structure
- Use dependency injection for shared resources
- Define request/response models with Pydantic
- Use async/await for I/O operations
- Organize routes with routers

### Route Patterns
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

@app.post("/query")
async def query(request: QueryRequest):
    try:
        result = await process_query(request.query)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Documentation
- Use OpenAPI/Swagger for API documentation
- Document all endpoints with docstrings
- Include request/response examples
- Document error responses

## Syntheverse API Patterns

### Integration Points
- PoC API connects Next.js frontend to Layer 2 backend
- RAG API provides document search and query capabilities
- Both APIs use Groq API for LLM operations
- APIs handle file uploads and processing

### Environment Variables
- Use centralized `src.core.utils.load_groq_api_key()` utility for loading GROQ_API_KEY
- Store API keys in `.env` file at project root
- Document required variables in module docstrings
- Validate configuration on startup
- Never commit `.env` files to repository

### CORS Configuration
- Configure CORS for frontend origins
- Use environment-specific CORS settings
- Allow only necessary headers and methods

### File Handling
- Validate file types (PDFs for PoC submissions)
- Store files securely
- Generate unique filenames
- Clean up temporary files

### Logging
- Log API requests and responses
- Include request IDs for tracing
- Log errors with full context
- Use appropriate log levels







