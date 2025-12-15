# Testing the PoC Frontend

## Prerequisites

1. **Groq API Key**: Set `GROQ_API_KEY` environment variable
2. **Python Dependencies**: Install PoC server dependencies
3. **Node.js**: For running the Next.js frontend

## Quick Start

### 1. Start the Backend API Server

```bash
# Terminal 1: Start the API server
cd ui-poc-api
pip install -r requirements.txt
export GROQ_API_KEY=your-groq-api-key
python app.py
```

The API server will run on `http://localhost:5001`

### 2. Start the Frontend

```bash
# Terminal 2: Start the Next.js frontend
cd ui-poc
npm install
npm run dev
```

The frontend will run on `http://localhost:3000`

### 3. Test the Application

1. **Open Browser**: Navigate to `http://localhost:3000`

2. **Dashboard** (`/dashboard`):
   - Should show overview statistics
   - Charts for contribution status and metal distribution
   - Epoch distribution breakdown

3. **Submit Contribution** (`/submission`):
   - Fill out the form:
     - Title: "Test Contribution"
     - Contributor: "test-contributor-001"
     - Category: "scientific"
     - Content: Paste some text content
   - Click "Submit Contribution"
   - Should redirect to submission detail page

4. **Submission Detail** (`/submission/[hash]`):
   - View the submitted contribution
   - Click "Evaluate Contribution" button
   - Wait for evaluation (may take 30-60 seconds)
   - Should show evaluation metrics and allocations

5. **Explorer** (`/explorer`):
   - Browse all contributions in a table
   - Test sorting by clicking column headers
   - Test search/filter functionality
   - Click on a row to view detail

6. **Registry** (`/registry`):
   - View chronological append-only log
   - See contribution timeline
   - Click on entries to view details

7. **Sandbox Map** (`/sandbox-map`):
   - Visualize contribution network
   - Test filters (overlap type, status, metal)
   - Click nodes to select
   - Double-click nodes to navigate to detail
   - Test zoom and pan controls

## Testing Checklist

### Dashboard
- [ ] Statistics load correctly
- [ ] Charts render properly
- [ ] Epoch distribution shows correctly
- [ ] Data updates when contributions are added

### Submission
- [ ] Form validation works
- [ ] Submission creates entry in archive
- [ ] Redirect to detail page works
- [ ] Status shows as "submitted"

### Evaluation
- [ ] Evaluation button triggers evaluation
- [ ] Progress indicators show (if implemented)
- [ ] Evaluation results display correctly
- [ ] Multi-metal allocations show (if applicable)
- [ ] Status updates to qualified/unqualified

### Explorer
- [ ] Table loads all contributions
- [ ] Sorting works on all columns
- [ ] Search/filter works
- [ ] Pagination works
- [ ] Click to detail works

### Registry
- [ ] Chronological order is correct
- [ ] Registry index numbers are sequential
- [ ] Metal indicators show correctly
- [ ] Status badges display properly
- [ ] Click to detail works

### Sandbox Map
- [ ] Network graph renders
- [ ] Nodes show correct colors (metals)
- [ ] Edges show overlap relationships
- [ ] Filters work correctly
- [ ] Node selection works
- [ ] Double-click navigation works
- [ ] Zoom/pan controls work
- [ ] Legend displays correctly

## Troubleshooting

### API Connection Issues
- Check that API server is running on port 5001
- Verify `NEXT_PUBLIC_API_URL` in `.env.local` (defaults to `http://localhost:5001`)
- Check browser console for CORS errors

### Evaluation Fails
- Verify `GROQ_API_KEY` is set correctly
- Check API server logs for errors
- Ensure text content is provided

### No Data Showing
- Check if archive has contributions
- Verify API endpoints are returning data
- Check browser network tab for API calls

### Sandbox Map Not Rendering
- Check browser console for errors
- Verify vis-network CSS is loaded
- Check that map data is being fetched

## Expected Behavior

1. **Archive-First**: All submissions are stored regardless of evaluation status
2. **Multi-Metal**: Contributions can contain multiple metals (Gold + Silver + Copper)
3. **Lifecycle Tracking**: Status transitions: Draft → Submitted → Evaluating → Qualified/Unqualified
4. **Redundancy Detection**: Evaluates against entire archive, not just approved submissions
5. **Visualization**: Sandbox map shows relationships and overlaps

## Next Steps

After basic testing:
1. Test with multiple contributions
2. Test edge cases (empty content, very long content)
3. Test filter combinations
4. Test with different metal types
5. Verify archive persistence across restarts
