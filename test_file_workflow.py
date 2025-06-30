"""
Test File-Based Workflow for Document Translation Pipeline

This script demonstrates how the Parser Agent saves data to files 
and how the Translation Agent can load and use that data.
"""

import json
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.json import JSON
from rich.table import Table

from src.agents.parser_agent import DocumentParserTool
from src.utils.file_manager import DocumentFileManager

console = Console()

def test_parser_with_file_saving():
    """Test the Parser Agent with file saving enabled."""
    
    console.print(Panel.fit("🔄 Testing File-Based Workflow", style="bold blue"))
    
    # Test parsing with file saving
    console.print("\n[yellow]Step 1: Running Parser Agent with file saving...[/yellow]")
    
    tool = DocumentParserTool()
    result = tool._run("blog_final_fixed99.docx", save_to_files=True)
    
    try:
        parsed_result = json.loads(result)
        session_info = parsed_result.get('session_info', {})
        session_id = session_info.get('session_id')
        
        console.print(f"✅ Parsing completed!")
        console.print(f"📋 Session ID: {session_id}")
        console.print(f"💾 Files saved to: {session_info.get('saved_files', {}).get('session_dir')}")
        
        return session_id, session_info
        
    except json.JSONDecodeError:
        console.print("❌ Failed to parse result as JSON")
        console.print(result)
        return None, None

def test_file_manager_operations(session_id: str):
    """Test file manager operations."""
    
    console.print(f"\n[yellow]Step 2: Testing File Manager operations for session {session_id}...[/yellow]")
    
    file_manager = DocumentFileManager()
    
    # Test loading parsed output
    console.print("\n[cyan]Loading complete parsed structure...[/cyan]")
    parsed_data = file_manager.load_parser_output(session_id)
    
    if parsed_data:
        console.print(f"✅ Loaded parsed data: {len(parsed_data.get('paragraphs', []))} paragraphs")
        console.print(f"✅ Semantic structure: {list(parsed_data.get('semantic_structure', {}).get('content_types', {}).keys())}")
    
    # Test loading translatable content (what Translation Agent would use)
    console.print("\n[cyan]Loading translatable content for Translation Agent...[/cyan]")
    translatable_content = file_manager.load_translatable_content(session_id)
    
    if translatable_content:
        console.print("✅ Loaded translatable content organized by semantic type:")
        
        # Show what Translation Agent would see
        table = Table(title="Translatable Content Summary")
        table.add_column("Content Type", style="cyan")
        table.add_column("Count", style="green")
        table.add_column("Sample", style="yellow")
        
        # Document title
        if translatable_content.get('document_title'):
            title = translatable_content['document_title']
            table.add_row("Document Title", "1", title['text'][:50] + "...")
        
        # Headers
        headers = translatable_content.get('headers', {})
        main_headers = headers.get('main_headers', [])
        sub_headers = headers.get('sub_headers', [])
        
        if main_headers:
            table.add_row("Main Headers", str(len(main_headers)), main_headers[0]['text'][:50] + "...")
        
        if sub_headers:
            table.add_row("Sub Headers", str(len(sub_headers)), sub_headers[0]['text'][:50] + "...")
        
        # Content
        content = translatable_content.get('content', {})
        for content_type, items in content.items():
            if items:
                table.add_row(
                    content_type.replace('_', ' ').title(),
                    str(len(items)),
                    items[0]['text'][:50] + "..." if items[0].get('text') else "N/A"
                )
        
        console.print(table)
        
        # Show translation context
        context = translatable_content.get('translation_context', {})
        console.print(f"\n[green]Translation Context:[/green]")
        console.print(f"  📄 Document Type: {context.get('document_type', 'unknown')}")
        console.print(f"  🎨 Preserve Formatting: {context.get('preserve_formatting', False)}")
        console.print(f"  🏗️  Preserve Structure: {context.get('preserve_structure', False)}")

def test_session_management():
    """Test session management features."""
    
    console.print(f"\n[yellow]Step 3: Testing session management...[/yellow]")
    
    file_manager = DocumentFileManager()
    
    # List all sessions
    sessions = file_manager.list_sessions()
    
    if sessions:
        console.print(f"\n[green]Found {len(sessions)} processing session(s):[/green]")
        
        table = Table(title="Processing Sessions")
        table.add_column("Session ID", style="cyan")
        table.add_column("Original File", style="green")
        table.add_column("Stage", style="yellow")
        table.add_column("Created", style="blue")
        
        for session in sessions[:5]:  # Show latest 5 sessions
            table.add_row(
                session.get('session_id', 'N/A')[:15] + "...",
                session.get('original_filename', 'N/A'),
                session.get('stage', 'unknown'),
                session.get('created_at', 'N/A')[:19].replace('T', ' ')
            )
        
        console.print(table)
    else:
        console.print("ℹ️  No previous sessions found")

def show_next_steps():
    """Show what happens next in the pipeline."""
    
    console.print(f"\n[magenta]🚀 Next Steps for Translation Agent:[/magenta]")
    
    console.print("""
[green]✅ Ready for Translation Agent![/green]

The Translation Agent will:
1. 🔍 Load translatable content using session_id
2. 🌍 Translate content by semantic type (titles, headers, body text)
3. 🧠 Use context to make better translation decisions
4. 💾 Save translated results to 02_translated_content.json
5. 📝 Preserve semantic structure and formatting metadata

[yellow]File Structure Created:[/yellow]
📁 output/
  └── {session_id}/
      ├── 📄 session_manifest.json     # Session tracking
      ├── 📄 01_parsed_structure.json  # Complete parsed data
      ├── 📄 01_semantic_structure.json # Semantic analysis
      └── 📄 01_translatable_content.json # Ready for translation

[cyan]Translation Agent Input:[/cyan]
- Organized content by semantic type
- Preserved formatting metadata
- Document structure context
- Translation hints and constraints
    """)

def main():
    """Main test function."""
    
    # Check if the blog document exists
    if not os.path.exists("blog_final_fixed99.docx"):
        console.print("❌ blog_final_fixed99.docx not found in current directory")
        return
    
    # Test the file workflow
    session_id, session_info = test_parser_with_file_saving()
    
    if session_id:
        test_file_manager_operations(session_id)
        test_session_management()
        show_next_steps()
    
    console.print(f"\n[bold green]File-based workflow test completed! ✨[/bold green]")

if __name__ == "__main__":
    main() 