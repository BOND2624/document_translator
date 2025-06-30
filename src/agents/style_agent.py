"""
Style Agent - Analyzes and adapts document formatting for target language
Handles RTL/LTR considerations, font compatibility, and style consistency
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

from crewai import Agent, Task, Crew, Process
from crewai_tools import BaseTool
from pydantic import BaseModel, Field
from typing import ClassVar
from langchain_openai import AzureChatOpenAI

from ..utils.file_manager import DocumentFileManager


@dataclass
class StyleProfile:
    """Defines styling rules for different document types and languages"""
    name: str
    description: str
    font_families: List[str]
    font_sizes: Dict[str, str]
    colors: Dict[str, str]
    alignments: Dict[str, str]
    spacing: Dict[str, str]
    language_specific_rules: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LanguageStyleRules:
    """Language-specific formatting rules"""
    language_code: str
    writing_direction: str  # 'ltr' or 'rtl'
    preferred_fonts: List[str]
    text_alignment_default: str
    spacing_adjustments: Dict[str, float]
    punctuation_rules: Dict[str, str]
    number_formatting: str
    date_formatting: str


class StyleAnalysisModel(BaseModel):
    """Model for style analysis results"""
    original_styles: Dict[str, Any] = Field(description="Original document styles")
    target_language_requirements: Dict[str, Any] = Field(description="Target language style requirements")
    style_adaptations: List[Dict[str, Any]] = Field(description="Required style adaptations")
    formatting_consistency_score: float = Field(description="Style consistency score")


class DocumentStyleTool(BaseTool):
    """Tool for analyzing and adapting document styles"""
    
    name: str = "document_style_tool"
    description: str = "Analyzes original document formatting and adapts it for target language"
    
    # Class-level data to avoid Pydantic conflicts
    STYLE_PROFILES: ClassVar[Dict[str, StyleProfile]] = {
        "professional": StyleProfile(
            name="professional",
            description="Professional business document styling",
            font_families=["Arial", "Calibri", "Times New Roman"],
            font_sizes={
                "document_title": "18pt",
                "main_header": "14pt", 
                "sub_header": "12pt",
                "body_text": "11pt",
                "special_content": "10pt"
            },
            colors={
                "document_title": "#1f4e79",
                "main_header": "#2c5aa0", 
                "sub_header": "#365f91",
                "body_text": "#1a1a1a",
                "special_content": "#5d6d7e"
            },
            alignments={
                "document_title": "center",
                "main_header": "left",
                "sub_header": "left", 
                "body_text": "justify",
                "special_content": "left"
            },
            spacing={
                "document_title": "24pt after",
                "main_header": "18pt before, 6pt after",
                "sub_header": "12pt before, 3pt after",
                "body_text": "0pt before, 6pt after",
                "special_content": "6pt before, 6pt after"
            }
        )
    }
    
    LANGUAGE_RULES: ClassVar[Dict[str, Dict[str, Any]]] = {
        "spanish": {
            "writing_direction": "ltr",
            "preferred_fonts": ["Arial", "Calibri", "Times New Roman"],
            "text_alignment_default": "justify",
            "spacing_adjustments": {"line_spacing": 1.0, "paragraph_spacing": 1.0}
        },
        "english": {
            "writing_direction": "ltr", 
            "preferred_fonts": ["Arial", "Calibri", "Times New Roman"],
            "text_alignment_default": "justify",
            "spacing_adjustments": {"line_spacing": 1.0, "paragraph_spacing": 1.0}
        }
    }
    
    def _apply_style_profile(self, 
                           element_type: str,
                           content_element: Dict[str, Any],
                           style_profile: StyleProfile,
                           language_rules: Dict[str, Any]) -> Dict[str, Any]:
        """Apply style profile to a content element"""
        styled_element = content_element.copy()
        
        # Get base formatting from original
        original_formatting = styled_element.get("formatting", {})
        
        # Create new formatting based on style profile
        new_formatting = {
            "alignment": style_profile.alignments.get(element_type, "left"),
            "spacing": style_profile.spacing.get(element_type, "6pt after"),
            "runs": []
        }
        
        # Determine if element should be bold (headers and titles)
        should_be_bold = element_type in ["document_title", "main_header", "sub_header"]
        
        # Process text runs
        if "runs" in original_formatting:
            for run in original_formatting["runs"]:
                new_run = {
                    "text": styled_element.get("translated_text", styled_element.get("original_text", "")),
                    "bold": should_be_bold or run.get("bold", False),
                    "italic": run.get("italic", False),
                    "underline": run.get("underline", False),
                    "font_name": language_rules["preferred_fonts"][0],
                    "font_size": style_profile.font_sizes.get(element_type, "11pt"),
                    "font_color": style_profile.colors.get(element_type, "#000000")
                }
                new_formatting["runs"].append(new_run)
        else:
            # Create default run if none exists
            new_formatting["runs"] = [{
                "text": styled_element.get("translated_text", styled_element.get("original_text", "")),
                "bold": should_be_bold,
                "italic": False,
                "underline": False,
                "font_name": language_rules["preferred_fonts"][0],
                "font_size": style_profile.font_sizes.get(element_type, "11pt"),
                "font_color": style_profile.colors.get(element_type, "#000000")
            }]
        
        # Update element with new formatting
        styled_element["styled_formatting"] = new_formatting
        styled_element["style_profile"] = style_profile.name
        styled_element["language_adapted"] = True
        
        return styled_element
    
    def _run(self, 
             session_id: str,
             style_profile_name: str = "professional") -> str:
        """Apply styling to translated document content"""
        
        try:
            file_manager = DocumentFileManager()
            
            # Load translation agent output
            translation_output_path = file_manager.get_session_file(session_id, "02_style_agent_input.json")
            if not os.path.exists(translation_output_path):
                return f"Error: Translation output not found for session {session_id}"
            
            with open(translation_output_path, 'r', encoding='utf-8') as f:
                translation_data = json.load(f)
            
            # Extract key information
            session_metadata = translation_data.get("session_metadata", {})
            translation_context = translation_data.get("translation_context", {})
            document_elements = translation_data.get("document_elements", {})
            
            target_language = translation_context.get("target_language", "English")
            document_type = translation_context.get("document_type", "professional")
            
            # Get style profile and language rules
            style_profile = self.STYLE_PROFILES.get(style_profile_name, self.STYLE_PROFILES["professional"])
            language_rules = self.LANGUAGE_RULES.get(target_language.lower(), self.LANGUAGE_RULES["english"])
            
            # Process each element type
            styled_elements = {}
            elements_styled_count = {
                "document_title": 0,
                "main_headers": 0,
                "sub_headers": 0,
                "content_sections": 0,
                "tables": 0
            }
            
            # Style document title
            if "title" in document_elements:
                styled_elements["title"] = self._apply_style_profile(
                    "document_title", document_elements["title"], style_profile, language_rules
                )
                elements_styled_count["document_title"] = 1
            
            # Style headers
            styled_elements["headers"] = {}
            if "headers" in document_elements:
                for header_type in ["main_headers", "sub_headers"]:
                    if header_type in document_elements["headers"]:
                        styled_headers = []
                        for header in document_elements["headers"][header_type]:
                            element_type = "main_header" if header_type == "main_headers" else "sub_header"
                            styled_header = self._apply_style_profile(
                                element_type, header, style_profile, language_rules
                            )
                            styled_headers.append(styled_header)
                        styled_elements["headers"][header_type] = styled_headers
                        elements_styled_count[header_type] = len(styled_headers)
            
            # Style content sections - handle both "content" and "content_blocks" 
            styled_elements["content"] = {}
            
            # Check for content in "content" key
            if "content" in document_elements:
                for content_type in ["body_text", "special_content"]:
                    if content_type in document_elements["content"]:
                        styled_content = []
                        for content_item in document_elements["content"][content_type]:
                            styled_item = self._apply_style_profile(
                                content_type, content_item, style_profile, language_rules
                            )
                            styled_content.append(styled_item)
                        styled_elements["content"][content_type] = styled_content
                        elements_styled_count["content_sections"] += len(styled_content)
            
            # Check for content in "content_blocks" key (alternative structure)
            if "content_blocks" in document_elements:
                for content_type in ["body_text", "special_content"]:
                    if content_type in document_elements["content_blocks"]:
                        if content_type not in styled_elements["content"]:
                            styled_elements["content"][content_type] = []
                        
                        styled_content = []
                        for content_item in document_elements["content_blocks"][content_type]:
                            styled_item = self._apply_style_profile(
                                content_type, content_item, style_profile, language_rules
                            )
                            styled_content.append(styled_item)
                        styled_elements["content"][content_type].extend(styled_content)
                        elements_styled_count["content_sections"] += len(styled_content)
            
            # Style tables
            styled_elements["tables"] = []
            if "tables" in document_elements:
                for table in document_elements["tables"]:
                    # Tables don't need style profile application, just pass through with structure
                    styled_table = table.copy()
                    styled_table["table_styled"] = True
                    styled_elements["tables"].append(styled_table)
                elements_styled_count["tables"] = len(styled_elements["tables"])
            
            # Create styled content output
            styled_content = {
                "session_metadata": {
                    **session_metadata,
                    "style_processing_completed_at": datetime.now().isoformat(),
                    "ready_for_output_agent": True
                },
                "style_context": {
                    "style_profile": style_profile.name,
                    "target_language": target_language,
                    "language_direction": language_rules["writing_direction"],
                    "styling_completed_at": datetime.now().isoformat()
                },
                "language_adaptations": {
                    "writing_direction": language_rules["writing_direction"],
                    "preferred_fonts": language_rules["preferred_fonts"],
                    "text_alignment_default": language_rules["text_alignment_default"]
                },
                "styled_elements": styled_elements
            }
            
            # Create style summary
            style_summary = {
                "style_metadata": {
                    "profile_used": style_profile.name,
                    "document_type": document_type,
                    "language": target_language,
                    "styled_at": datetime.now().isoformat()
                },
                "elements_styled": elements_styled_count,
                "style_rules_applied": list(style_profile.font_sizes.keys()),
                "formatting_consistency": {
                    "font_families_used": language_rules["preferred_fonts"],
                    "color_scheme": list(style_profile.colors.values()),
                    "alignment_types": list(set(style_profile.alignments.values()))
                }
            }
            
            # Create output for Output Agent
            output_agent_input = {
                "session_metadata": styled_content["session_metadata"],
                "generation_context": {
                    "output_format": "docx",
                    "style_profile": style_profile.name,
                    "language": target_language,
                    "writing_direction": language_rules["writing_direction"],
                    "prepared_at": datetime.now().isoformat()
                },
                "document_structure": {
                    "title": styled_elements.get("title"),
                    "headers": styled_elements.get("headers", {}),
                    "content": styled_elements.get("content", {}),
                    "tables": styled_elements.get("tables", [])
                },
                "style_specifications": {
                    "fonts": style_profile.font_families,
                    "colors": style_profile.colors,
                    "alignments": style_profile.alignments,
                    "spacing": style_profile.spacing
                }
            }
            
            # Save all outputs
            styled_content_path = file_manager.get_session_file(session_id, "03_styled_content.json")
            with open(styled_content_path, 'w', encoding='utf-8') as f:
                json.dump(styled_content, f, indent=2, ensure_ascii=False)
            
            style_summary_path = file_manager.get_session_file(session_id, "03_style_summary.json")
            with open(style_summary_path, 'w', encoding='utf-8') as f:
                json.dump(style_summary, f, indent=2, ensure_ascii=False)
            
            output_agent_input_path = file_manager.get_session_file(session_id, "03_output_agent_input.json")
            with open(output_agent_input_path, 'w', encoding='utf-8') as f:
                json.dump(output_agent_input, f, indent=2, ensure_ascii=False)
            
            # Update session manifest
            file_manager.update_session_manifest(session_id, {
                "style_agent_completed": True,
                "styled_content_file": "03_styled_content.json",
                "style_summary_file": "03_style_summary.json",
                "output_agent_input_file": "03_output_agent_input.json",
                "total_elements_styled": sum(elements_styled_count.values()),
                "style_profile_used": style_profile.name
            })
            
            total_styled = sum(elements_styled_count.values())
            return f"Style analysis and adaptation completed successfully. Styled {total_styled} elements using '{style_profile.name}' profile for {target_language}. Language direction: {language_rules['writing_direction']}. Files saved: styled_content, style_summary, output_agent_input."
            
        except Exception as e:
            return f"Error in style processing: {str(e)}"


def create_style_agent() -> Agent:
    """Create the Style Agent with proper configuration"""
    
    # Create Azure OpenAI LLM
    azure_llm = AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        temperature=0.1
    )
    
    style_tool = DocumentStyleTool()
    
    return Agent(
        role='Document Style Specialist',
        goal='Analyze and adapt document formatting for target language requirements while maintaining visual consistency and readability',
        backstory="""You are an expert in document formatting and cross-language typography. 
        You understand how different languages require different formatting approaches, 
        from RTL languages like Arabic to character-based languages like Chinese. 
        Your expertise includes font selection, spacing optimization, color schemes, 
        and maintaining professional document appearance across language barriers.""",
        tools=[style_tool],
        llm=azure_llm,
        verbose=True,
        allow_delegation=False
    )


def create_style_task(agent: Agent, session_id: str, style_profile: str = "professional") -> Task:
    """Create the style adaptation task"""
    
    return Task(
        description=f"""Analyze and adapt the document formatting for the translated content in session {session_id}.

        Your responsibilities:
        1. Load the translation output from the Translation Agent
        2. Analyze the original document's formatting patterns
        3. Apply appropriate style profile ({style_profile}) for the target language
        4. Adapt formatting for language-specific requirements (RTL/LTR, fonts, spacing)
        5. Ensure visual consistency and professional appearance
        6. Generate styled content ready for document generation
        
        Use the document_style_tool to process the styling with profile: {style_profile}
        """,
        
        expected_output="""Complete style analysis and adaptation with:
        1. Styled content with adapted formatting for all elements
        2. Style summary with applied rules and consistency metrics
        3. Output agent input file with document structure and style specifications
        
        All files should be saved to the session directory for the Output Agent to use.""",
        
        agent=agent
    )


def run_style_agent(session_id: str, style_profile: str = "professional") -> str:
    """Run the Style Agent workflow"""
    
    # Create agent and task
    style_agent = create_style_agent()
    style_task = create_style_task(style_agent, session_id, style_profile)
    
    # Create and run crew
    crew = Crew(
        agents=[style_agent],
        tasks=[style_task],
        process=Process.sequential,
        verbose=True
    )
    
    # Execute the workflow
    result = crew.kickoff()
    
    return str(result)


if __name__ == "__main__":
    # Example usage
    session_id = "d212cbd859d2_20250621_125824"  # Replace with actual session ID
    result = run_style_agent(session_id, "professional")
    print("Style Agent Result:", result) 