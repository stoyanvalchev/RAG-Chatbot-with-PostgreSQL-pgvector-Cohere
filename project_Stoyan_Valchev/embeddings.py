import cohere
from dotenv import load_dotenv
import os
import psycopg2
import pandas as pd

load_dotenv()

api_key = os.getenv('COHERE_API_KEY')
co = cohere.Client(api_key)

db_config = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT')),
}

conn = psycopg2.connect(**db_config)
cursor = conn.cursor()

cursor.execute("SELECT id, project_name, industry, overview, responsible_person FROM public.projects")
rows = cursor.fetchall()


texts = [f"{project_name} ({industry}), {responsible_person}: {overview}" 
         for _, project_name, industry, overview, responsible_person in rows]

response = co.embed(texts=texts, model='small')
embeddings = response.embeddings

for (project_id, *_), embedding in zip(rows, embeddings):
    cursor.execute(
        "UPDATE public.projects SET embedding = %s WHERE id = %s",
        (embedding, project_id)
    )
conn.commit()
