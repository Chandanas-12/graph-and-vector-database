import os
from neo4j import GraphDatabase
from pinecone import Pinecone
from openai import OpenAI
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

class RAGSystem:
    def __init__(self):
        # Initialize Neo4j connection
        self.neo4j_uri = os.getenv('NEO4J_URI')
        self.neo4j_user = os.getenv('NEO4J_USER')
        self.neo4j_password = os.getenv('NEO4J_PASSWORD')
        self.neo4j_database = os.getenv('NEO4J_DATABASE')
        
        self.driver = GraphDatabase.driver(
            self.neo4j_uri,
            auth=(self.neo4j_user, self.neo4j_password)
        )
        
        # Initialize OpenAI client
        self.openai_client = OpenAI()
        
        # Initialize Pinecone
        self.pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        self.index = self.pc.Index("meeting-analysis")

    def close(self):
        self.driver.close()

    def get_embedding(self, text):
        """Get embeddings for a piece of text using OpenAI's API"""
        response = self.openai_client.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding

    def query_vector_store(self, query_text, top_k=3):
        """Query the vector store for relevant chunks"""
        # Get embedding for the query
        query_embedding = self.get_embedding(query_text)
        
        # Query Pinecone
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        return results.matches

    def query_graph_database(self, keywords):
        """Query the graph database for relevant discussions"""
        with self.driver.session(database=self.neo4j_database) as session:
            result = session.run("""
                // Find discussion points
                MATCH (meeting:Meeting)-[:HAS_POINT]->(discussion:DiscussionPoint)
                WHERE any(keyword IN $keywords 
                    WHERE toLower(discussion.content) CONTAINS keyword)
                
                // Get related topics
                OPTIONAL MATCH (topic:Topic)-[:DISCUSSED_IN]->(discussion)
                
                // Get people mentioned
                OPTIONAL MATCH (person:Person)-[:MENTIONED_IN]->(discussion)
                
                // Get adjacent discussion points for context
                OPTIONAL MATCH (meeting)-[:HAS_POINT]->(adjacent:DiscussionPoint)
                WHERE adjacent.timestamp < discussion.timestamp
                
                // Collect all context
                WITH discussion, meeting,
                     collect(DISTINCT topic.name) as topics,
                     collect(DISTINCT person.name) as people,
                     collect(DISTINCT adjacent.content) as prior_context
                
                RETURN discussion.timestamp as timestamp,
                       discussion.content as content,
                       meeting.title as meeting_title,
                       topics,
                       people,
                       prior_context
                ORDER BY timestamp
            """, keywords=keywords)
            
            return list(result)

    def generate_response(self, query, vector_results, graph_results):
        """Generate a response using OpenAI's API with both vector and graph context"""
        # Prepare context from vector store
        vector_context = "\nRelevant meeting notes:\n"
        for match in vector_results:
            vector_context += f"- {match.metadata['content']}\n"
        
        # Prepare context from graph database
        graph_context = "\nRelevant discussion points:\n"
        for record in graph_results:
            graph_context += f"Meeting: {record['meeting_title']}\n"
            graph_context += f"Content: {record['content']}\n"
            if record['topics']:
                graph_context += f"Topics: {', '.join(record['topics'])}\n"
            if record['people']:
                graph_context += f"People involved: {', '.join(record['people'])}\n"
            graph_context += "\n"
        
        # Combine all context
        system_prompt = """You are an AI assistant helping to analyze meeting notes and discussions.
        Use the provided context from both the vector store (semantic search) and graph database
        to answer the question comprehensively. If there are any conflicts between sources,
        point them out. If information is missing or unclear, acknowledge that."""
        
        # Generate response
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"""Context from vector search:{vector_context}
                                             \nContext from graph database:{graph_context}
                                             \nQuestion: {query}"""}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content

    def query(self, user_query):
        """Main query method that combines vector and graph search"""
        try:
            # Get relevant chunks from vector store
            vector_results = self.query_vector_store(user_query)
            
            # Extract keywords for graph search
            # Use OpenAI to extract key terms from the query
            keyword_extraction = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Extract key terms from the query that would be useful for searching in a graph database. Return them as a comma-separated list."},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.3
            )
            
            keywords = [term.strip().lower() for term in keyword_extraction.choices[0].message.content.split(',')]
            
            # Get relevant discussions from graph database
            graph_results = self.query_graph_database(keywords)
            
            # Generate final response
            response = self.generate_response(user_query, vector_results, graph_results)
            
            return {
                'response': response,
                'vector_results': [
                    {
                        'content': match.metadata['content'],
                        'score': match.score,
                        'file': match.metadata['file_name']
                    } for match in vector_results
                ],
                'graph_results': [
                    {
                        'meeting_title': record['meeting_title'],
                        'content': record['content'],
                        'topics': record['topics'],
                        'people': record['people']
                    } for record in graph_results
                ]
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'response': f"An error occurred while processing your query: {str(e)}"
            }

def main():
    # Initialize RAG system
    rag = RAGSystem()
    
    try:
        # Example queries to test the system
        example_queries = [
            "What are the main requirements discussed in the meetings?",
            "What is the timeline for the project?",
            "Who are the key stakeholders involved?"
        ]
        
        for query in example_queries:
            print(f"\nQuery: {query}")
            print("-" * 80)
            
            result = rag.query(query)
            
            print("\nResponse:")
            print(result['response'])
            
            print("\nSources:")
            print("\nVector Store Results:")
            for vr in result['vector_results']:
                print(f"- Score: {vr['score']:.4f}")
                print(f"  File: {vr['file']}")
                print(f"  Content: {vr['content'][:200]}...")
            
            print("\nGraph Database Results:")
            for gr in result['graph_results']:
                print(f"- Meeting: {gr['meeting_title']}")
                print(f"  Topics: {', '.join(gr['topics']) if gr['topics'] else 'None'}")
                print(f"  People: {', '.join(gr['people']) if gr['people'] else 'None'}")
            
            print("\n" + "="*80)
    
    finally:
        rag.close()

if __name__ == "__main__":
    main()
