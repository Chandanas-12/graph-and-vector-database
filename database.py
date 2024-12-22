from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

class Neo4jDatabase:
    def __init__(self):
        load_dotenv()
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")
        self.database = os.getenv("NEO4J_DATABASE", "neo4j")
        
        print(f"Attempting to connect to: {uri}")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Verify connectivity
        try:
            self.driver.verify_connectivity()
            print("Successfully verified connectivity!")
            
            # Run a test query
            with self.driver.session(database=self.database) as session:
                result = session.run("RETURN 1 as num")
                result.single()
                print("Successfully ran test query!")
                
        except Exception as e:
            print(f"Error connecting to Neo4j: {str(e)}")
            raise

    def close(self):
        if self.driver:
            self.driver.close()

    def create_meeting_node(self, title, date=None):
        with self.driver.session(database=self.database) as session:
            result = session.run(
                "CREATE (m:Meeting {id: randomUUID(), title: $title, date: $date}) "
                "RETURN m.id as id",
                title=title,
                date=date
            )
            return result.single()["id"]

    def create_discussion_point(self, meeting_id, content, timestamp=None, speaker=None):
        with self.driver.session(database=self.database) as session:
            result = session.run(
                "MATCH (m:Meeting {id: $meeting_id}) "
                "CREATE (d:DiscussionPoint {id: randomUUID(), content: $content, timestamp: $timestamp, speaker: $speaker})"
                "CREATE (m)-[:HAS_POINT]->(d) "
                "RETURN d.id as id",
                meeting_id=meeting_id,
                content=content,
                timestamp=timestamp,
                speaker=speaker
            )
            return result.single()["id"]

    def create_person_node(self, name):
        with self.driver.session(database=self.database) as session:
            result = session.run(
                "MERGE (p:Person {name: $name}) "
                "RETURN p.name as name",
                name=name
            )
            return result.single()["name"]

    def create_topic_node(self, name):
        with self.driver.session(database=self.database) as session:
            result = session.run(
                "MERGE (t:Topic {name: $name}) "
                "RETURN t.name as name",
                name=name
            )
            return result.single()["name"]

    def create_person_discussion_relationship(self, person_name, discussion_id, relationship_type="MENTIONED_IN"):
        with self.driver.session(database=self.database) as session:
            session.run(
                f"MATCH (p:Person {{name: $person_name}}), (d:DiscussionPoint {{id: $discussion_id}}) "
                f"CREATE (p)-[:{relationship_type}]->(d)",
                person_name=person_name,
                discussion_id=discussion_id
            )

    def create_topic_discussion_relationship(self, topic_name, discussion_id):
        with self.driver.session(database=self.database) as session:
            session.run(
                "MATCH (t:Topic {name: $topic_name}), (d:DiscussionPoint {id: $discussion_id}) "
                "CREATE (t)-[:DISCUSSED_IN]->(d)",
                topic_name=topic_name,
                discussion_id=discussion_id
            )

    def query_meeting_timeline(self, meeting_id):
        with self.driver.session(database=self.database) as session:
            result = session.run(
                "MATCH (m:Meeting {id: $meeting_id})-[:HAS_POINT]->(d:DiscussionPoint) "
                "RETURN d.timestamp as timestamp, d.content as content, d.speaker as speaker "
                "ORDER BY d.timestamp",
                meeting_id=meeting_id
            )
            return [dict(record) for record in result]

    def query_person_activities(self, person_name):
        with self.driver.session(database=self.database) as session:
            result = session.run(
                "MATCH (p:Person {name: $name})-[r]->(d:DiscussionPoint)<-[:HAS_POINT]-(m:Meeting) "
                "RETURN type(r) as relationship, m.title as title, d.timestamp as timestamp, d.content as content "
                "ORDER BY m.date DESC, d.timestamp",
                name=person_name
            )
            return [dict(record) for record in result]
