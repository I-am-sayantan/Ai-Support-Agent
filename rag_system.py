"""
RAG (Retrieval-Augmented Generation) System using FAISS and OpenAI Embeddings

This module handles:
- Document processing and chunking
- Embedding generation using Azure OpenAI
- Vector storage using FAISS
- Semantic search and retrieval
"""

import os
import json
import pickle
from typing import List, Dict, Tuple
import numpy as np
from openai import AzureOpenAI
import faiss
from pathlib import Path


class DocumentChunker:
    """Split documents into chunks for embedding"""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """Split text into overlapping chunks"""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            chunk = {
                'text': chunk_text,
                'metadata': metadata or {},
                'start_idx': i,
                'end_idx': i + len(chunk_words)
            }
            chunks.append(chunk)
        
        return chunks


class EmbeddingGenerator:
    """Generate embeddings using Azure OpenAI"""
    
    def __init__(self, api_key: str, azure_endpoint: str, api_version: str = "2024-12-01-preview", 
                 embedding_deployment: str = None):
        self.client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint
        )
        # Use provided deployment or default to text-embedding-ada-002
        # For Azure, this should be the deployment name, not the model name
        self.embedding_model = embedding_deployment or os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single text"""
        response = self.client.embeddings.create(
            input=text,
            model=self.embedding_model
        )
        return np.array(response.data[0].embedding, dtype=np.float32)
    
    def generate_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts"""
        embeddings = []
        # Process in batches of 100 to avoid rate limits
        batch_size = 100
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = self.client.embeddings.create(
                input=batch,
                model=self.embedding_model
            )
            batch_embeddings = [np.array(item.embedding, dtype=np.float32) for item in response.data]
            embeddings.extend(batch_embeddings)
        
        return np.array(embeddings)


class FAISSVectorStore:
    """FAISS vector store for similarity search"""
    
    def __init__(self, dimension: int = 1536):
        # text-embedding-ada-002 produces 1536-dimensional vectors
        self.dimension = dimension
        # Using L2 distance for similarity
        self.index = faiss.IndexFlatL2(dimension)
        self.chunks = []
    
    def add_embeddings(self, embeddings: np.ndarray, chunks: List[Dict]):
        """Add embeddings to the index"""
        self.index.add(embeddings)
        self.chunks.extend(chunks)
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[Dict, float]]:
        """Search for k most similar chunks"""
        # Reshape for FAISS
        query_embedding = query_embedding.reshape(1, -1)
        
        # Search
        distances, indices = self.index.search(query_embedding, k)
        
        # Return chunks with distances (lower distance = more similar)
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.chunks):
                results.append((self.chunks[idx], float(distance)))
        
        return results
    
    def save(self, index_path: str, chunks_path: str):
        """Save index and chunks to disk"""
        faiss.write_index(self.index, index_path)
        with open(chunks_path, 'wb') as f:
            pickle.dump(self.chunks, f)
    
    def load(self, index_path: str, chunks_path: str):
        """Load index and chunks from disk"""
        self.index = faiss.read_index(index_path)
        with open(chunks_path, 'rb') as f:
            self.chunks = pickle.load(f)


