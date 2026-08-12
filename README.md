# GraphOne / FrontierAtlas Intelligence Pipeline

This repository contains the complete implementation for the GraphOne Data Intelligence pipeline, designed to seamlessly extract, enrich, and canonicalize massive volumes of semi-structured web data across the AI and venture ecosystem.

## Features

- **Massive Scalability**: Asynchronous `aiohttp` pipelines structured for non-blocking I/O, capable of processing thousands of entities concurrently.
- **Extreme Freshness Engine**: Intelligently normalizes JSON-LD, OpenGraph, and `<time>` HTML meta-tags. Backed by deterministic hashing (`content_id`) to track 24-hour exact freshness and prevent duplicates.
- **Multi-Tier LLM Extraction**: Orchestrator dynamically routes JSON schema extraction across Groq, Gemini, and DeepSeek with exponential backoff and jitter for `429 Too Many Requests` handling. Implements intelligent payload truncation to prevent `413 Payload Too Large` errors.
- **Deterministic Entity Resolution**: Utilizes `rapidfuzz` to canonicalize raw startup names (e.g. "Open AI Inc.") against a mock 50-entity seed index.
- **Anti-Bot Defenses**: Features dynamic HTTP headers and automated delay jittering to prevent CAPTCHA triggering on high-value intelligence sources.

## Setup Instructions

### 1. Prerequisites
Ensure you have Python 3.10+ and Node.js installed.

### 2. Environment Variables
Create a `.env` file in the root directory and populate it with your API keys:
```env
# LLM Providers (Comma-separated for key rotation)
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key
DEEPSEEK_API_KEY=your_deepseek_key

# Model Selection
GROQ_MODEL=llama-3.3-70b-versatile
GEMINI_MODEL=gemini-2.5-flash

# Orchestration Settings
LLM_PROVIDER_ORDER=groq,gemini,deepseek
LLM_MAX_RETRIES=4

# GitHub API (For Research Paper stars)
GITHUB_TOKEN=your_github_token
```

### 3. Backend Setup
Install the python dependencies:
```bash
pip install -r requirements.txt
```

Run the backend FastAPI server:
```bash
python -m uvicorn api.main:app --reload --port 8000
```

### 4. Frontend Setup
In a new terminal, navigate to the frontend directory:
```bash
cd frontend
npm install
npm run dev
```
Navigate to the provided localhost port (e.g. `http://localhost:5173`) to view the Glassmorphism Intelligence Dashboard.

### 5. Exporting Data
To generate the final CSVs formatted exactly to the required nested schemas for Google Sheets submission, run:
```bash
python export.py
```
The final CSVs will be available in the `exports/` folder.

## Architecture Documentation
Please see [architecture.md](./architecture.md) (or the generated PDF equivalent) for a detailed technical design addressing Scale, 413/429 handling, Freshness Tracking, and our Database storage strategy.
