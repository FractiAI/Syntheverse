# Quick Test Guide

## Start Everything

```bash
# Make sure GROQ_API_KEY is set
export GROQ_API_KEY=your-groq-api-key

# Start both API and frontend
./start_poc_ui.sh
```

This will:
1. Start the API server on port 5001
2. Start the Next.js frontend on port 3000
3. Wait for both to be ready

## Test the System

### 1. Open the Frontend
Navigate to: **http://localhost:3000**

### 2. Test Each View

#### Dashboard (`/dashboard`)
- Should show statistics and charts
- Check that data loads

#### Submit Contribution (`/submission`)
- Fill out the form:
  - Title: "Test Contribution"
  - Contributor: "test-001"
  - Category: "scientific"
  - Content: "This is a test contribution for the PoC system."
- Click "Submit Contribution"
- Should redirect to detail page

#### Submission Detail (`/submission/[hash]`)
- View the submitted contribution
- Click "Evaluate Contribution"
- Wait for evaluation (30-60 seconds)
- Should show metrics and allocations

#### Explorer (`/explorer`)
- Browse contributions in table
- Test sorting and search
- Click rows to view details

#### Registry (`/registry`)
- View chronological log
- Check timeline order
- Click entries for details

#### Sandbox Map (`/sandbox-map`)
- Visualize contribution network
- Test filters
- Click/double-click nodes
- Test zoom and pan

### 3. Quick Connectivity Test

```bash
./test_poc_quick.sh
```

This tests:
- API server health
- API endpoints
- Frontend connectivity

## Stop Everything

```bash
./stop_poc_ui.sh
```

## Troubleshooting

### API Server Won't Start
- Check if port 5001 is in use: `lsof -ti:5001`
- Verify GROQ_API_KEY is set
- Check logs: `tail -f /tmp/poc_api.log`

### Frontend Won't Start
- Check if port 3000 is in use: `lsof -ti:3000`
- Install dependencies: `cd ui-poc && npm install`
- Check logs: `tail -f /tmp/poc_frontend.log`

### No Data Showing
- Verify API is running: `curl http://localhost:5001/health`
- Check browser console for errors
- Verify API endpoints return data: `curl http://localhost:5001/api/archive/statistics`

### Evaluation Fails
- Check GROQ_API_KEY is set correctly
- Check API server logs for errors
- Verify text content is provided in submission

## Expected Results

1. **Archive-First**: All submissions stored regardless of status
2. **Multi-Metal**: Contributions can have multiple metals
3. **Lifecycle**: Status transitions work correctly
4. **Visualization**: Sandbox map shows relationships
5. **Filtering**: All filters work in explorer and map
