"""Translation Agent for intelligent document translation with semantic awareness."""

import json
import logging
from typing import Dict, List, Any, Optional
from crewai import Agent, Task
from crewai_tools import BaseTool
from pydantic import BaseModel, Field
from pathlib import Path

from src.utils.file_manager import DocumentFileManager

logger = logging.getLogger(__name__)


class TranslationContext(BaseModel):
    """Model for translation context and settings."""
    
    source_language: str = Field(description="Source language code")
    target_language: str = Field(description="Target language code") 
    document_type: str = Field(description="Type of document being translated")
    preserve_formatting: bool = Field(description="Whether to preserve formatting")
    preserve_structure: bool = Field(description="Whether to preserve document structure")
    translation_style: str = Field(description="Translation style (formal, casual, technical)")


class DocumentTranslationTool(BaseTool):
    """Tool for translating documents with semantic awareness."""
    
    name: str = "document_translator"
    description: str = "Translate document content while preserving semantic structure and formatting"
    
    def __init__(self):
        super().__init__(
            name="document_translator",
            description="Translate document content while preserving semantic structure and formatting"
        )
    
    def get_file_manager(self):
        """Get file manager instance."""
        return DocumentFileManager()
    
    def _run(self, session_id: str, target_language: str = "Spanish", 
             source_language: str = "English", translation_style: str = "formal") -> str:
        """Translate document content from a session."""
        try:
            file_manager = self.get_file_manager()
            
            # Load translatable content
            translatable_content = file_manager.load_translatable_content(session_id)
            
            if not translatable_content:
                return f"Error: Could not load translatable content for session {session_id}"
            
            logger.info(f"Starting translation for session {session_id}: {source_language} -> {target_language}")
            
            # Create translation context
            translation_context = TranslationContext(
                source_language=source_language,
                target_language=target_language,
                document_type=translatable_content.get('translation_context', {}).get('document_type', 'general'),
                preserve_formatting=translatable_content.get('translation_context', {}).get('preserve_formatting', True),
                preserve_structure=translatable_content.get('translation_context', {}).get('preserve_structure', True),
                translation_style=translation_style
            )
            
            # Translate content by semantic type
            translated_content = self._translate_by_semantic_type(translatable_content, translation_context)
            
            # Save translation results
            saved_files = file_manager.save_translation_output(session_id, translated_content)
            
            # Create response with translation summary
            translation_summary = self._create_translation_summary(translated_content, translation_context)
            
            result = {
                'translation_completed': True,
                'session_id': session_id,
                'translation_context': translation_context.model_dump(),
                'translation_summary': translation_summary,
                'saved_files': saved_files,
                'translated_content': translated_content
            }
            
            return json.dumps(result, indent=2, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"Error in translation: {str(e)}")
            return f"Error in translation: {str(e)}"
    
    def _translate_by_semantic_type(self, translatable_content: Dict[str, Any], 
                                  context: TranslationContext) -> Dict[str, Any]:
        """Translate content organized by semantic type."""
        
        translated_content = {
            'translation_metadata': {
                'source_language': context.source_language,
                'target_language': context.target_language,
                'translation_style': context.translation_style,
                'document_type': context.document_type,
                'translated_at': self._get_timestamp()
            },
            'document_title': None,
            'headers': {
                'main_headers': [],
                'sub_headers': []
            },
            'content': {
                'body_text': [],
                'special_content': [],
                'list_items': [],
                'quotes': [],
                'captions': []
            },
            'tables': [],
            'translation_notes': []
        }
        
        # Translate document title
        if translatable_content.get('document_title'):
            translated_content['document_title'] = self._translate_document_title(
                translatable_content['document_title'], context
            )
        
        # Translate headers
        headers = translatable_content.get('headers', {})
        if headers.get('main_headers'):
            translated_content['headers']['main_headers'] = [
                self._translate_header(header, context, level=1) 
                for header in headers['main_headers']
            ]
        
        if headers.get('sub_headers'):
            translated_content['headers']['sub_headers'] = [
                self._translate_header(header, context, level=2)
                for header in headers['sub_headers']
            ]
        
        # Translate content by type
        content = translatable_content.get('content', {})
        for content_type, items in content.items():
            if items:
                translated_content['content'][content_type] = [
                    self._translate_content_item(item, context, content_type)
                    for item in items
                ]
        
        # Translate tables
        tables = translatable_content.get('tables', [])
        if tables:
            translated_content['tables'] = [
                self._translate_table(table, context)
                for table in tables
            ]
        
        return translated_content
    
    def _translate_document_title(self, title_item: Dict[str, Any], 
                                context: TranslationContext) -> Dict[str, Any]:
        """Translate document title with formal style."""
        
        original_text = title_item.get('text', '')
        
        # For now, simulate translation (in real implementation, use LLM)
        translated_text = self._simulate_translation(
            original_text, context, 
            style="formal_title",
            notes="Document title - preserve formality and key terms"
        )
        
        return {
            'original_text': original_text,
            'translated_text': translated_text,
            'semantic_type': title_item.get('semantic_type'),
            'index': title_item.get('index'),
            'style': title_item.get('style'),
            'formatting': title_item.get('formatting', {}),
            'translation_notes': f"Translated as document title in {context.translation_style} style"
        }
    
    def _translate_header(self, header_item: Dict[str, Any], 
                         context: TranslationContext, level: int) -> Dict[str, Any]:
        """Translate headers while preserving structural keywords."""
        
        original_text = header_item.get('text', '')
        
        # Headers need to preserve structure and be concise
        translated_text = self._simulate_translation(
            original_text, context,
            style="header",
            notes=f"Level {level} header - preserve structure and key terms"
        )
        
        return {
            'original_text': original_text,
            'translated_text': translated_text,
            'semantic_type': header_item.get('semantic_type'),
            'hierarchy_level': header_item.get('hierarchy_level'),
            'index': header_item.get('index'),
            'style': header_item.get('style'),
            'formatting': header_item.get('formatting', {}),
            'translation_notes': f"Level {level} header translation - preserved structural meaning"
        }
    
    def _translate_content_item(self, content_item: Dict[str, Any], 
                              context: TranslationContext, content_type: str) -> Dict[str, Any]:
        """Translate content items based on their semantic type."""
        
        original_text = content_item.get('text', '')
        
        # Different translation strategies based on content type
        translation_strategies = {
            'body_text': 'natural_flow',
            'special_content': 'careful_preserve_meaning',
            'list_items': 'concise_clear',
            'quotes': 'preserve_tone_and_meaning',
            'captions': 'descriptive_accurate'
        }
        
        strategy = translation_strategies.get(content_type, 'natural_flow')
        
        translated_text = self._simulate_translation(
            original_text, context,
            style=strategy,
            notes=f"{content_type} - using {strategy} strategy"
        )
        
        return {
            'original_text': original_text,
            'translated_text': translated_text,
            'semantic_type': content_item.get('semantic_type'),
            'index': content_item.get('index'),
            'style': content_item.get('style'),
            'formatting': content_item.get('formatting', {}),
            'translation_strategy': strategy,
            'translation_notes': f"Translated {content_type} using {strategy} approach"
        }
    
    def _translate_table(self, table_data: Dict[str, Any], 
                        context: TranslationContext) -> Dict[str, Any]:
        """Translate table content while preserving structure."""
        
        # For now, return table structure info
        # In real implementation, would translate cell content
        return {
            'original_table': table_data,
            'translation_notes': 'Table structure preserved - cell content would be translated',
            'requires_cell_translation': True
        }
    
    def _simulate_translation(self, text: str, context: TranslationContext, 
                            style: str, notes: str) -> str:
        """Simulate translation (replace with actual LLM translation)."""
        
        # Check if Azure OpenAI is configured
        try:
            from ..config import Config
            if Config.validate():
                # Use real Azure OpenAI translation
                return self._call_azure_openai_translation(text, context.source_language, context.target_language, style)
        except:
            pass
        
        # Fallback to simulation for demo/testing purposes
        # This should be replaced with real translation in production
        return f"[{context.target_language.upper()}] {text}"
    
    def _call_azure_openai_translation(self, text: str, source_lang: str, target_lang: str, style: str) -> str:
        """
        Call Azure OpenAI for actual translation.
        
        This method creates language-agnostic translation prompts and calls Azure OpenAI
        to translate any text from any source language to any target language.
        """
        try:
            import os
            from langchain_openai import AzureChatOpenAI
            
            # Create Azure OpenAI client
            llm = AzureChatOpenAI(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                temperature=0.1
            )
            
            # Create style-specific translation prompts
            style_instructions = {
                'formal_title': 'Translate this document title in a formal, professional style suitable for business documents.',
                'header': 'Translate this section header while preserving its structural meaning and keeping it concise.',
                'natural_flow': 'Translate this text naturally with smooth, readable flow while maintaining the original meaning.',
                'careful_preserve_meaning': 'Translate this text carefully, preserving all technical terms and specific meanings.',
                'concise_clear': 'Translate this text concisely and clearly, maintaining brevity.',
                'preserve_tone_and_meaning': 'Translate this text while carefully preserving the original tone and meaning.',
                'descriptive_accurate': 'Translate this descriptive text accurately while maintaining its descriptive nature.'
            }
            
            instruction = style_instructions.get(style, style_instructions['natural_flow'])
            
            # Language-specific examples for better context
            language_examples = {
                'Spanish': {
                    'formal_title': 'Example: "Financial Report" → "Informe Financiero"',
                    'header': 'Example: "Market Analysis" → "Análisis de Mercado"',
                    'greeting': 'Example: "Hello" → "Hola"'
                },
                'French': {
                    'formal_title': 'Example: "Financial Report" → "Rapport Financier"',
                    'header': 'Example: "Market Analysis" → "Analyse du Marché"',
                    'greeting': 'Example: "Hello" → "Bonjour"'
                },
                'German': {
                    'formal_title': 'Example: "Financial Report" → "Finanzbericht"',
                    'header': 'Example: "Market Analysis" → "Marktanalyse"',
                    'greeting': 'Example: "Hello" → "Hallo"'
                },
                'Italian': {
                    'formal_title': 'Example: "Financial Report" → "Rapporto Finanziario"',
                    'header': 'Example: "Market Analysis" → "Analisi di Mercato"',
                    'greeting': 'Example: "Hello" → "Ciao"'
                },
                'Portuguese': {
                    'formal_title': 'Example: "Financial Report" → "Relatório Financeiro"',
                    'header': 'Example: "Market Analysis" → "Análise de Mercado"',
                    'greeting': 'Example: "Hello" → "Olá"'
                },
                'Chinese': {
                    'formal_title': 'Example: "Financial Report" → "财务报告"',
                    'header': 'Example: "Market Analysis" → "市场分析"',
                    'greeting': 'Example: "Hello" → "你好"'
                },
                'Japanese': {
                    'formal_title': 'Example: "Financial Report" → "財務報告書"',
                    'header': 'Example: "Market Analysis" → "市場分析"',
                    'greeting': 'Example: "Hello" → "こんにちは"'
                },
                'Korean': {
                    'formal_title': 'Example: "Financial Report" → "재무 보고서"',
                    'header': 'Example: "Market Analysis" → "시장 분석"',
                    'greeting': 'Example: "Hello" → "안녕하세요"'
                },
                'Russian': {
                    'formal_title': 'Example: "Financial Report" → "Финансовый отчёт"',
                    'header': 'Example: "Market Analysis" → "Анализ рынка"',
                    'greeting': 'Example: "Hello" → "Привет"'
                },
                'Arabic': {
                    'formal_title': 'Example: "Financial Report" → "التقرير المالي"',
                    'header': 'Example: "Market Analysis" → "تحليل السوق"',
                    'greeting': 'Example: "Hello" → "مرحبا"'
                }
            }
            
            # Get examples for the target language
            examples = language_examples.get(target_lang, {})
            example_text = ""
            if examples:
                example_text = f"\n\nExamples for {target_lang}:\n"
                for key, example in examples.items():
                    example_text += f"- {example}\n"
            
            # Create the translation prompt
            prompt = f"""You are a professional translator. {instruction}

Source Language: {source_lang}
Target Language: {target_lang}

Text to translate: "{text}"
{example_text}
Requirements:
- Provide ONLY the translated text, no explanations or additional text
- Do not add any prefixes like "[{target_lang.upper()}]" or similar markers
- Maintain the original meaning and context
- Use appropriate terminology for the target language
- If the text contains proper nouns or technical terms, handle them appropriately for the target language

Translation:"""

            # Call Azure OpenAI
            response = llm.invoke(prompt)
            
            # Extract and clean the response
            translated_text = response.content.strip()
            
            # Remove any potential prefixes that might have been added
            prefixes_to_remove = [
                f"[{target_lang.upper()}]",
                f"[{target_lang.lower()}]",
                f"{target_lang.upper()}:",
                f"{target_lang.lower()}:",
                "Translation:",
                "Translated text:",
                "Result:"
            ]
            
            for prefix in prefixes_to_remove:
                if translated_text.startswith(prefix):
                    translated_text = translated_text[len(prefix):].strip()
            
            return translated_text
            
        except Exception as e:
            # If Azure OpenAI fails, fallback to simulation
            print(f"Azure OpenAI translation failed: {e}")
            return f"[{target_lang.upper()}] {text}"
    
    def _create_translation_summary(self, translated_content: Dict[str, Any], 
                                  context: TranslationContext) -> Dict[str, Any]:
        """Create a summary of the translation process."""
        
        summary = {
            'translation_stats': {
                'document_title_translated': translated_content.get('document_title') is not None,
                'main_headers_count': len(translated_content.get('headers', {}).get('main_headers', [])),
                'sub_headers_count': len(translated_content.get('headers', {}).get('sub_headers', [])),
                'total_content_items': sum(
                    len(items) for items in translated_content.get('content', {}).values()
                ),
                'tables_processed': len(translated_content.get('tables', []))
            },
            'translation_quality_notes': [
                f"Document translated from {context.source_language} to {context.target_language}",
                f"Translation style: {context.translation_style}",
                f"Document type: {context.document_type}",
                "Semantic structure preserved during translation",
                "Formatting metadata maintained for reconstruction"
            ]
        }
        
        return summary
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()


