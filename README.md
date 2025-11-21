# DocumentReferenceRAG  
**RAG System developed for the Fleet-Mechanic Assistant AI Agent at the Pasco County Sheriff’s Office**  

## Table of Contents  
1. [Project Overview](#project-overview)  
2. [Features](#features)  
3. [Architecture & Components](#architecture--components)  
4. [Getting Started](#getting-started)  
   - [Prerequisites](#prerequisites)  
   - [Installation](#installation)  
   - [Configuration](#configuration)  
   - [Running the Application](#running-the-application)  
5. [Usage](#usage)  
6. [Project Structure](#project-structure)  
7. [Contributing](#contributing)  
8. [License](#license)  
9. [Acknowledgements](#acknowledgements)  

---

## Project Overview  
DocumentReferenceRAG is a Retrieval-Augmented Generation (RAG) system built to support a fleet-mechanic assistant AI agent. The system enables the agent to reference and reason over service manuals, PDFs, and domain-specific documentation to respond to queries, provide recommendations, and assist maintenance workflows.

### Why this project matters  
- Mechanics often need fast access to relevant documentation.  
- The RAG approach allows combining knowledge from large language models with factual external documents to improve accuracy and relevance.  
- Built for the Pasco County Sheriff’s Office fleet environment, but designed to be generalizable to similar documentation-driven domains.  

---

## Features  
- Ingest and index PDF manuals and documents for retrieval.  
- Use document processing utilities to parse, chunk, and store content in a structured database.  
- Query interface (`app.py`) to ask questions and receive AI-enhanced answers with references.  
- SQLite-based persistent storage (`db_sqlite.py`, `manual_database.py`).  
- Tools to inspect database integrity (`db_check.py`).  
- Vision integration (`gpt_vision.py`) for image-rich documents or diagrams.  
- Modular utilities (`pdf_utils.py`, `processing_manual.py`) to support preprocessing.  
- Easy to extend with new document sets.  

---

## Architecture & Components  

### Document Ingestion & Processing  
- **`pdf_utils.py`** — Parses PDF files and extracts text/images.  
- **`processing_manual.py`** — Prepares manuals for indexing (chunking, extraction, metadata, etc.).  

### Database / Index Layer  
- **`manual_database.py`** — Schema/model for storing document chunks.  
- **`db_sqlite.py`** — SQLite implementation.  
- **`db_check.py`** — DB integrity and quick diagnostic tool.  

### Query & AI Interaction  
- **`app.py`** — API server endpoint for querying the RAG pipeline.  
- **`gpt_vision.py`** — Optional image/diagram understanding layer.  

---

## Getting Started  

### Prerequisites  
- Python 3.x  
- Pip  
- LLM or vision model API keys (if required)  

---

### Installation  
```bash
git clone https://github.com/CasEverling/DocumentReferenceRAG.git
cd DocumentReferenceRAG
