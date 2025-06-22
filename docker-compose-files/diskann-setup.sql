-- List all tables in the current database (public schema is common)
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';


CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name TEXT,
    description TEXT,
    price NUMERIC(10, 2),
    in_stock BOOLEAN,
    description_embedding VECTOR(1536) -- Change dimension based on your model (e.g., 1536 for text-embedding-ada-002)
);

-- Add a generated column to automatically create embeddings on insert/update
-- This is experimental, but very powerful for a demo!
ALTER TABLE products
ALTER COLUMN description_embedding SET GENERATED ALWAYS AS (
    azure_ai.create_embeddings(
        azure_ai.azure_openai_embedding_args('text-embedding-ada-002', description) -- Use your model name and column
    )
) STORED;




CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name TEXT,
    description TEXT,
    price NUMERIC(10, 2),
    in_stock BOOLEAN,
    description_embedding VECTOR(1536) -- Change dimension based on your model (e.g., 1536 for text-embedding-ada-002)
);

-- Add a generated column to automatically create embeddings on insert/update
-- This is experimental, but very powerful for a demo!
ALTER TABLE products
ALTER COLUMN description_embedding SET GENERATED ALWAYS AS (
    azure_ai.create_embeddings(
        azure_ai.azure_openai_embedding_args('text-embedding-ada-002', description) -- Use your model name and column
    )
) STORED;


Insert 

INSERT INTO products (name, description, price, in_stock) VALUES
('Premium Smartwatch', 'A sleek smartwatch with advanced health tracking and long battery life.', 299.99, TRUE),
('Wireless Noise-Cancelling Headphones', 'Immersive audio experience with superior noise cancellation for travel and work.', 199.99, TRUE),
('Compact Digital Camera', 'Capture stunning photos and 4K videos with this easy-to-use digital camera.', 450.00, FALSE),
('Ergonomic Office Chair', 'Supportive and comfortable chair designed for long hours of work, adjustable.', 350.00, TRUE),
('High-Speed External SSD', 'Fast and portable storage solution for backing up large files and gaming.', 150.00, TRUE),
('Smart LED Light Bulbs (4-pack)', 'Control your home lighting with your voice or smartphone app, energy efficient.', 45.00, TRUE),
('Robot Vacuum Cleaner', 'Automated cleaning for your home, smart navigation and powerful suction.', 499.00, FALSE),
('Yoga Mat Pro', 'Thick, non-slip mat for comfortable and stable yoga and fitness workouts.', 35.00, TRUE),
('Portable Espresso Maker', 'Enjoy fresh espresso on the go, perfect for camping and travel.', 99.00, TRUE);


CREATE INDEX idx_products_diskann ON products USING diskann (description_embedding VECTOR_COSINE_OPS);

-- For larger datasets, consider tuning parameters (e.g., higher l_value_ib for better quality)
-- CREATE INDEX idx_products_diskann_tuned ON products USING diskann (description_embedding VECTOR_COSINE_OPS)
-- WITH (max_neighbors = 64, l_value_ib = 200, pq_param_num_chunks = 384); -- Adjust pq_param_num_chunks for 1536 / 4 = 384


-- Get embedding for your query
SELECT azure_ai.create_embeddings(
    azure_ai.azure_openai_embedding_args('text-embedding-ada-002', 'gadgets for smart home')
) AS query_vector;

-- Copy the resulting vector from the above output. Let's assume it's `[...your_query_vector...]`

-- Perform similarity search (top 3 most similar)
SELECT
    product_id,
    name,
    description,
    price,
    description_embedding <=> '[...your_query_vector...]' AS similarity_score
FROM
    products
ORDER BY
    similarity_score
LIMIT 3;


-- Find in-stock products similar to "fitness equipment" and under $100
-- First, get embedding for "fitness equipment"
SELECT azure_ai.create_embeddings(
    azure_ai.azure_openai_embedding_args('text-embedding-ada-002', 'fitness equipment')
) AS query_vector;

-- Let's say the query vector is `[...fitness_query_vector...]`

SELECT
    product_id,
    name,
    description,
    price,
    description_embedding <=> '[...fitness_query_vector...]' AS similarity_score
FROM
    products
WHERE
    in_stock = TRUE AND price < 100.00
ORDER BY
    similarity_score
LIMIT 3;



-- Set search behavior to 'off' to force a sequential scan if no other index is used
SET diskann.iterative_search TO 'off';

EXPLAIN ANALYZE
SELECT
    product_id,
    name,
    description,
    description_embedding <=> '[...your_query_vector...]' AS similarity_score
FROM
    products
ORDER BY
    similarity_score
LIMIT 3;

SET diskann.iterative_search TO 'relaxed_order'; -- Reset it for future DiskANN queries




