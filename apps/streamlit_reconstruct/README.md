# 🔬 Research Nexus Visualizer

AI-powered interactive research interconnection map generator — built with Streamlit + OpenRouter.

## Features

| Feature | Description |
|---------|-------------|
| 🤖 AI Categorization | LLM dynamically infers thematic clusters from your URL corpus |
| 🗺️ Network Graph | Interactive vis.js network: zoom, drag, click-to-inspect |
| 🔮 Predictions | AI identifies research gaps and recommends next steps |
| 📤 Export | Standalone HTML, JSON, and CSV download |
| 🌐 OpenRouter | Access ALL available models (GPT-4, Claude, Llama, Mistral…) |

## Quickstart

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run
streamlit run app.py
```

Then open http://localhost:8501

## Usage Flow

```
1. Input Data tab  →  upload collected_links.txt (or paste URLs)
2. AI Analysis tab →  enter OpenRouter API key, pick model, run analysis
3. Visualization   →  interactive network map renders automatically
4. Predictions     →  AI research gap analysis
5. Export          →  download HTML / JSON / CSV
```

## Input Formats

- **collected_links.txt** — one URL per line  
- **CSV** — any column containing http:// URLs  
- **JSON** — array of strings, object with URL values, or previously exported Research Nexus JSON  
- **Directory** — scans recursively for `collected_links.txt`, `links.txt`, `.mermaid` files  

## Directory Structure Convention

```
PROJECT_ROOT/
├── raw_data/
│   └── urls/collected_links.txt   ← auto-detected
├── processed/                      ← AI output saved here
├── output/                         ← HTML exports
├── logs/
└── collected_links.txt             ← also auto-detected
```

## OpenRouter

Get your API key at https://openrouter.ai  
Free models are listed first (look for `:free` suffix).

## Tech Stack

- **Streamlit** — UI framework  
- **OpenRouter** — LLM gateway (GPT-4, Claude, Llama, Mistral, etc.)  
- **vis.js** — network visualization (embedded in exported HTML)  
- **Plotly** — in-app charts  
- **Pandas** — data processing  
