DocumentReferenceRAG

RAG System developed for the Fleet-Mechanic Assistant AI Agent at the Pasco County Sheriff’s Office

Table of Contents

Project Overview

Features

Architecture & Components

Getting Started

Prerequisites

Installation

Configuration

Running the Application

Usage

Project Structure

Contributing

License

Acknowledgements

Project Overview

DocumentReferenceRAG is a Retrieval-Augmented Generation (RAG) system built to support a fleet-mechanic assistant AI agent. The system enables the agent to reference and reason over service manuals, PDFs, and domain-specific documentation to respond to queries, provide recommendations, and assist maintenance workflows.

Why this project matters

Mechanics often need fast access to relevant documentation.

The RAG approach allows combining knowledge from large language models with factual external documents to improve accuracy and relevance.

Built for the Pasco County Sheriff’s Office fleet environment, but designed to be generalizable to similar documentation-driven domains.

Features

Ingest and index PDF manuals and documents for retrieval.

Use document processing utilities to parse, chunk, and store content in a database.

Query interface (app.py) to ask questions and receive AI-enhanced answers with references.

SQLite / manual database support via scripts (db_sqlite.py, manual_database.py, db_check.py).

Vision integration (gpt_vision.py) for image-rich documents/materials.

Modular utilities (pdf_utils.py, processing_manual.py) to support preprocessing.

Easy to extend with new document sets.

Architecture & Components

Below is a high-level component breakdown:

Document Ingestion & Processing

pdf_utils.py: utilities to parse PDF files, extract text/images.

processing_manual.py: orchestrates manual/document preprocessing (chunking, metadata).

Database / Index Layer

manual_database.py: defines the database schema/model for storing manual/document chunks.

db_sqlite.py : SQLite implementation for persistence.

db_check.py: health/check scripts verifying database integrity.

API / Query Interface

app.py: HTTP API (likely using a lightweight framework) to receive queries and return responses referencing documents.

gpt_vision.py: handles vision-based document/image queries (e.g., diagrams in manuals).

Requirements

requirements.txt: lists Python dependencies.

Getting Started
Prerequisites

Python 3.x (recommend latest stable)

Pip (or preferred Python package manager)

APIs/credentials of any external LLM service (if used)

PDF manuals/documentation to ingest

Installation

Clone the repository:

git clone https://github.com/CasEverling/DocumentReferenceRAG.git  
cd DocumentReferenceRAG  


Create a virtual environment (optional but recommended):

python -m venv venv  
source venv/bin/activate      # Unix/macOS  
venv\Scripts\activate         # Windows  


Install dependencies:

pip install -r requirements.txt  

Configuration

Add your document files under the data/ directory (or adjust config).

Update database connection settings (in db_sqlite.py or other config file).

Set environment variables or config file for LLM/vision service keys.

(Optional) Adjust chunk size, indexing parameters, or document parsing thresholds in processing_manual.py.

Running the Application

To preprocess documents:

python processing_manual.py  


To start the API server:

python app.py  


To perform a basic DB check:

python db_check.py  

Usage

Once the API server is running, you can send a query (via HTTP POST/GET) to the endpoint defined in app.py. The system will:

Retrieve relevant document chunks from the database.

Pass them (alongside the query) to the LLM for answer generation.

Return the answer along with reference metadata (document name, page/chunk).

Example
curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"question": "How do I replace a brake pad on vehicle model X?"}'


Response:

{
  "answer": "You should first jack up the vehicle, remove the wheel, inspect the caliper pins…",
  "references": [
    {"document": "BrakeManual_ModelX.pdf", "page": 42, "chunk_id": 7}
  ]
}

Project Structure
DocumentReferenceRAG/
├── app.py                  # API interface  
├── db_check.py             # Database integrity / status checker  
├── db_sqlite.py            # SQLite DB implementation  
├── gpt_vision.py           # Vision/diagram processing module  
├── manual_database.py      # Manual/document‐chunk model and ingestion  
├── pdf_utils.py            # PDF parsing utilities  
├── processing_manual.py    # Document preprocessing orchestration  
├── requirements.txt        # Python dependencies  
├── data/                   # Directory to store raw manuals/docs  
└── README.md               # (this file)  

Contributing

Contributions are very welcome! Here’s how you can help:

Fork the repository and create a new branch for your feature or fix.

Ensure new code is well-documented and tested.

Submit a pull request describing your changes.

Please adhere to the project’s coding style and maintain modularity.

License

Specify the license here (e.g., MIT License).

MIT © 2025 [Your Name / Organization]

Acknowledgements

Thanks to the Pasco County Sheriff’s Office for enabling the fleet-mechanic use case.

Inspirations: Retrieval-Augmented Generation (RAG) frameworks, document-processing pipelines.

Many thanks to open-source libraries referenced in requirements.txt
