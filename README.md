# Bengaluru Rental Truth-Teller

The second opinion your broker doesn't want you to have.

## Problem

Bengaluru's rental market is opaque. Brokers exploit information asymmetry —
quoting long deposits as “standard,” inflating rents, and pressuring newcomers who lack reference points.

## Solution

A conversational agent grounded in enriched listing data. Ask whether a rent or deposit is fair, compare neighbourhoods, or search semantically over descriptions — answers should cite sources from your Elasticsearch index.

## Tech Stack

- **Elasticsearch Cloud Serverless** — storage, semantic search (ELSER via `semantic_text`), ES|QL analytics  
- **AWS Bedrock (Claude)** — tool-use orchestration and reasoning  
- **Python** — ingest pipeline, agent loop, tools  
- **Streamlit** — chat UI  

## Prerequisites

Steps **1–2** in [`docs/rental-truth-teller-implementation-plan.md`](docs/rental-truth-teller-implementation-plan.md): Elastic Serverless project with API key, and Bedrock access with IAM credentials.

## Quick start

1. `cp .env.example .env` and fill in `ES_URL`, `ES_API_KEY`, and AWS variables.

2. Create a virtualenv and install deps:
   ```bash
   pip install -r requirements.txt
   ```

3. **Step 3** (plan): verify ELSER endpoint `.elser-2-elasticsearch` exists on your cluster.

4. Download the Kaggle CSV into `data/raw/` (see `data/raw/README.md`).

5. Create index:
   - Bash: `bash scripts/setup_es.sh`
   - PowerShell (Windows): `powershell -ExecutionPolicy Bypass -File scripts/setup_es.ps1`

6. Build processed data and index:
   ```bash
   python ingest/normalize_and_enrich.py
   python ingest/bulk_index.py
   ```

7. Run the UI:
   ```bash
   streamlit run app/streamlit_app.py
   ```

Optional CLI demos (from repo root):

```bash
python scripts/demo.py
```

## Layout

Matches the implementation plan: `ingest/` (normalize, bulk index, mappings), `agent/` (Bedrock loop + ES tools), `app/streamlit_app.py`, `data/`, `scripts/`.

## Data

- Kaggle: [Bangalore House Rent Details](https://www.kaggle.com/datasets/csunnikrishnan/bangalore-house-rent-details-1bhk-2bhk-3bhk) — see `data/SOURCES.md`

## Team

Add your names here.
