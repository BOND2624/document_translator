#!/usr/bin/env python3
"""Test script for the Translation Agent."""

import json
import logging
import os
from pathlib import Path

# Add the project root to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.translation_agent import create_translation_agent, create_translation_task
from src.utils.file_manager import DocumentFileManager
from src.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_translation_agent():
    """Test the Translation Agent with existing session data."""
    
    # Setup Azure OpenAI environment (for testing without actual API calls, we'll skip validation)
    logger.info("Setting up Azure OpenAI configuration...")
    try:
        # For testing purposes, we'll create a mock LLM or use None
        # In production, you would set up proper Azure OpenAI credentials
        llm = None  # This will use CrewAI's default behavior without requiring API keys
        
        # Set environment variables to avoid OpenAI API key requirement
        os.environ.setdefault("OPENAI_API_KEY", "test-key-for-simulation")
        
        logger.info("Azure OpenAI configuration ready (using simulation mode)")
    except Exception as e:
        logger.warning(f"Azure OpenAI setup failed, using simulation mode: {e}")
        llm = None
    
    # Initialize file manager to find available sessions
    file_manager = DocumentFileManager()
    sessions = file_manager.list_sessions()
    
    if not sessions:
        logger.error("No sessions found. Please run the Parser Agent first.")
        return
    
    # Use the most recent session
    session_id = sessions[-1]['session_id']
    logger.info(f"Testing Translation Agent with session: {session_id}")
    
    # Check if session has translatable content
    translatable_content = file_manager.load_translatable_content(session_id)
    if not translatable_content:
        logger.error(f"No translatable content found for session {session_id}")
        return
    
    logger.info("Found translatable content:")
    logger.info(f"- Document title: {bool(translatable_content.get('document_title'))}")
    logger.info(f"- Main headers: {len(translatable_content.get('headers', {}).get('main_headers', []))}")
    logger.info(f"- Sub headers: {len(translatable_content.get('headers', {}).get('sub_headers', []))}")
    logger.info(f"- Content sections: {len(translatable_content.get('content', {}))}")
    
    # Create the Translation Agent
    logger.info("\n" + "="*50)
    logger.info("Creating Translation Agent...")
    translation_agent = create_translation_agent(llm=llm)
    
    # Create translation task
    logger.info("Creating translation task...")
    translation_task = create_translation_task(
        agent=translation_agent,
        session_id=session_id,
        target_language="Spanish",
        source_language="English"
    )
    
    # Test the translation tool directly to avoid LLM API calls
    logger.info("\n" + "="*50)
    logger.info("Testing translation tool directly...")
    
    try:
        # Import and test the tool directly
        from src.agents.translation_agent import DocumentTranslationTool
        
        translation_tool = DocumentTranslationTool()
        
        # Test the tool directly
        result = translation_tool._run(
            session_id=session_id,
            target_language="Spanish",
            source_language="English",
            translation_style="formal"
        )
        
        logger.info("\n" + "="*50)
        logger.info("Translation completed successfully!")
        
        # Parse the result if it's JSON
        try:
            if isinstance(result, str):
                result_data = json.loads(result)
            else:
                result_data = result
            
            # Display translation summary
            if 'translation_summary' in result_data:
                summary = result_data['translation_summary']
                logger.info("\nTranslation Summary:")
                
                if 'translation_stats' in summary:
                    stats = summary['translation_stats']
                    logger.info(f"- Document title translated: {stats.get('document_title_translated', False)}")
                    logger.info(f"- Main headers translated: {stats.get('main_headers_count', 0)}")
                    logger.info(f"- Sub headers translated: {stats.get('sub_headers_count', 0)}")
                    logger.info(f"- Content items translated: {stats.get('total_content_items', 0)}")
                    logger.info(f"- Tables processed: {stats.get('tables_processed', 0)}")
            
            # Display saved files
            if 'saved_files' in result_data:
                logger.info(f"\nFiles saved: {len(result_data['saved_files'])}")
                for file_path in result_data['saved_files']:
                    logger.info(f"- {file_path}")
            
            # Show a sample of translated content
            if 'translated_content' in result_data:
                translated = result_data['translated_content']
                
                # Show translated title
                if translated.get('document_title'):
                    title = translated['document_title']
                    logger.info(f"\nSample Translation - Document Title:")
                    logger.info(f"Original: {title.get('original_text', 'N/A')}")
                    logger.info(f"Translated: {title.get('translated_text', 'N/A')}")
                
                # Show a translated header
                headers = translated.get('headers', {}).get('main_headers', [])
                if headers:
                    header = headers[0]
                    logger.info(f"\nSample Translation - Main Header:")
                    logger.info(f"Original: {header.get('original_text', 'N/A')}")
                    logger.info(f"Translated: {header.get('translated_text', 'N/A')}")
        
        except json.JSONDecodeError:
            logger.info("Result is not JSON, displaying as text:")
            logger.info(result)
        
    except Exception as e:
        logger.error(f"Error during translation: {str(e)}", exc_info=True)


def show_translation_files(session_id: str = None):
    """Show the translation files created."""
    
    file_manager = DocumentFileManager()
    
    if not session_id:
        sessions = file_manager.list_sessions()
        if not sessions:
            logger.error("No sessions found.")
            return
        session_id = sessions[-1]['session_id']
    
    logger.info(f"\nTranslation Files for Session: {session_id}")
    logger.info("="*60)
    
    session_dir = file_manager.base_output_dir / session_id
    if not session_dir.exists():
        logger.error(f"Session directory not found: {session_dir}")
        return
    
    # List all files in session directory
    files = list(session_dir.glob("*.json"))
    files.sort()
    
    for file_path in files:
        logger.info(f"\n📄 {file_path.name}")
        logger.info("-" * 40)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Show file summary based on filename
            if "02_translated_content" in file_path.name:
                logger.info("Complete translated content with metadata")
                if 'translation_metadata' in data:
                    metadata = data['translation_metadata']
                    logger.info(f"Language: {metadata.get('source_language')} -> {metadata.get('target_language')}")
                    logger.info(f"Style: {metadata.get('translation_style')}")
                    logger.info(f"Translated at: {metadata.get('translated_at')}")
            
            elif "02_translation_summary" in file_path.name:
                logger.info("Translation process summary and statistics")
                if 'stats' in data:
                    stats = data['stats']
                    logger.info(f"Title translated: {stats.get('title_translated')}")
                    if 'headers_translated' in stats:
                        headers = stats['headers_translated']
                        logger.info(f"Headers: {headers.get('main_headers', 0)} main, {headers.get('sub_headers', 0)} sub")
            
            elif "02_style_agent_input" in file_path.name:
                logger.info("Prepared input for Style Agent")
                if 'session_metadata' in data:
                    metadata = data['session_metadata']
                    logger.info(f"Ready for Style Agent: {metadata.get('ready_for_style_agent')}")
            
            logger.info(f"File size: {file_path.stat().st_size} bytes")
            
        except Exception as e:
            logger.error(f"Error reading {file_path.name}: {str(e)}")


if __name__ == "__main__":
    print("Document Translation Agent Test")
    print("="*50)
    
    # Test the translation agent
    test_translation_agent()
    
    print("\n" + "="*50)
    print("Showing Translation Files...")
    show_translation_files() 