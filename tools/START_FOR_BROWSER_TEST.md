# Start Services for Browser Testing

## Step 1: Start the API Server

Open a **Terminal window** and run:

```bash
cd /Users/macbook/FractiAI/Syntheverse/ui-poc-api
python3 app.py
```

**OR** use the startup script:

```bash
cd /Users/macbook/FractiAI/Syntheverse
./start_poc_ui.sh
```

You should see:
```
Starting PoC API Server...
API will be available at: http://localhost:5001
✓ PoC Server initialized successfully
 * Running on http://0.0.0.0:5001
```

**Keep this terminal window open** - the API server needs to keep running.

## Step 2: Start the Frontend

Open a **NEW Terminal window** and run:

```bash
cd /Users/macbook/FractiAI/Syntheverse/ui-poc
npm run dev
```

You should see:
```
 ▲ Next.js 14.x.x
 - Local:        http://localhost:3001
 - Ready in X seconds
```

**Keep this terminal window open too** - the frontend dev server needs to keep running.

## Step 3: Open in Browser

1. Open your web browser (Chrome, Firefox, Safari, etc.)
2. Navigate to: **http://localhost:3001**
3. You should see the Syntheverse PoC UI!

## Step 4: Test the UI

### Dashboard
- Go to **http://localhost:3001/dashboard**
- You should see statistics and charts (may be empty if no contributions yet)

### Submit a Contribution
1. Click **"Submission"** in the navigation
2. Fill out the form:
   - **Title**: "Test Contribution"
   - **Contributor ID**: "test-001"
   - **Category**: Choose one (scientific/tech/alignment)
   - **Content**: Type some text content
3. Click **"Submit Contribution"**
4. You'll be redirected to the detail page

### View Submission Detail
- Click on any contribution in the Explorer or Registry
- Or use the hash from the URL after submitting
- Click **"Evaluate Contribution"** to run evaluation

### Explore Contributions
- Click **"Explorer"** in navigation
- See all contributions in a table
- Try sorting, searching, filtering

### View Registry
- Click **"Registry"** in navigation  
- See chronological timeline of all contributions

### Sandbox Map
- Click **"Sandbox Map"** in navigation
- Visualize contribution network
- Click nodes to select, double-click to view details

## Troubleshooting

### Port Already in Use
If you see "port already in use":
```bash
# Kill process on port 5001 (API)
lsof -ti:5001 | xargs kill -9

# Kill process on port 3001 (Frontend)
lsof -ti:3001 | xargs kill -9
```

### API Not Responding
- Check that API server is running
- Check terminal for error messages
- Verify GROQ_API_KEY is set: `echo $GROQ_API_KEY`

### Frontend Not Loading
- Check that `npm run dev` is running
- Check browser console (F12) for errors
- Try refreshing the page

### No Data Showing
- Submit a test contribution first
- Check API is responding: `curl http://localhost:5001/health`

## Quick Test Checklist

- [ ] API server running (Terminal 1)
- [ ] Frontend running (Terminal 2)
- [ ] Browser opened to http://localhost:3001
- [ ] Can see Dashboard
- [ ] Can submit a contribution
- [ ] Can view submission detail
- [ ] Can browse Explorer
- [ ] Can view Registry
- [ ] Can see Sandbox Map

## Stop Services

When done testing:

1. In Terminal 1 (API): Press `Ctrl+C`
2. In Terminal 2 (Frontend): Press `Ctrl+C`

**OR** use the stop script:

```bash
cd /Users/macbook/FractiAI/Syntheverse
./stop_poc_ui.sh
```
