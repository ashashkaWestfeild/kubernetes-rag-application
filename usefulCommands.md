# Data Ingestion Commands

Source: https://agenticai-session.notion.site/Data-Ingestion-Commands-3925a934f2cf803b802ed0b6483257f4

Ingestion commands for the 3 useful cases.

## 1. Ingest only clean data

```bash
python -m app.ingestion.processor DATA/true_data true
```

This wipes Qdrant first, then indexes only the clean documents from `DATA/true_data`.

## 2. Ingest only 10 noisy files

```bash
python -m app.ingestion.processor DATA/noisy_sample_10 noisy
```

## 3. Ingest only 15 noisy files

```bash
python -m app.ingestion.processor DATA/noisy_sample_15 noisy
```

Use `--wipe` when you want a fresh Qdrant collection. If you want to append noisy files after clean data, omit `--wipe` on the noisy ingestion command.

## Eval flow (diagram on the same page)

- **Golden dataset** (`evals/golden_dataset.json`): 15 RAG Q&A samples + 6 guardrails samples
- **Eval Streamlit app** (`evals/app.py`), 3 steps: review ground truth -> run live pipeline -> run eval metrics
- **Live pipeline** calls the FastAPI backend `POST /query` (`app/main.py`), i.e. guardrails + LangGraph + retrieval + response (`app/agents/*`, `app/guardrails/*`, `app/services/retrieval/*`)
- **Enriched dataset** (`actual_response`, `actual_contexts`, `actual_tools_called`), held in Streamlit session_state, filled by `evals/pipeline.py`
- **Guardrails evaluation**: TP / TN / FP / FN (`evals/guardrails_eval.py`)
- **RAGAS metrics**: faithfulness, answer relevancy, context precision, context recall, answer correctness (`evals/metrics.py`)
- **Tool correctness**: expected tool vs actual tool (`evals/metrics.py`)
- **Results dashboard**: scores + tables + summary (`evals/app.py`)
