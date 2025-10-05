CREATE DATABASE postgres_rag_task;

\connect postgres_rag_task;

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    project_name TEXT,
    industry TEXT,
    overview TEXT,
    responsible_person TEXT,
    embedding VECTOR(1024)
);