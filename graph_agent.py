from database import Neo4jDatabase
import re
from datetime import datetime

class GraphAgent:
    def __init__(self):
        self.db = Neo4jDatabase()
        
    def close(self):
        if self.db:
            self.db.close()

    def extract_timestamp(self, text):
        """Extract timestamp from text in format HH:MM"""
        match = re.search(r'(\d{1,2}:\d{2})\s*$', text)
        if match:
            return match.group(1)
        return None

    def extract_people(self, text):
        """Extract people names from text"""
        # Simple name extraction - looks for capitalized words
        # This could be enhanced with NER models
        names = re.findall(r'\b[A-Z][a-z]+\b', text)
        return list(set(names))  # Remove duplicates

    def extract_topics(self, text):
        """Extract potential topics from text"""
        # Simple topic extraction - looks for key technical terms
        # This could be enhanced with more sophisticated NLP
        topics = []
        technical_terms = ['Neo4j', 'API', 'database', 'interface', 'testing', 'development',
                         'integration', 'design', 'implementation', 'project']
        
        for term in technical_terms:
            if re.search(rf'\b{term}\b', text, re.IGNORECASE):
                topics.append(term.lower())
        
        return list(set(topics))

    def process_meeting_notes(self, title, notes):
        """Process meeting notes and create graph structure"""
        try:
            # Create meeting node
            meeting_id = self.db.create_meeting_node(title)
            
            # Process each line
            for line in notes.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                # Extract timestamp
                timestamp = self.extract_timestamp(line)
                if timestamp:
                    # Remove timestamp from content
                    content = line[:line.rfind(timestamp)].strip()
                else:
                    content = line
                
                # Create discussion point
                point_id = self.db.create_discussion_point(meeting_id, content, timestamp)
                
                # Extract and create people nodes and relationships
                people = self.extract_people(content)
                for person in people:
                    self.db.create_person_node(person)
                    self.db.create_person_discussion_relationship(person, point_id)
                
                # Extract and create topic nodes and relationships
                topics = self.extract_topics(content)
                for topic in topics:
                    self.db.create_topic_node(topic)
                    self.db.create_topic_discussion_relationship(topic, point_id)
            
            return meeting_id
            
        except Exception as e:
            print(f"Error processing meeting notes: {str(e)}")
            raise

    def query_meeting_timeline(self, meeting_id):
        """Query the timeline of a meeting"""
        return self.db.query_meeting_timeline(meeting_id)

    def query_person_activities(self, person_name):
        """Query activities related to a person"""
        return self.db.query_person_activities(person_name)