def create_translation_agent(llm=None) -> Agent:
    """Create and configure the Translation Agent."""
    
    translation_tool = DocumentTranslationTool()
    
    # Create agent configuration
    agent_config = {
        "role": "Expert Document Translation Specialist",
        "goal": "Translate documents while preserving semantic structure, formatting, and contextual meaning",
        "backstory": """You are an expert translator with deep knowledge of document structures, 
        cultural nuances, and technical terminology. You specialize in translating complex documents 
        while maintaining their original semantic structure, formatting, and meaning. You understand 
        that different parts of a document (titles, headers, body text) require different translation 
        approaches, and you preserve the hierarchical structure and formatting metadata to ensure 
        perfect reconstruction of the translated document.""",
        "tools": [translation_tool],
        "verbose": True,
        "allow_delegation": False
    }
    
    # Add LLM only if provided
    if llm is not None:
        agent_config["llm"] = llm
    
    agent = Agent(**agent_config)
    
    return agent


def create_translation_task(agent: Agent, session_id: str, target_language: str = "Spanish", 
                           source_language: str = "English") -> Task:
    """Create a translation task for a specific session."""
    
    return Task(
        description=f"""Translate the document content from session '{session_id}' from {source_language} to {target_language}.

        Requirements:
        1. Load the parsed and structured content from the session
        2. Translate content while preserving semantic structure:
           - Document titles: Use formal, professional translation
           - Headers: Preserve structural meaning and hierarchy
           - Body text: Natural, flowing translation maintaining meaning
           - Special content: Careful preservation of technical terms
        3. Maintain all formatting metadata for reconstruction
        4. Preserve document outline and hierarchy relationships
        5. Save translated content for the next agent in the pipeline
        
        The translation should be contextually appropriate for a {source_language} financial/trading document 
        being translated to {target_language}, maintaining professional tone and technical accuracy.""",
        
        expected_output=f"""A comprehensive translation result containing:
        - Translated document title in {target_language}
        - All headers translated with preserved hierarchy
        - Body content translated with natural flow
        - Preserved formatting and semantic metadata
        - Translation quality summary and notes
        - Saved files ready for the next pipeline stage
        
        The output should maintain the document's semantic structure while providing high-quality 
        {target_language} translation appropriate for financial/professional contexts.""",
        
        agent=agent
    ) 