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
DocumentReferenceRAG is a Retrieval-Augmented Generation (RAG) system built to support a fleet-mechanic assistant AI agent. It processes, indexes, and retrieves information from service manuals, PDFs, and technical documentation to provide accurate, reference-backed answers to queries from mechanics and technicians.

---

## Features
- Ingest and index PDF manuals and documents for retrieval  
- Chunking and metadata extraction for better search quality  
- Query interface (`app.py`) with RAG-enhanced responses  
- SQLite-based document database  
- Vision-based extraction for image-heavy manuals (`gpt_vision.py`)  
- Diagnostics tools for database health (`db_check.py`)  
- Modular and easily extensible architecture

---

## Architecture & Components

### Document Ingestion & Processing
- **`pdf_utils.py`** — Extracts text, metadata, and images from PDFs  
- **`processing_manual.py`** — Handles chunking, preprocessing, and indexing workflow  

### Database Layer
- **`manual_database.py`** — Document schema and database operations  
- **`db_sqlite.py`** — SQLite engine implementation  
- **`db_check.py`** — DB integrity checker

### Query & AI Pipeline
- **`app.py`** — API endpoint for querying the RAG system  
- **`gpt_vision.py`** — Vision integration for diagrams and image-based references

---

## Getting Started

### Prerequisites
- Python 3.x  
- Pip  
- (Optional) LLM / Vision model API keys

---

## Installation

```bash
git clone https://github.com/CasEverling/DocumentReferenceRAG.git
cd DocumentReferenceRAG
