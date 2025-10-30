[![Owner](https://img.shields.io/badge/Owner-stoyanvalchev-emeraldgreen)](https://github.com/stoyanvalchev)

# RAG Chatbot with PostgreSQL + pgvector + Cohere

This project implements a **retrieval-augmented generation (RAG) chatbot** using:

- **PostgreSQL with pgvector** for vector storage
- **Cohere** for embeddings, reranking, and generation
- **Docker** for orchestration and setup

With Docker Compose, the database is fully set up automatically.

---

## Requirements

```bash
pip install -r requirements.txt
```

---

## Setup and Run

### 1. Start the database with Docker Compose:

```bash
docker-compose up -d
```

The database is automatically created and initialized via the `init.sql` script included in the Docker setup.

### 2. Run the data extraction script and generate embeddings:

```bash
python data_extraction.py
```

This script extracts the data from `projects_data.md`, loads it into the PostgreSQL database and generates embeddings.

The file fills the `embedding` column of the database with multidimensional vectors using a 1024-dimensional Cohere embedding model.
For future work, I plan on experimenting with different embedding models and dimensionalities to further improve retrieval quality.

### 3. Start the chatbot application:

Launch the chatbot console app:

```bash
python console_app.py
```

You should see:

```
Welcome to the Stoyan Valchev's Info Chatbot! Type 'q', 'quit', or 'exit' to quit.
```

Type your query and press Enter. The chatbot will respond using both the database content and external knowledge.

## AI Prompts

All of the tested prompts with the answers of the chat are saved in `ai_prompts.md`.

## Optimization of hyperparameters

To improve relevance and response quality, a grid search was conducted over key hyperparameters such as:

- Number of retrieved documents (top_k)

- Number of reranked documents

- Generation model

- Maximum token count

The optimization process and evaluation metric are detailed in `hyperparameter_optimization.ipynb`, where the best-performing configuration was selected based on a custom accuracy metric.

An extra function for better performance was added to improve the relevance and quality of retrieved documents.

A reranking function was also implemented to improve the performance of the retrieval system by reordering the initially retrieved documents based on their semantic relevance.

## Conclusion

I found 15 optimal hyperparameter combinations for the model. Based on testing these, I observed that the model tends to cut off its sentences when `max_tokens` is set below 200. For tasks requiring long lists of data, a higher number of retrieved documents consistently improves performance. The number of reranked documents generally aligns with the `top_k` parameter. Overall, the `command-r-08-2024` model outperforms the other one that is made specifically for RAG applications across all tested combinations.