-- First, create an HNSW index (requires pgvector extension only, which is already enabled)
-- CREATE INDEX idx_products_hnsw ON products USING hnsw (description_embedding vector_cosine_ops);

-- Then run a query using the HNSW index
-- EXPLAIN ANALYZE
-- SELECT
--     product_id,
--     name,
--     description,
--     description_embedding <=> '[...your_query_vector...]' AS similarity_score
-- FROM
--     products
-- ORDER BY
--     similarity_score
-- LIMIT 3;
-----------------------
\
-- In Azure Portal: Add 'pg_diskann', 'vector', 'azure_ai' to azure.extensions server parameter. Save.

-- In psql/Azure Data Studio:
CREATE EXTENSION IF NOT EXISTS pg_diskann CASCADE;
CREATE EXTENSION IF NOT EXISTS azure_ai;

-- Set your Azure OpenAI endpoint and API key
-- Replace with your actual endpoint and key
SELECT azure_ai.set_setting('azure_openai.endpoint', 'https://<your-openai-resource-name>.openai.azure.com/');
SELECT azure_ai.set_setting('azure_openai.subscription_key', '<YOUR_AZURE_OPENAI_API_KEY>');

-- Verify settings (optional)
SELECT azure_ai.get_setting('azure_openai.endpoint');
SELECT azure_ai.get_setting('azure_openai.subscription_key');

=======
2. Create Table with Generated Column (Corrected create_embeddings call):

The azure_openai.create_embeddings function takes the deployment_name (the name you gave your embedding model deployment in Azure OpenAI Studio, e.g., 'text-embedding-deployment' or 'text-embedding-ada-002') and the input text.

SQL

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name TEXT,
    description TEXT,
    price NUMERIC(10, 2),
    in_stock BOOLEAN,
    -- The correct call to azure_openai.create_embeddings
    description_embedding VECTOR(1536) GENERATED ALWAYS AS (
        azure_openai.create_embeddings(
            'text-embedding-ada-002', -- **Your Azure OpenAI Deployment Name here**
            description
        )
    ) STORED
);
Explanation of the corrected GENERATED ALWAYS AS part:

azure_openai.create_embeddings: This is the correct function to call. It's located in the azure_openai schema, which is part of the azure_ai extension.
'text-embedding-ada-002': This should be the name of your deployed embedding model in Azure OpenAI Studio. When you deploy a model like text-embedding-ada-002 (Version 2) or text-embedding-3-small, you give it a deployment name. Use that exact name here.
description: This is the column from your products table whose text content you want to generate an embedding for.
3. Insert Data (Embeddings will be generated automatically):

SQL

INSERT INTO products (name, description, price, in_stock) VALUES
('Premium Smartwatch', 'A sleek smartwatch with advanced health tracking and long battery life.', 299.99, TRUE),
('Wireless Noise-Cancelling Headphones', 'Immersive audio experience with superior noise cancellation for travel and work.', 199.99, TRUE),
('Compact Digital Camera', 'Capture stunning photos and 4K videos with this easy-to-use digital camera.', 450.00, FALSE),
('Ergonomic Office Chair', 'Supportive and comfortable chair designed for long hours of work, adjustable.', 350.00, TRUE),
('High-Speed External SSD', 'Fast and portable storage solution for backing up large files and gaming.', 150.00, TRUE),
('Smart LED Light Bulbs (4-pack)', 'Control your home lighting with your voice or smartphone app, energy efficient.', 45.00, TRUE),
('Robot Vacuum Cleaner', 'Automated cleaning for your home, smart navigation and powerful suction.', 499.00, FALSE),
('Yoga Mat Pro', 'Thick, non-slip mat for comfortable and stable yoga and fitness workouts.', 35.00, TRUE),
('Portable Espresso Maker', 'Enjoy fresh espresso on the go, perfect for camping and travel.', 99.00, TRUE);
Each time you insert a row, the description_embedding column will automatically be populated by calling your Azure OpenAI embedding model.

4. Perform Similarity Search:

For queries, you'll also use azure_openai.create_embeddings to get the query vector:

SQL

-- Get embedding for your query "gadgets for smart home"
SELECT azure_openai.create_embeddings('text-embedding-ada-002', 'gadgets for smart home') AS query_vector;

-- Copy the resulting vector. Let's assume it's `'{0.1, 0.2, ..., 0.9}'` for demonstration.

-- Perform similarity search
SELECT
    product_id,
    name,
    description,
    description_embedding <=> '{0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, ... (1536 dimensions)}' AS similarity_score -- REPLACE WITH YOUR ACTUAL QUERY VECTOR
FROM
    products
ORDER BY
    similarity_score
LIMIT 3;





