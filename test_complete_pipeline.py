"""
Complete Pipeline Test - End-to-End Document Translation
Tests all 5 agents in sequence with proper workflow
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv
import time
import json

# Load environment variables
load_dotenv()

# Add the project root to the Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from src.agents.parser_agent import create_parser_agent, create_parsing_task, DocumentParserTool
from src.agents.translation_agent import create_translation_agent, create_translation_task, DocumentTranslationTool
from src.agents.style_agent import run_style_agent
from src.agents.output_agent import run_output_agent
from src.utils.file_manager import DocumentFileManager
from src.config import Config
from crewai import Crew


def print_separator(title: str):
    """Print a formatted separator"""
    print("\n" + "=" * 80)
    print(f"🚀 {title}")
    print("=" * 80)


def get_target_language():
    """Prompt user to select target language"""
    available_languages = {
        '1': 'Spanish',
        '2': 'French', 
        '3': 'German',
        '4': 'Italian',
        '5': 'Portuguese',
        '6': 'Chinese',
        '7': 'Japanese',
        '8': 'Korean',
        '9': 'Russian',
        '10': 'Arabic',
        '11': 'Custom'
    }
    
    print_separator("TARGET LANGUAGE SELECTION")
    print("🌐 Please select the target language for translation:")
    print()
    
    for key, language in available_languages.items():
        if key == '11':
            print(f"   {key}. {language} (Enter your own language)")
        else:
            print(f"   {key}. {language}")
    
    print()
    while True:
        try:
            choice = input("Enter your choice (1-11): ").strip()
            
            if choice in available_languages:
                if choice == '11':
                    # Custom language input
                    custom_lang = input("Enter the target language name: ").strip()
                    if custom_lang:
                        print(f"✅ Selected target language: {custom_lang}")
                        return custom_lang
                    else:
                        print("❌ Please enter a valid language name.")
                        continue
                else:
                    selected_language = available_languages[choice]
                    print(f"✅ Selected target language: {selected_language}")
                    return selected_language
            else:
                print("❌ Invalid choice. Please enter a number between 1-11.")
                
        except KeyboardInterrupt:
            print("\n❌ Operation cancelled by user.")
            return None
        except Exception as e:
            print(f"❌ Error: {e}. Please try again.")


def print_step_result(step: str, result: str, success: bool = True):
    """Print formatted step result"""
    status = "✅" if success else "❌"
    print(f"\n{status} {step} Result:")
    print("-" * 60)
    print(result)
    print("-" * 60)


def check_session_files(session_id: str):
    """Check what files exist in the session directory"""
    file_manager = DocumentFileManager()
    session_dir = Path(file_manager.base_output_dir) / session_id
    
    if not session_dir.exists():
        print(f"❌ Session directory not found: {session_dir}")
        return
    
    print(f"\n📁 Session Directory: {session_dir}")
    files = list(session_dir.glob("*"))
    files.sort()
    
    for file_path in files:
        if file_path.is_file():
            size_kb = file_path.stat().st_size / 1024
            print(f"   📄 {file_path.name} ({size_kb:.1f} KB)")


def run_parser_step(input_document: str):
    """Run the Parser Agent step"""
    try:
        # Use the tool directly for consistency and speed
        parser_tool = DocumentParserTool()
        result = parser_tool._run(input_document, save_to_files=True)
        
        # Extract session ID from the JSON result
        try:
            import json
            result_data = json.loads(result)
            session_id = result_data.get("session_info", {}).get("session_id")
            if session_id:
                return result, session_id
        except json.JSONDecodeError:
            # Fallback to text parsing if JSON parsing fails
            if "Session ID:" in result:
                session_id = result.split("Session ID:")[1].split()[0].strip()
                return result, session_id
        
        return result, None
            
    except Exception as e:
        return f"Error in parser: {str(e)}", None


def run_translation_step(session_id: str, target_language: str = "Spanish"):
    """Run the Translation Agent step"""
    try:
        # Use the tool directly for consistency and speed
        translation_tool = DocumentTranslationTool()
        result = translation_tool._run(
            session_id=session_id,
            target_language=target_language,
            source_language="English",
            translation_style="formal"
        )
        return result
        
    except Exception as e:
        return f"Error in translation: {str(e)}"


def run_complete_pipeline():
    """Run the complete document translation pipeline"""
    
    print_separator("COMPLETE DOCUMENT TRANSLATION PIPELINE")
    print("🎯 Target: blog_final_fixed99.docx → Multi-Language Translation")
    print("🔄 Pipeline: Parser → Translation → Style → Output")
    
    # Get target language from user
    target_language = get_target_language()
    if not target_language:
        print("❌ Pipeline cancelled - no target language selected.")
        return None
    
    print_separator("PIPELINE CONFIGURATION")
    print(f"📄 Input Document: blog_final_fixed99.docx")
    print(f"🌐 Source Language: English")
    print(f"🎯 Target Language: {target_language}")
    print(f"📋 Translation Style: Professional/Formal")
    print("🔄 Ready to start pipeline...")
    
    # Document to process
    input_document = "blog_final_fixed99.docx"
    
    if not os.path.exists(input_document):
        print(f"❌ Input document not found: {input_document}")
        return None
    
    try:
        # STEP 1: PARSER AGENT
        print_separator("STEP 1: PARSER AGENT - Document Analysis")
        print("📊 Extracting structure, formatting, and semantic analysis...")
        
        start_time = time.time()
        parser_result, session_id = run_parser_step(input_document)
        parser_time = time.time() - start_time
        
        print_step_result("Parser Agent", parser_result)
        print(f"⏱️  Parser Agent completed in {parser_time:.2f} seconds")
        
        if not session_id:
            print("❌ Failed to extract session ID from parser result")
            return None
        
        print(f"🆔 Session ID: {session_id}")
        check_session_files(session_id)
        
        # STEP 2: TRANSLATION AGENT
        print_separator("STEP 2: TRANSLATION AGENT - Content Translation")
        print(f"🌐 Translating content to {target_language} with context awareness...")
        
        start_time = time.time()
        translation_result = run_translation_step(session_id, target_language)
        translation_time = time.time() - start_time
        
        print_step_result("Translation Agent", translation_result)
        print(f"⏱️  Translation Agent completed in {translation_time:.2f} seconds")
        check_session_files(session_id)
        
        # STEP 3: STYLE AGENT 
        print_separator("STEP 3: STYLE AGENT - Formatting & Styling")
        print(f"🎨 Applying professional styling adapted for {target_language}...")
        
        start_time = time.time()
        style_result = run_style_agent(session_id, "professional")
        style_time = time.time() - start_time
        
        print_step_result("Style Agent", style_result)
        print(f"⏱️  Style Agent completed in {style_time:.2f} seconds")
        check_session_files(session_id)
        
        # STEP 4: OUTPUT AGENT
        print_separator("STEP 4: OUTPUT AGENT - Document Generation")
        print("📝 Generating final DOCX document with translated content...")
        
        start_time = time.time()
        output_result = run_output_agent(session_id, f"{target_language}_Translation_{session_id}.docx")
        output_time = time.time() - start_time
        
        print_step_result("Output Agent", output_result)
        print(f"⏱️  Output Agent completed in {output_time:.2f} seconds")
        check_session_files(session_id)
        
        # FINAL SUMMARY
        print_separator("PIPELINE COMPLETION SUMMARY")
        
        total_time = parser_time + translation_time + style_time + output_time
        print(f"🎯 Original Document: {input_document}")
        print(f"🌐 Translation: English → {target_language}")
        print(f"🆔 Session ID: {session_id}")
        print(f"⏱️  Total Pipeline Time: {total_time:.2f} seconds")
        print(f"   📊 Parser: {parser_time:.2f}s")
        print(f"   🌐 Translation: {translation_time:.2f}s") 
        print(f"   🎨 Styling: {style_time:.2f}s")
        print(f"   📝 Output: {output_time:.2f}s")
        
        # Check for final document
        file_manager = DocumentFileManager()
        session_dir = Path(file_manager.base_output_dir) / session_id
        docx_files = list(session_dir.glob("*.docx"))
        
        if docx_files:
            print(f"\n🎉 SUCCESS! Generated Documents:")
            for docx_file in docx_files:
                size_mb = docx_file.stat().st_size / (1024 * 1024)
                print(f"   📄 {docx_file.name} ({size_mb:.2f} MB)")
                print(f"   📂 Full path: {docx_file}")
                
            # Check if translated content is actually in target language
            print(f"\n🔍 TRANSLATION VERIFICATION:")
            styled_content_path = session_dir / "03_styled_content.json"
            if styled_content_path.exists():
                with open(styled_content_path, 'r', encoding='utf-8') as f:
                    styled_data = json.load(f)
                
                # Check title translation
                title = styled_data.get("styled_elements", {}).get("title", {})
                if title:
                    original = title.get("original_text", "")
                    translated = title.get("translated_text", "")
                    print(f"   📋 Title Translation:")
                    print(f"      EN: {original[:60]}...")
                    print(f"      {target_language}: {translated[:60]}...")
                
                # Check first header translation
                headers = styled_data.get("styled_elements", {}).get("headers", {}).get("main_headers", [])
                if headers:
                    header = headers[0]
                    original = header.get("original_text", "")
                    translated = header.get("translated_text", "")
                    print(f"   📋 First Header Translation:")
                    print(f"      EN: {original}")
                    print(f"      {target_language}: {translated}")
        else:
            print(f"\n❌ No DOCX files found in session directory")
        
        print(f"\n✅ COMPLETE PIPELINE FINISHED SUCCESSFULLY!")
        print(f"🔍 All files saved in: output/{session_id}/")
        
        return session_id
        
    except Exception as e:
        print(f"\n❌ Pipeline Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    session_id = run_complete_pipeline()
    
    if session_id:
        print(f"\n🚀 Pipeline completed successfully!")
        print(f"📋 Session ID: {session_id}")
        print(f"📁 Output directory: output/{session_id}/")
        print(f"💡 You can now review the translated document and run the QA Agent if needed.")
    else:
        print(f"\n❌ Pipeline failed. Please check the error messages above.") 