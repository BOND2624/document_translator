"""
File Manager for Document Translation Pipeline

Handles saving and loading data between agents in the pipeline.
Each document gets a unique session ID for tracking through the pipeline.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import hashlib
import logging

logger = logging.getLogger(__name__)

class DocumentFileManager:
    """Manages file operations for the document translation pipeline."""
    
    def __init__(self, base_output_dir: str = "output", temp_dir: str = "temp"):
        self.base_output_dir = Path(base_output_dir)
        self.temp_dir = Path(temp_dir)
        
        # Ensure directories exist
        self.base_output_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        
        logger.info(f"DocumentFileManager initialized with output_dir: {self.base_output_dir}")
    
    def generate_session_id(self, input_file_path: str) -> str:
        """Generate a unique session ID for a document processing session."""
        # Create a hash based on filename and timestamp
        file_name = Path(input_file_path).name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        content = f"{file_name}_{timestamp}"
        session_id = hashlib.md5(content.encode()).hexdigest()[:12]
        return f"{session_id}_{timestamp}"
    
    def create_session_directory(self, session_id: str) -> Path:
        """Create a session-specific directory for all processing files."""
        session_dir = self.base_output_dir / session_id
        session_dir.mkdir(exist_ok=True)
        logger.info(f"Created session directory: {session_dir}")
        return session_dir
    
    def save_parser_output(self, session_id: str, parsed_data: Dict[str, Any], 
                          original_filename: str) -> Dict[str, str]:
        """Save parser agent output to files."""
        session_dir = self.create_session_directory(session_id)
        
        # Save complete parsed data
        parsed_file = session_dir / "01_parsed_structure.json"
        with open(parsed_file, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, indent=2, ensure_ascii=False)
        
        # Save semantic structure separately for easy access
        semantic_file = session_dir / "01_semantic_structure.json"
        semantic_data = {
            'semantic_structure': parsed_data.get('semantic_structure', {}),
            'document_outline': parsed_data.get('document_outline', []),
            'metadata': parsed_data.get('metadata', {}),
            'original_filename': original_filename,
            'session_id': session_id,
            'created_at': datetime.now().isoformat()
        }
        with open(semantic_file, 'w', encoding='utf-8') as f:
            json.dump(semantic_data, f, indent=2, ensure_ascii=False)
        
        # Save translatable content for Translation Agent
        translatable_file = session_dir / "01_translatable_content.json"
        translatable_content = self._extract_translatable_content(parsed_data)
        with open(translatable_file, 'w', encoding='utf-8') as f:
            json.dump(translatable_content, f, indent=2, ensure_ascii=False)
        
        # Create session manifest
        manifest = {
            'session_id': session_id,
            'original_filename': original_filename,
            'created_at': datetime.now().isoformat(),
            'stage': 'parsed',
            'files': {
                'parsed_structure': str(parsed_file.name),
                'semantic_structure': str(semantic_file.name),
                'translatable_content': str(translatable_file.name)
            }
        }
        
        manifest_file = session_dir / "session_manifest.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"Parser output saved for session {session_id}")
        return {
            'session_dir': str(session_dir),
            'parsed_structure': str(parsed_file),
            'semantic_structure': str(semantic_file),
            'translatable_content': str(translatable_file),
            'manifest': str(manifest_file)
        }
    
    def _extract_translatable_content(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract content that needs translation, organized by semantic type."""
        paragraphs = parsed_data.get('paragraphs', [])
        
        translatable_content = {
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
            'tables': parsed_data.get('tables', []),
            'translation_context': {
                'document_type': 'financial_report',  # Could be enhanced to detect automatically
                'preserve_formatting': True,
                'preserve_structure': True
            }
        }
        
        for para in paragraphs:
            if not para.get('is_translatable', True) or not para.get('text', '').strip():
                continue
                
            semantic_type = para.get('semantic_type', 'unknown')
            content_item = {
                'text': para.get('text', ''),
                'index': para.get('paragraph_index', 0),
                'style': para.get('style', ''),
                'semantic_type': semantic_type,
                'hierarchy_level': para.get('hierarchy_level'),
                'formatting': {
                    'alignment': para.get('alignment', 'left'),
                    'runs': para.get('runs', [])
                }
            }
            
            # Categorize content by semantic type
            if semantic_type == 'document_title':
                translatable_content['document_title'] = content_item
            elif semantic_type == 'main_header':
                translatable_content['headers']['main_headers'].append(content_item)
            elif semantic_type == 'sub_header':
                translatable_content['headers']['sub_headers'].append(content_item)
            elif semantic_type == 'body_text':
                translatable_content['content']['body_text'].append(content_item)
            elif semantic_type == 'special_content':
                translatable_content['content']['special_content'].append(content_item)
            elif semantic_type == 'list_item':
                translatable_content['content']['list_items'].append(content_item)
            elif semantic_type == 'quote':
                translatable_content['content']['quotes'].append(content_item)
            elif semantic_type == 'caption':
                translatable_content['content']['captions'].append(content_item)
        
        return translatable_content
    
    def load_parser_output(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load parser output for a session."""
        session_dir = self.base_output_dir / session_id
        
        if not session_dir.exists():
            logger.error(f"Session directory not found: {session_dir}")
            return None
        
        # Load complete parsed structure
        parsed_file = session_dir / "01_parsed_structure.json"
        if parsed_file.exists():
            with open(parsed_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        logger.error(f"Parsed structure file not found: {parsed_file}")
        return None
    
    def load_translatable_content(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load translatable content for Translation Agent."""
        session_dir = self.base_output_dir / session_id
        translatable_file = session_dir / "01_translatable_content.json"
        
        if translatable_file.exists():
            with open(translatable_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        logger.error(f"Translatable content file not found: {translatable_file}")
        return None
    
    def save_translation_output(self, session_id: str, translated_content: Dict[str, Any]) -> List[str]:
        """Save translation output to session directory."""
        
        session_dir = self.base_output_dir / session_id
        if not session_dir.exists():
            logger.error(f"Session directory not found: {session_dir}")
            return []
        
        saved_files = []
        
        try:
            # Save complete translation output
            translation_file = session_dir / "02_translated_content.json"
            with open(translation_file, 'w', encoding='utf-8') as f:
                json.dump(translated_content, f, indent=2, ensure_ascii=False)
            saved_files.append(str(translation_file))
            
            # Save translation summary
            summary_file = session_dir / "02_translation_summary.json"
            summary_data = {
                'translation_metadata': translated_content.get('translation_metadata', {}),
                'translation_summary': translated_content.get('translation_summary', {}),
                'stats': {
                    'title_translated': translated_content.get('document_title') is not None,
                    'headers_translated': {
                        'main_headers': len(translated_content.get('headers', {}).get('main_headers', [])),
                        'sub_headers': len(translated_content.get('headers', {}).get('sub_headers', []))
                    },
                    'content_translated': {
                        content_type: len(items) 
                        for content_type, items in translated_content.get('content', {}).items()
                    },
                    'tables_translated': len(translated_content.get('tables', []))
                }
            }
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False)
            saved_files.append(str(summary_file))
            
            # Save style agent input (organized by element types)
            style_input_file = session_dir / "02_style_agent_input.json"
            style_input = {
                'session_metadata': {
                    'session_id': session_id,
                                         'translation_completed_at': self._get_timestamp(),
                    'ready_for_style_agent': True
                },
                'translation_context': translated_content.get('translation_metadata', {}),
                'document_elements': {
                    'title': translated_content.get('document_title'),
                    'headers': translated_content.get('headers', {}),
                    'content_blocks': translated_content.get('content', {}),
                    'tables': translated_content.get('tables', [])
                },
                'style_requirements': {
                    'preserve_original_formatting': True,
                    'maintain_semantic_hierarchy': True,
                    'apply_target_language_conventions': True,
                    'professional_document_style': True
                }
            }
            
            with open(style_input_file, 'w', encoding='utf-8') as f:
                json.dump(style_input, f, indent=2, ensure_ascii=False)
            saved_files.append(str(style_input_file))
            
            # Update session manifest
            manifest_file = session_dir / "session_manifest.json"
            if manifest_file.exists():
                with open(manifest_file, 'r') as f:
                    manifest = json.load(f)
                
                manifest['stage'] = 'translated'
                manifest['files']['translated_content'] = str(translation_file.name)
                manifest['updated_at'] = datetime.now().isoformat()
                manifest['translation_completed'] = True
                manifest['files_saved'] = saved_files
                manifest['ready_for_style_agent'] = True
                
                with open(manifest_file, 'w') as f:
                    json.dump(manifest, f, indent=2)
            
            logger.info(f"Translation output saved for session {session_id}: {len(saved_files)} files")
            
        except Exception as e:
            logger.error(f"Error saving translation output: {str(e)}")
            return []
        
        return saved_files
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all processing sessions."""
        sessions = []
        
        for session_dir in self.base_output_dir.iterdir():
            if session_dir.is_dir():
                manifest_file = session_dir / "session_manifest.json"
                if manifest_file.exists():
                    with open(manifest_file, 'r') as f:
                        manifest = json.load(f)
                        sessions.append(manifest)
        
        return sorted(sessions, key=lambda x: x.get('created_at', ''), reverse=True)
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a processing session."""
        session_dir = self.base_output_dir / session_id
        manifest_file = session_dir / "session_manifest.json"
        
        if manifest_file.exists():
            with open(manifest_file, 'r') as f:
                return json.load(f)
        
        return None
    
    def get_session_file(self, session_id: str, filename: str) -> str:
        """Get the full path to a file in a session directory."""
        session_dir = self.base_output_dir / session_id
        return str(session_dir / filename)
    
    def update_session_manifest(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update the session manifest with new information."""
        session_dir = self.base_output_dir / session_id
        manifest_file = session_dir / "session_manifest.json"
        
        try:
            if manifest_file.exists():
                with open(manifest_file, 'r') as f:
                    manifest = json.load(f)
            else:
                manifest = {
                    'session_id': session_id,
                    'created_at': datetime.now().isoformat()
                }
            
            # Update manifest with new data
            manifest.update(updates)
            manifest['updated_at'] = datetime.now().isoformat()
            
            with open(manifest_file, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error updating session manifest: {str(e)}")
            return False
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat() 