# Testing PoC Frontend

## Quick Start

Run the test script to start everything:

```bash
./test_poc_frontend.sh
```

This will:
1. Check dependencies
2. Start API server on port 5001
3. Start Next.js frontend on port 3000
4. Open browser to test

## Manual Testing

### 1. Start API Server

```bash
cd ui-poc-api
pip install -r requirements.txt
export GROQ_API_KEY=your-key-here  # Required for evaluations
python server.py
```

API will run on: http://localhost:5001

### 2. Start Frontend

In a new terminal:

```bash
cd ui-poc
npm install  # First time only
npm run dev
```

Frontend will run on: http://localhost:3000

### 3. Test Views

1. **Dashboard** (http://localhost:3000/dashboard)
   - Should show statistics cards
   - Charts should render

2. **Explorer** (http://localhost:3000/explorer)
   - Should show contributions table
   - Try sorting, filtering, searching

3. **Submission** (http://localhost:3000/submission)
   - Submit a test contribution
   - Fill form and submit

4. **Registry** (http://localhost:3000/registry)
   - Should show chronological list
   - Click to view details

5. **Sandbox Map** (http://localhost:3000/sandbox-map)
   - Should show network graph
   - Try filters and interactions

### 4. Test API Endpoints

```bash
# Check API health
curl http://localhost:5001/

# Get archive statistics
curl http://localhost:5001/api/archive/statistics

# Get contributions
curl http://localhost:5001/api/archive/contributions

# Get sandbox map
curl http://localhost:5001/api/sandbox-map
```

## Troubleshooting

### API Server Errors

- Check `GROQ_API_KEY` is set
- Check Python dependencies: `pip install -r ui-poc-api/requirements.txt`
- Check logs: `tail -f /tmp/poc_api.log`

### Frontend Errors

- Check Node dependencies: `cd ui-poc && npm install`
- Check logs: `tail -f /tmp/poc_frontend.log`
- Check browser console for errors

### CORS Errors

- Ensure API server CORS is configured for `http://localhost:3000`
- Check API server is running on port 5001

### No Data Showing

- API server may not be initialized (check GROQ_API_KEY)
- Archive may be empty (submit some contributions first)
- Check network tab in browser DevTools

## Expected Behavior

1. **Empty State**: If no contributions exist, views should show empty states
2. **Submit Flow**: Submit → Draft → Submitted → Evaluating → Qualified/Unqualified
3. **Multi-metal**: Contributions can have multiple metals after evaluation
4. **Archive-first**: All submissions stored regardless of status
5. **Sandbox Map**: Visualizes relationships and overlaps
