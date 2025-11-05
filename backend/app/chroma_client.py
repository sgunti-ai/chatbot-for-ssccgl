import chromadb
from sentence_transformers import SentenceTransformer
import os
from typing import List, Dict, Optional

class ChromaClient:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        # Use persistent client for production
        self.client = chromadb.PersistentClient(path="./chroma_db")
        # For development, you can use HttpClient to connect to ChromaDB container
        # self.client = chromadb.HttpClient(host="localhost", port=8001)
        
        self.collection = self.client.get_or_create_collection(
            name="ssc_questions",
            metadata={"description": "SSC Exam Questions Database"}
        )
    
    def insert_question(self, question_data: Dict, namespace: str = "ssc-questions"):
        """Insert a single question into ChromaDB"""
        embedding = self.model.encode([question_data['full_text']]).tolist()[0]
        
        self.collection.add(
            documents=[question_data['full_text']],
            embeddings=[embedding],
            metadatas=[{
                "text": question_data['text'],
                "options": question_data.get('options', []),
                "correct_answer": question_data.get('correct_answer', ''),
                "subject": question_data.get('subject', 'General'),
                "year": question_data.get('year', 2024),
                "paper_type": question_data.get('paper_type', 'CGL'),
                "question_id": question_data['id']
            }],
            ids=[question_data['id']]
        )
    
    def batch_insert_questions(self, questions: List[Dict], namespace: str = "ssc-questions"):
        """Batch insert multiple questions into ChromaDB"""
        if not questions:
            return
        
        documents = []
        embeddings = []
        metadatas = []
        ids = []
        
        for question in questions:
            documents.append(question['full_text'])
            embeddings.append(self.model.encode([question['full_text']]).tolist()[0])
            metadatas.append({
                "text": question['text'],
                "options": question.get('options', []),
                "correct_answer": question.get('correct_answer', ''),
                "subject": question.get('subject', 'General'),
                "year": question.get('year', 2024),
                "paper_type": question.get('paper_type', 'CGL'),
                "question_id": question['id']
            })
            ids.append(question['id'])
        
        # Insert in batches to avoid large payloads
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            end_idx = min(i + batch_size, len(documents))
            
            self.collection.add(
                documents=documents[i:end_idx],
                embeddings=embeddings[i:end_idx],
                metadatas=metadatas[i:end_idx],
                ids=ids[i:end_idx]
            )
            
            print(f"Inserted batch {i//batch_size + 1}: {end_idx - i} questions")
    
    def semantic_search(self, query: str, top_k: int = 5, subject: Optional[str] = None):
        """Semantic search in ChromaDB"""
        query_embedding = self.model.encode([query]).tolist()[0]
        
        if subject:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where={"subject": {"$eq": subject}}
            )
        else:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
        
        matches = []
        if results['documents'] and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                matches.append({
                    "question": results['metadatas'][0][i].get('text', results['documents'][0][i]),
                    "options": results['metadatas'][0][i].get('options', []),
                    "correct_answer": results['metadatas'][0][i].get('correct_answer', ''),
                    "subject": results['metadatas'][0][i].get('subject', ''),
                    "similarity_score": 1 - results['distances'][0][i] if 'distances' in results and results['distances'][0] else 0.8,
                    "question_id": results['metadatas'][0][i].get('question_id', results['ids'][0][i])
                })
        
        return matches
    
    def search_by_subject(self, query: str, subject: str, top_k: int = 5):
        """Search within specific subject"""
        return self.semantic_search(query, top_k, subject)
    
    def get_collection_stats(self):
        """Get statistics about the collection"""
        return self.collection.count()
    
    def delete_question(self, question_id: str):
        """Delete a question by ID"""
        self.collection.delete(ids=[question_id])
    
    def update_question(self, question_id: str, question_data: Dict):
        """Update a question"""
        # Delete old and insert new
        self.delete_question(question_id)
        self.insert_question(question_data)
