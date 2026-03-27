# Softnet

Social Network Analysis Tool

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/NETfrix/softnet?quickstart=1)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/NETfrix/softnet)

## Quick Start

### Use online (no install needed)

Click the **Deploy to Render** button above to get a public URL anyone can use — no signup required for your users.

Or click **Open in GitHub Codespaces** for a personal dev environment in the browser.

### Run locally

1. Make sure you have **Python 3.10+** and **Node.js 18+** installed.
2. Double-click `Softnet.bat` (Windows) or run:

```bash
pip install -e .
cd frontend && npm install && npm run build && cd ..
python run.py
```

The app will open at [http://localhost:8000](http://localhost:8000).

## Features

- Network visualization with Sigma.js
- Community detection (Leiden algorithm)
- ERGM analysis (MPLE, MCMC-MLE, MPLE-seeded MCMC)
- Network metrics: centrality, clustering, reciprocity, components
- Import/export: GraphML, CSV, Excel
- Bipartite network support
- Sankey diagrams and community graphs
