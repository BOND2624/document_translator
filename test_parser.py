"""Test script for the Parser Agent."""

import os
import json
from pathlib import Path
from src.agents.parser_agent import create_parser_agent, create_parsing_task, DocumentParserTool
from src.config import Config
from crewai import Crew
from docx import Document
from docx.shared import RGBColor
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel

console = Console()



def test_parser_tool_directly():
    """Test the DocumentParserTool directly."""
    
    console.print("\n[bold blue]Testing DocumentParserTool directly...[/bold blue]")
    
    tool = DocumentParserTool()
    
    # Test the specific blog document
    console.print("\n[yellow]Testing blog_final_fixed99.docx parsing:[/yellow]")
    result_docx = tool._run("blog_final_fixed99.docx")
    
    try:
        parsed_data = json.loads(result_docx)
        console.print("✅ DOCX parsing successful")
        console.print(f"📊 Found {len(parsed_data['paragraphs'])} paragraphs")
        console.print(f"📊 Found {len(parsed_data['tables'])} tables")
        console.print(f"📊 Fonts used: {parsed_data['metadata']['fonts_used']}")
        console.print(f"📊 Has formatting: {parsed_data['metadata']['has_formatting']}")
        console.print(f"📊 Styles used: {parsed_data['metadata']['styles_used']}")
        
        # Show enhanced semantic analysis
        console.print("\n[magenta]🧠 Semantic Analysis:[/magenta]")
        semantic = parsed_data.get('semantic_structure', {})
        metadata = parsed_data.get('metadata', {})
        
        if semantic.get('document_title'):
            title_text = semantic['document_title']['text'][:50]
            console.print(f"📑 Document Title: '{title_text}...'")
        
        total_sections = metadata.get('total_sections', 0)
        total_subsections = metadata.get('total_subsections', 0)
        console.print(f"🏗️  Structure: {total_sections} sections, {total_subsections} subsections")
        console.print(f"📋 Content Types: {semantic.get('content_types', {})}")
        
        # Show document outline
        outline = parsed_data.get('document_outline', [])
        if outline:
            console.print("\n[blue]📋 Document Outline:[/blue]")
            for item in outline[:5]:  # Show first 5 outline items
                if item['type'] == 'title':
                    console.print(f"  📄 TITLE: {item['text']}")
                elif item['type'] == 'section':
                    console.print(f"  📂 SECTION: {item['text']}")
                    if item.get('children'):
                        for child in item['children'][:2]:  # Show first 2 subsections
                            console.print(f"    📁 SUB: {child['text']}")
                elif item['type'] == 'content':
                    console.print(f"  📝 Content: {item['text']}")
        
        # Show sample content with semantic info
        console.print("\n[cyan]Sample paragraphs with semantic analysis:[/cyan]")
        for i, para in enumerate(parsed_data['paragraphs'][:3]):  # Show first 3 paragraphs
            if para['text'].strip():
                console.print(f"📝 Paragraph {i+1}: {para['text'][:80]}{'...' if len(para['text']) > 80 else ''}")
                console.print(f"   Style: {para['style']}, Semantic: {para.get('semantic_type', 'unknown')}, Level: {para.get('hierarchy_level', 'N/A')}")
        
        if parsed_data['tables']:
            console.print(f"\n[cyan]Found {len(parsed_data['tables'])} table(s)[/cyan]")
            
    except json.JSONDecodeError:
        console.print("❌ Failed to parse DOCX result as JSON")
        console.print(result_docx)

def test_parser_agent():
    """Test the Parser Agent with CrewAI."""
    
    console.print("\n[bold blue]Testing Parser Agent with CrewAI...[/bold blue]")
    
    # Check if Azure OpenAI is configured (for full agent testing)
    if not Config.validate():
        console.print("⚠️  Azure OpenAI not configured. Testing parser tool only.")
        test_parser_tool_directly()
        return
    
    try:
        # Setup Azure OpenAI environment variables
        console.print("🔧 Setting up Azure OpenAI environment...")
        Config.setup_azure_environment()
        
        # Create agent and task
        agent = create_parser_agent()
        task = create_parsing_task(agent=agent, file_path="blog_final_fixed99.docx")
        
        # Create crew
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True
        )
        
        console.print("🚀 Starting document parsing with CrewAI...")
        result = crew.kickoff()
        
        console.print("\n[green]Parser Agent Result:[/green]")
        console.print(Panel(str(result), title="Parsing Output"))
        
    except Exception as e:
        console.print(f"❌ Error testing Parser Agent: {str(e)}")
        console.print("💡 Falling back to direct tool testing...")
        test_parser_tool_directly()

def main():
    """Main test function."""
    
    console.print(Panel.fit("🔍 Document Parser Agent Test", style="bold magenta"))
    
    # Check if the blog document exists
    if not os.path.exists("blog_final_fixed99.docx"):
        console.print("❌ blog_final_fixed99.docx not found in current directory")
        return
    
    console.print("✅ Found blog_final_fixed99.docx - ready to parse!")
    
    # Test the parser
    test_parser_agent()
    
    console.print("\n[bold green]Parser Agent testing completed! ✨[/bold green]")
    console.print("\n[dim]Next steps:[/dim]")
    console.print("1. Configure Azure OpenAI in config.env for full agent testing")
    console.print("2. Review the parsed output structure")
    console.print("3. Proceed to create the Translation Agent")

if __name__ == "__main__":
    main()