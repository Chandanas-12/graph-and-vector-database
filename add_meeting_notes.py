from graph_agent import GraphAgent
from rag_agent import RAGAgent
from datetime import datetime

def add_meeting_notes():
    # Initialize agents
    graph_agent = GraphAgent()
    rag_agent = RAGAgent()
    
    try:
        # First, clear existing data
        with graph_agent.db.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        
        # Real Project Meeting Notes
        project_meeting = """
        Project Planning and Team Updates Meeting - December 8, 2024
        
        4:19 Dr. Sonia emphasized the importance of all participants joining the class with their videos on before the instructor starts the training session.
        
        6:01 Each team was instructed to present their approach for the assigned tasks, with discussions to follow for refinement.
        
        6:16 Rajat was introduced as the new project manager for the group, responsible for managing tasks and addressing queries moving forward.
        
        8:51 Sandesh presented a detailed design for the project, including a user-agent interaction model and a feedback loop for gathering requirements.
        
        11:10 Rajat will be the primary point of contact for refining the project outputs, as the tool is being built specifically for him.
        
        13:02 The project charter is a live document that will evolve based on project requirements and stakeholder inputs, and it will differ for various types of projects, but the template provided for Agent One will be used as a reference.
        
        15:57 There are two modes for inputting project requirements into the agent: uploading a document or conversing directly with the agent to refine the requirements, which will help streamline the process.
        
        20:40 The team will focus on integrating Neo4j into their project, with plans to create a use case involving a Graph Retrieval Agent, utilizing documents such as meeting notes for conversational AI development.
        
        21:15 Chandana's team interpreted the task as creating a system design for the entire project, resulting in a flowchart that includes user actions and data management, rather than focusing solely on the database integration.
        
        24:24 Rajat will provide access credentials for MongoDB and assist with other necessary details, while teams are encouraged to set up their own Neo4j accounts for prototyping purposes.
        
        26:44 The integration framework for the agent has been divided into five phases, with the second phase focusing on defining input, output, and core functionalities such as creating, deleting, and updating folders.
        
        28:37 The agent will also manage meeting notes by creating, reading, and deleting them in phase three, with a roadmap established for testing and deployment.
        
        Action Items:
        - Set up individual Neo4j accounts for prototyping
        - Complete project charter template based on Agent One reference
        - Implement document upload and conversation modes
        - Design the five-phase integration framework
        - Set up meeting notes management system
        """
        
        # Process the meeting notes using the database directly
        meeting_id = graph_agent.db.create_meeting_node(
            "Project Planning and Team Updates",
            date="2024-12-08"
        )
        
        # Add discussion points
        lines = project_meeting.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Handle timestamp format
            if ':' in line and any(c.isdigit() for c in line):
                try:
                    time_str, content = line.split(' ', 1)
                    if ':' in time_str:
                        discussion_id = graph_agent.db.create_discussion_point(
                            meeting_id,
                            content=content.strip(),
                            timestamp=time_str
                        )
                        
                        # Create relationships for mentioned people
                        for person in ["Dr. Sonia", "Rajat", "Sandesh", "Chandana"]:
                            if person in content:
                                graph_agent.db.create_person_node(person)
                                graph_agent.db.create_person_discussion_relationship(
                                    person,
                                    discussion_id
                                )
                                
                        # Create relationships for topics
                        topics = {
                            "Neo4j integration": ["neo4j", "graph database"],
                            "Project Charter": ["project charter", "charter"],
                            "Integration Framework": ["integration framework", "framework", "phase"],
                            "System Design": ["system design", "design", "flowchart"],
                            "MongoDB": ["mongodb"],
                            "Graph Retrieval Agent": ["graph retrieval", "agent"]
                        }
                        
                        for topic, keywords in topics.items():
                            if any(keyword.lower() in content.lower() for keyword in keywords):
                                graph_agent.db.create_topic_node(topic)
                                graph_agent.db.create_topic_discussion_relationship(
                                    topic,
                                    discussion_id
                                )
                except ValueError:
                    continue
            
            # Handle action items
            elif line.startswith('-'):
                discussion_id = graph_agent.db.create_discussion_point(
                    meeting_id,
                    content=line.strip(),
                    timestamp="action_item"
                )
        
        print("Successfully processed meeting notes!")
        
    except Exception as e:
        print(f"Error processing meeting notes: {str(e)}")
    finally:
        graph_agent.close()
        rag_agent.close()

if __name__ == "__main__":
    add_meeting_notes()
