# Neo4j Graph Retrieval Agent

This project implements a Graph Retrieval Agent that processes meeting notes and stores them in both a Neo4j graph database and Pinecone vector database for intelligent retrieval and analysis using a hybrid RAG (Retrieval Augmented Generation) approach.

## Features

- **Document Processing and Graph Creation**
  - Automated meeting notes analysis
  - Graph database storage in Neo4j
  - Vector embeddings storage in Pinecone
  - Relationship extraction from meeting notes
  
- **Hybrid RAG System**
  - Combined vector and graph-based retrieval
  - Semantic search using OpenAI embeddings
  - Structured relationship queries via Neo4j
  - Comprehensive response generation
  
- **Intelligent Query Processing**
  - Natural language query understanding
  - Context-aware response generation
  - Source attribution for transparency
  - Multi-source information synthesis

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your credentials:
```env
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=us-east-1-aws
```

3. Make sure Neo4j is running locally or update the connection details in the `.env` file.

## Project Structure

### Core Files
- `graph_agent.py`: Main implementation of the Graph Retrieval Agent
- `database.py`: Neo4j database connection and operations
- `models.py`: Data models for nodes and relationships
- `utils.py`: Utility functions for text processing

### RAG System Files
- `vectorize_store.py`: Vector storage implementation for meeting notes
- `query_vectors.py`: Vector search testing and validation
- `rag_with_vectors.py`: Integrated RAG system combining graph and vector search

### Analysis Files
- `add_meeting_notes.py`: Process and add new meeting notes
- `query_early_discussions.py`: Query historical discussions
- `run_rag_examples.py`: Example queries using the RAG system

## Requirements

### System Requirements
- Python 3.8+
- Neo4j Database
- Pinecone Account (Free Tier or higher)
- OpenAI API access

### Python Dependencies
```
neo4j
openai
pinecone-client
python-dotenv
```

## Usage

1. **Add Meeting Notes**
```bash
python add_meeting_notes.py path/to/meeting/notes.txt
```

2. **Vectorize Meeting Notes**
```bash
python vectorize_store.py
```

3. **Query the System**
```bash
python rag_with_vectors.py
```

## Query Examples

The system can handle various types of queries:
- Requirements analysis
- Timeline inquiries
- Stakeholder identification
- Topic exploration
- Relationship discovery

## Architecture

The system uses a hybrid approach combining:
1. **Neo4j Graph Database**
   - Stores structured relationships
   - Manages entity connections
   - Enables graph traversal queries

2. **Pinecone Vector Database**
   - Stores document embeddings
   - Enables semantic search
   - Supports similarity matching

3. **OpenAI Integration**
   - Generates embeddings
   - Extracts keywords
   - Produces natural language responses




