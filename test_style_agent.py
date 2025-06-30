"""
Test script for the Style Agent
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

from src.agents.style_agent import run_style_agent
from src.utils.file_manager import DocumentFileManager


def test_style_agent():
    """Test the Style Agent functionality"""
    
    print("🎨 Testing Style Agent...")
    print("=" * 60)
    
    # Use the existing session ID
    session_id = "d212cbd859d2_20250621_125824"
    
    print(f"📋 Session ID: {session_id}")
    print(f"🎨 Style Profile: professional")
    print(f"🌍 Target Language: Spanish")
    print()
    
    try:
        # Run the Style Agent
        result = run_style_agent(session_id, "professional")
        
        print("✅ Style Agent Execution Result:")
        print(result)
        print()
        
        # Check output files
        file_manager = DocumentFileManager()
        
        # Check styled content file
        styled_content_path = file_manager.get_session_file(session_id, "03_styled_content.json")
        if os.path.exists(styled_content_path):
            print(f"✅ Styled content file created: {styled_content_path}")
            file_size = os.path.getsize(styled_content_path)
            print(f"   📊 File size: {file_size:,} bytes")
        else:
            print(f"❌ Styled content file not found: {styled_content_path}")
        
        # Check style summary file
        style_summary_path = file_manager.get_session_file(session_id, "03_style_summary.json")
        if os.path.exists(style_summary_path):
            print(f"✅ Style summary file created: {style_summary_path}")
        else:
            print(f"❌ Style summary file not found: {style_summary_path}")
        
        # Check output agent input file
        output_agent_input_path = file_manager.get_session_file(session_id, "03_output_agent_input.json")
        if os.path.exists(output_agent_input_path):
            print(f"✅ Output agent input file created: {output_agent_input_path}")
        else:
            print(f"❌ Output agent input file not found: {output_agent_input_path}")
        
        print()
        print("🎨 Style Agent test completed!")
        
    except Exception as e:
        print(f"❌ Error during Style Agent test: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_style_agent() 