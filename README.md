# Softnet

Social Network Analysis Tool

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/NETfrix/softnet?quickstart=1)

## Quick Start

### Run in the cloud (no install needed)

Click the **Open in GitHub Codespaces** button above. The app will build automatically and open in your browser.

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
