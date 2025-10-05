from cohere import Client
import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API keys
co = Client(os.getenv("COHERE_API_KEY"))


# DB connection
db_config = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT')),
}

conn = psycopg2.connect(**db_config)
cursor = conn.cursor()


def embed_text(text: str, model: str):
    resp = co.embed(texts=[text], model=model, input_type="search_query")
    return resp.embeddings[0]

def retrieve_similar(query: str, top_k: int, embedding_model: str):
    query_embedding = embed_text(query, embedding_model)
    cursor.execute(
        """
        SELECT id, project_name, industry, overview, responsible_person
        FROM public.projects
        ORDER BY embedding <#> %s::vector
        LIMIT %s;
        """,
        (query_embedding, top_k)
    )
    return cursor.fetchall()

def chatbot_response(user_message: str, context_docs, generation_model: str, max_tokens: int):
    context = "\n\n".join(
        f"{name} ({industry}), {person}: {overview}"
        for _, name, industry, overview, person in context_docs
    )

    prompt = f"""
You are a knowledgeable assistant. Use the following project descriptions to answer the question.

Project descriptions:
{context}

Question:
{user_message}  

Answer concisely and informatively:
"""

    response = co.chat(
        model=generation_model,
        message=prompt,
        max_tokens=max_tokens,
    )

    return response.text.strip()


def rerank_docs(query, docs, rerank_n: int):
    doc_texts = [f"{d[1]} ({d[2]}), {d[4]}: {d[3]}" for d in docs]
    rerank_response = co.rerank(
        query=query,
        documents=doc_texts,
        top_n=rerank_n,
        model="rerank-v3.5"
    )
    reranked = sorted(
        zip(docs, rerank_response.results),
        key=lambda x: x[1].relevance_score,
        reverse=True
    )
    return [item[0] for item in reranked[:rerank_n]]


# Console loop
if __name__ == "__main__":

    print("Welcome to the Stoyan Valchev's Info Chatbot! Type 'q', 'quit', or 'exit' to quit.")
    
    embedding_model = "small"
    generation_model = "command-r-08-2024"
    top_k = 6
    rerank_n = 4
    max_tokens = 200
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['q', 'exit', 'quit']:
            break

        similar_docs = retrieve_similar(user_input, top_k, embedding_model)
        if rerank_n <= top_k:
            similar_docs = rerank_docs(user_input, similar_docs, rerank_n)

        answer = chatbot_response(user_input, similar_docs, generation_model, max_tokens)
        print(f"Chat: {answer}")
    
    cursor.close()
    conn.close()
    print("Goodbye!")
