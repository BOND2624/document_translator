"""
Test script for the Output Agent
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from src.agents.output_agent import run_output_agent
from src.utils.file_manager import DocumentFileManager


def test_output_agent():
    """Test the Output Agent functionality"""
    
    print("📝 Testing Output Agent...")
    print("=" * 60)
    
    # Use the existing session ID
    session_id = "d212cbd859d2_20250621_125824"
    
    print(f"📋 Session ID: {session_id}")
    print(f"📄 Output Format: DOCX")
    print(f"🎨 From Style Agent: Styled content with professional formatting")
    print()
    
    try:
        # Run the Output Agent
        result = run_output_agent(session_id)
        
        print("✅ Output Agent Execution Result:")
        print(result)
        print()
        
        # Check output files
        file_manager = DocumentFileManager()
        
        # Check generated DOCX document
        session_dir = Path(file_manager.base_output_dir) / session_id
        docx_files = list(session_dir.glob("*.docx"))
        
        if docx_files:
            docx_file = docx_files[0]  # Get the first (most recent) DOCX file
            print(f"✅ DOCX document created: {docx_file.name}")
            file_size_mb = docx_file.stat().st_size / (1024 * 1024)
            print(f"   📊 File size: {file_size_mb:.2f} MB")
            print(f"   📂 Full path: {docx_file}")
        else:
            print(f"❌ No DOCX files found in session directory: {session_dir}")
        
        # Check generation summary file
        summary_path = file_manager.get_session_file(session_id, "04_generation_summary.json")
        if os.path.exists(summary_path):
            print(f"✅ Generation summary created: {Path(summary_path).name}")
            
            # Show some summary details
            import json
            with open(summary_path, 'r', encoding='utf-8') as f:
                summary = json.load(f)
            
            stats = summary.get("document_stats", {})
            print(f"   📈 Document Statistics:")
            print(f"      • Total elements: {stats.get('total_elements', 0)}")
            print(f"      • Main headers: {stats.get('main_headers', 0)}")
            print(f"      • Sub headers: {stats.get('sub_headers', 0)}")
            print(f"      • Body paragraphs: {stats.get('body_paragraphs', 0)}")
            print(f"      • Tables: {stats.get('tables', 0)}")
        else:
            print(f"❌ Generation summary not found: {summary_path}")
        
        # Check QA Agent input file
        qa_input_path = file_manager.get_session_file(session_id, "04_qa_agent_input.json")
        if os.path.exists(qa_input_path):
            print(f"✅ QA Agent input file created: {Path(qa_input_path).name}")
        else:
            print(f"❌ QA Agent input file not found: {qa_input_path}")
        
        # Check session manifest
        manifest = file_manager.get_session_status(session_id)
        if manifest:
            print(f"✅ Session manifest updated")
            if manifest.get("output_agent_completed"):
                print(f"   ✅ Output Agent marked as completed")
            if "generated_document" in manifest:
                print(f"   📄 Generated document: {manifest['generated_document']}")
        
        print()
        print("📝 Output Agent test completed!")
        
    except Exception as e:
        print(f"❌ Error during Output Agent test: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_output_agent() 