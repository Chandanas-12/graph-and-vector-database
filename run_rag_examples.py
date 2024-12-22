from graph_rag import GraphRAG
from datetime import datetime
import os

def run_examples():
    rag = GraphRAG()
    
    # Create output directory if it doesn't exist
    output_dir = "meeting_analysis"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate timestamp for the output file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"meeting_analysis_{timestamp}.txt")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write("Meeting Notes Analysis\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Example 1: Query about Integration Framework
            f.write("\n1. Integration Framework Analysis\n")
            f.write("-" * 30 + "\n")
            question = "What are the phases of the integration framework that were discussed?"
            f.write(f"Q: {question}\n")
            answer = rag.generate_response(question)
            f.write(f"A: {answer}\n")
            
            # Example 2: Query about System Design
            f.write("\n2. System Design Analysis\n")
            f.write("-" * 30 + "\n")
            question = "What was discussed about the system design and who is responsible for it?"
            f.write(f"Q: {question}\n")
            answer = rag.generate_response(question)
            f.write(f"A: {answer}\n")
            
            # Example 3: Get Action Items
            f.write("\n3. Action Items from the Meeting\n")
            f.write("-" * 30 + "\n")
            action_items = rag.get_action_items()
            f.write(action_items + "\n")
            
            # Example 4: Project Management
            f.write("\n4. Project Management Analysis\n")
            f.write("-" * 30 + "\n")
            question = "Who is the project manager and what are their responsibilities?"
            f.write(f"Q: {question}\n")
            answer = rag.generate_response(question)
            f.write(f"A: {answer}\n")
            
            # Example 5: Technical Implementation Details
            f.write("\n5. Technical Implementation Details\n")
            f.write("-" * 30 + "\n")
            question = "What were the key technical decisions and implementation details discussed about Neo4j integration?"
            f.write(f"Q: {question}\n")
            answer = rag.generate_response(question)
            f.write(f"A: {answer}\n")
            
            # Example 6: Team Contributions
            f.write("\n6. Team Member Contributions\n")
            f.write("-" * 30 + "\n")
            question = "What were the main contributions and responsibilities discussed for each team member?"
            f.write(f"Q: {question}\n")
            answer = rag.generate_response(question)
            f.write(f"A: {answer}\n")
            
            # Example 7: Timeline and Milestones
            f.write("\n7. Timeline and Milestones\n")
            f.write("-" * 30 + "\n")
            question = "What are the key milestones and timeline expectations discussed in the meeting?"
            f.write(f"Q: {question}\n")
            answer = rag.generate_response(question)
            f.write(f"A: {answer}\n")
            
            # Example 8: Challenges and Solutions
            f.write("\n8. Challenges and Solutions\n")
            f.write("-" * 30 + "\n")
            question = "What challenges were identified during the meeting and what solutions were proposed?"
            f.write(f"Q: {question}\n")
            answer = rag.generate_response(question)
            f.write(f"A: {answer}\n")
            
            # Write footer
            f.write("\n" + "=" * 50 + "\n")
            f.write("End of Analysis\n")
        
        print(f"Analysis has been written to: {output_file}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        rag.close()

if __name__ == "__main__":
    run_examples()
