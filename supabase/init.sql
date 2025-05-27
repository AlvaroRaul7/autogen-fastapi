-- Enable the pgvector extension
create extension if not exists vector;

-- Create the documents table
create table if not exists documents (
    id bigint primary key generated always as identity,
    content text not null,
    embedding vector(1536), -- OpenAI embeddings are 1536 dimensions
    metadata jsonb,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Create an index for similarity search
create index on documents using ivfflat (embedding vector_cosine_ops); 