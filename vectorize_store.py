import os
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

class VectorStore:
    def __init__(self, force_recreate=True):
        # Initialize OpenAI client
        self.openai_client = OpenAI()
        
        # Initialize Pinecone
        pinecone_api_key = os.getenv('PINECONE_API_KEY')
        pinecone_env = os.getenv('PINECONE_ENVIRONMENT')
        
        if not pinecone_api_key or not pinecone_env:
            raise ValueError("Pinecone API key and environment must be set in .env file")
            
        print(f"Using Pinecone environment: {pinecone_env}")
        self.pc = Pinecone(api_key=pinecone_api_key)
        
        # Get or create index
        self.index_name = "meeting-analysis"
        try:
            # Check if index exists
            indexes = self.pc.list_indexes()
            
            # Delete existing index if force_recreate is True
            if self.index_name in indexes.names() and force_recreate:
                print(f"Deleting existing index: {self.index_name}")
                self.pc.delete_index(self.index_name)
                # Wait a moment after deletion
                time.sleep(10)
            
            # Create new index if it doesn't exist
            if self.index_name not in self.pc.list_indexes().names():
                print(f"Creating new index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=1536,  # dimensionality of text-embedding-ada-002
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
                # Wait for index to be ready
                print("Waiting for index to be ready...")
                time.sleep(10)  # Initial wait
                while not self.pc.describe_index(self.index_name).status['ready']:
                    print("Still waiting for index to be ready...")
                    time.sleep(5)
            else:
                print(f"Using existing index: {self.index_name}")
            
            self.index = self.pc.Index(self.index_name)
            print("Successfully connected to Pinecone index")
            
        except Exception as e:
            print(f"Error initializing Pinecone: {str(e)}")
            raise

    def get_embedding(self, text):
        """Get embeddings for a piece of text using OpenAI's API"""
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            raise

    def chunk_text(self, text, chunk_size=1000):
        """Split text into smaller chunks"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            current_chunk.append(word)
            current_size += len(word) + 1  # +1 for space
            
            if current_size >= chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_size = 0
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
            
        return chunks

    def vectorize_and_store(self, file_path):
        """Read the analysis file, vectorize its content, and store in Pinecone"""
        try:
            # Read the analysis file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Get file metadata
            file_name = os.path.basename(file_path)
            creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
            
            print(f"Processing file: {file_name}")
            print(f"File creation time: {creation_time}")
            
            # Split content into chunks
            chunks = self.chunk_text(content)
            print(f"Split content into {len(chunks)} chunks")
            
            # Process each chunk
            vectors = []
            for i, chunk in enumerate(chunks):
                print(f"Processing chunk {i+1}/{len(chunks)}")
                # Get embedding for the chunk
                embedding = self.get_embedding(chunk)
                
                # Prepare metadata
                metadata = {
                    "file_name": file_name,
                    "creation_time": creation_time.isoformat(),
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "content": chunk[:1000]  # Limit content length to avoid metadata size issues
                }
                
                # Add to vectors list
                vectors.append({
                    "id": f"{file_name}_{i}",
                    "values": embedding,
                    "metadata": metadata
                })
                
                # Add a small delay between embeddings
                time.sleep(0.5)
            
            # Upsert vectors in smaller batches
            batch_size = 25  # Reduced batch size
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                print(f"Upserting batch {i//batch_size + 1}/{(len(vectors) + batch_size - 1)//batch_size}")
                try:
                    self.index.upsert(vectors=batch)
                    # Longer delay between batches
                    time.sleep(2)
                except Exception as e:
                    print(f"Error upserting batch: {str(e)}")
                    raise
            
            print(f"Successfully vectorized and stored {len(chunks)} chunks from {file_name}")
            
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            raise

def main():
    try:
        # Initialize vector store with force_recreate=True to ensure a fresh start
        print("Initializing vector store...")
        vector_store = VectorStore(force_recreate=True)
        
        # Get the latest analysis file
        analysis_dir = "meeting_analysis"
        analysis_files = [f for f in os.listdir(analysis_dir) if f.endswith('.txt')]
        if not analysis_files:
            print("No analysis files found")
            return
        
        # Sort by creation time and get the latest
        latest_file = max(
            analysis_files,
            key=lambda f: os.path.getctime(os.path.join(analysis_dir, f))
        )
        file_path = os.path.join(analysis_dir, latest_file)
        
        # Vectorize and store the content
        print(f"\nProcessing file: {latest_file}")
        vector_store.vectorize_and_store(file_path)
        
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()