class RAGSystem:
    """Complete RAG system integrating all components"""
    
    def __init__(self, api_key: str, azure_endpoint: str, api_version: str = "2024-12-01-preview",
                 embedding_deployment: str = None):
        self.chunker = DocumentChunker(chunk_size=500, overlap=50)
        self.embedding_generator = EmbeddingGenerator(api_key, azure_endpoint, api_version, embedding_deployment)
        self.vector_store = None  # Will be initialized after first embedding
        self.documents_processed = 0
    
    def process_document(self, file_path: str) -> int:
        """Process a single document and add to vector store"""
        # Read document
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Create metadata
        metadata = {
            'source': os.path.basename(file_path),
            'path': file_path
        }
        
        # Chunk document
        chunks = self.chunker.chunk_text(text, metadata)
        
        # Generate embeddings
        chunk_texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embedding_generator.generate_embeddings_batch(chunk_texts)
        
        # Initialize vector store with correct dimension on first document
        if self.vector_store is None:
            embedding_dim = embeddings.shape[1]
            print(f"  Detected embedding dimension: {embedding_dim}")
            self.vector_store = FAISSVectorStore(dimension=embedding_dim)
        
        # Add to vector store
        self.vector_store.add_embeddings(embeddings, chunks)
        
        self.documents_processed += 1
        return len(chunks)
    
    def process_documents_from_directory(self, directory: str) -> Dict[str, int]:
        """Process all .txt files in a directory"""
        results = {}
        directory_path = Path(directory)
        
        for file_path in directory_path.glob('*.txt'):
            print(f"Processing {file_path.name}...")
            chunk_count = self.process_document(str(file_path))
            results[file_path.name] = chunk_count
            print(f"  → Created {chunk_count} chunks")
        
        return results
    
    def retrieve(self, query: str, k: int = 5) -> List[Dict]:
        """Retrieve relevant chunks for a query"""
        # Generate query embedding
        query_embedding = self.embedding_generator.generate_embedding(query)
        
        # Search vector store
        results = self.vector_store.search(query_embedding, k)
        
        # Format results
        retrieved_chunks = []
        for chunk, distance in results:
            retrieved_chunks.append({
                'text': chunk['text'],
                'source': chunk['metadata'].get('source', 'unknown'),
                'relevance_score': 1 / (1 + distance)  # Convert distance to similarity score
            })
        
        return retrieved_chunks
    
    def save_index(self, index_dir: str = "rag_index"):
        """Save the vector index to disk"""
        os.makedirs(index_dir, exist_ok=True)
        index_path = os.path.join(index_dir, "faiss.index")
        chunks_path = os.path.join(index_dir, "chunks.pkl")
        
        self.vector_store.save(index_path, chunks_path)
        
        # Save metadata
        metadata = {
            'documents_processed': self.documents_processed,
            'total_chunks': len(self.vector_store.chunks)
        }
        with open(os.path.join(index_dir, "metadata.json"), 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def load_index(self, index_dir: str = "rag_index"):
        """Load the vector index from disk"""
        index_path = os.path.join(index_dir, "faiss.index")
        chunks_path = os.path.join(index_dir, "chunks.pkl")
        
        # Initialize vector store if not already done
        if self.vector_store is None:
            # We'll get the dimension from the loaded index
            loaded_index = faiss.read_index(index_path)
            self.vector_store = FAISSVectorStore(dimension=loaded_index.d)
            self.vector_store.index = loaded_index
            
            # Load chunks
            with open(chunks_path, 'rb') as f:
                self.vector_store.chunks = pickle.load(f)
        else:
            self.vector_store.load(index_path, chunks_path)
        
        # Load metadata
        with open(os.path.join(index_dir, "metadata.json"), 'r') as f:
            metadata = json.load(f)
            self.documents_processed = metadata['documents_processed']


def build_rag_index(documents_dir: str, index_dir: str = "rag_index"):
    """Build RAG index from documents directory"""
    from dotenv import load_dotenv
    load_dotenv()
    
    # Initialize RAG system
    rag = RAGSystem(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
        embedding_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    )
    
    # Process documents
    print(f"\n{'='*60}")
    print("Building RAG Index")
    print('='*60)
    results = rag.process_documents_from_directory(documents_dir)
    
    # Save index
    print(f"\nSaving index to {index_dir}...")
    rag.save_index(index_dir)
    
    # Summary
    print(f"\n{'='*60}")
    print("Index Build Complete!")
    print('='*60)
    print(f"Documents processed: {rag.documents_processed}")
    print(f"Total chunks: {len(rag.vector_store.chunks)}")
    print(f"Index saved to: {index_dir}")
    print('='*60)
    
    return rag


if __name__ == "__main__":
    # Build the index
    documents_dir = "documents"
    rag_system = build_rag_index(documents_dir)
    
    # Test retrieval
    print("\n" + "="*60)
    print("Testing Retrieval")
    print("="*60)
    
    test_queries = [
        "How many remote work days are allowed?",
        "What is the API rate limit?",
        "What are the parental leave benefits?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 60)
        results = rag_system.retrieve(query, k=3)
        for i, result in enumerate(results, 1):
            print(f"\n{i}. [Source: {result['source']}] (Score: {result['relevance_score']:.3f})")
            print(f"   {result['text'][:200]}...")
