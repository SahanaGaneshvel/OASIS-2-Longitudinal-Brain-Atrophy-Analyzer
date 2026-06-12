# Deployment Guide - Phase 1

## Pre-Deployment Checklist

### Local Testing
- [ ] Analysis script runs: `python analysis/tabular_analysis.py`
- [ ] `web/public/data/results.json` exists and contains real metrics
- [ ] Dashboard loads locally: `npm run dev` → http://localhost:3000
- [ ] All components render correctly:
  - [ ] Subject selector works
  - [ ] Metrics display shows AUC ± std (not 0.000 ± 0.000)
  - [ ] Scatter plot renders
  - [ ] Footer acknowledgment visible

### Data Validation
- [ ] `results.json` contains >100 subjects
- [ ] AUC values are between 0.5 and 1.0
- [ ] Both demented and non-demented groups have >10 subjects
- [ ] p-value is < 0.05 (if hypothesis is correct)

---

## Deployment Steps

### 1. Build Frontend Locally (Test First)

```bash
cd web

# Install dependencies
npm install

# Test build
npm run build

# Verify output
ls -lh out/data/results.json  # Should exist and be >1KB

# Test production build locally
npm start
# Open http://localhost:3000 and verify everything works
```

### 2. Deploy to Vercel

#### Option A: Vercel CLI

```bash
# Install Vercel CLI globally
npm install -g vercel

# Login to Vercel
vercel login

# Deploy (from web/ directory)
cd web
vercel --prod

# Note the deployment URL
```

#### Option B: Vercel Dashboard (Git-based)

1. Push code to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial Phase 1 deployment"
   git remote add origin https://github.com/yourusername/oasis-brain-atrophy.git
   git push -u origin main
   ```

2. Connect to Vercel:
   - Go to https://vercel.com/new
   - Import your GitHub repository
   - **Root Directory**: `web`
   - **Framework Preset**: Next.js
   - **Build Command**: `npm run build`
   - **Output Directory**: `out`
   - Deploy

3. **Critical**: Ensure `web/public/data/results.json` is committed to Git **before** pushing (not gitignored for deployment)

---

## Important: Data Pipeline for Deployment

### Option 1: Commit Generated Results (Simplest)

For Phase 1, the easiest approach:

```bash
# Run analysis
python analysis/tabular_analysis.py

# Temporarily allow results.json in git (modify .gitignore)
git add web/public/data/results.json
git commit -m "Add computed analysis results for deployment"
git push
```

Then deploy via Vercel dashboard (it will use the committed JSON).

**Pros**: Simple, works for static dataset
**Cons**: Need to re-commit JSON when data changes

### Option 2: Build-Time Analysis (Advanced)

Modify `web/package.json` to run analysis during build:

```json
{
  "scripts": {
    "prebuild": "cd ../analysis && python tabular_analysis.py",
    "build": "next build"
  }
}
```

Then configure Vercel build settings:
- **Build Command**: `npm run build`
- **Install Command**: `pip install -r ../analysis/requirements.txt && npm install`

**Pros**: Always uses latest data
**Cons**: Requires Python in Vercel build environment (may need custom Docker image)

**Recommendation for Phase 1**: Use Option 1 (commit results.json). It's simpler and the dataset is static.

---

## Post-Deployment Verification

After deploying, verify at your live URL:

- [ ] Page loads without errors
- [ ] All three components render (SubjectViewer, CohortSummary, MetricsDisplay)
- [ ] Subject selector is populated with real subject IDs
- [ ] Metrics show non-zero values with ± std
- [ ] Scatter plot displays points in two colors (demented/non-demented)
- [ ] Footer shows data-use acknowledgment
- [ ] Console has no errors (open browser DevTools)

### Common Issues

**Dashboard loads but shows "Error: Failed to load analysis results"**
- `results.json` not deployed
- Check: `https://your-url.vercel.app/data/results.json` (should return JSON)
- Fix: Ensure `web/public/data/results.json` is committed or generated during build

**Metrics show 0.000 ± 0.000**
- Placeholder JSON is being used instead of real results
- Fix: Run `python analysis/tabular_analysis.py` and rebuild

**Build fails on Vercel**
- Check build logs in Vercel dashboard
- Common: Missing dependencies, wrong Node version
- Fix: Ensure `package.json` is valid, use Node 18+

---

## Update README with Live URL

Once deployed, update the main README:

```markdown
**Live demo:** https://your-app.vercel.app
```

---

## Phase 1 Deployment Complete

Verify checklist:

- [ ] Live URL works and shows real data
- [ ] README updated with live URL
- [ ] Metrics are computed from real OASIS-2 data (not fabricated)
- [ ] All values include ± std (from stratified CV)
- [ ] Data-use acknowledgment is visible
- [ ] Project is ready for review

**Stop here. Do NOT start Phase 2 until Phase 1 is confirmed working on the live URL.**

---

## Monitoring & Updates

### Updating Metrics

If you rerun the analysis with different parameters:

```bash
# Rerun analysis
python analysis/tabular_analysis.py

# Rebuild frontend
cd web
npm run build

# Redeploy
vercel --prod
# Or push to GitHub if using git-based deployment
```

### Performance

Expected load times:
- First paint: <2s
- `results.json`: <100KB, loads instantly
- Recharts rendering: <500ms

If slower, check:
- JSON file size (should be <200KB for 150 subjects)
- Next.js build optimization (should be static export)

---

## Next Steps: Phase 2

**Only proceed after Phase 1 live URL is confirmed working.**

Phase 2 will add:
- SynthSeg segmentation (offline batch processing)
- Per-region atrophy metrics
- Brain viewer (NiiVue or PNG slices)
- Regional atrophy heatmap

See [analysis/README.md](analysis/README.md) for Phase 2 setup.
