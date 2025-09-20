"""
Document Translation System - Streamlit UI
A user-friendly interface for translating documents with professional styling
"""

import streamlit as st
import os
import time
import tempfile
from pathlib import Path
import json
from datetime import datetime

# Import the translation pipeline components
from src.agents.parser_agent import DocumentParserTool
from src.agents.translation_agent import DocumentTranslationTool
from src.agents.style_agent import run_style_agent
from src.agents.output_agent import run_output_agent
from src.utils.file_manager import DocumentFileManager


def setup_page_config():
    """Setup Streamlit page configuration"""
    st.set_page_config(
        page_title="Document Translator",
        page_icon="🌐",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def get_supported_languages():
    """Get list of supported LTR languages"""
    return {
        "Spanish": "Spanish",
        "French": "French", 
        "German": "German",
        "Italian": "Italian",
        "Portuguese": "Portuguese",
        "Chinese (Simplified)": "Chinese",
        "Japanese": "Japanese",
        "Korean": "Korean",
        "Russian": "Russian",
        "Hindi": "Hindi",
        "Thai": "Thai"
    }


def save_uploaded_file(uploaded_file):
    """Save uploaded file to temporary location"""
    try:
        # Create temp directory if it doesn't exist
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        
        # Save file with original name
        file_path = temp_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return str(file_path)
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return None


def run_translation_pipeline(file_path, target_language, progress_bar, status_text):
    """Run the complete translation pipeline with progress tracking"""
    
    try:
        # STEP 1: PARSER AGENT
        status_text.text("📊 Step 1/4: Analyzing document structure...")
        progress_bar.progress(10)
        
        parser_tool = DocumentParserTool()
        parser_result = parser_tool._run(file_path, save_to_files=True)
        
        # Extract session ID
        try:
            result_data = json.loads(parser_result)
            session_id = result_data.get("session_info", {}).get("session_id")
            if not session_id:
                raise ValueError("No session ID found")
        except:
            st.error("Failed to parse document or extract session ID")
            return None, None
        
        progress_bar.progress(25)
        
        # STEP 2: TRANSLATION AGENT
        status_text.text(f"🌐 Step 2/4: Translating content to {target_language}...")
        progress_bar.progress(40)
        
        translation_tool = DocumentTranslationTool()
        translation_result = translation_tool._run(
            session_id=session_id,
            target_language=target_language,
            source_language="English",
            translation_style="formal"
        )
        
        progress_bar.progress(55)
        
        # STEP 3: STYLE AGENT
        status_text.text("🎨 Step 3/4: Applying professional styling...")
        progress_bar.progress(70)
        
        style_result = run_style_agent(session_id, "professional")
        
        progress_bar.progress(85)
        
        # STEP 4: OUTPUT AGENT
        status_text.text("📝 Step 4/4: Generating final document...")
        progress_bar.progress(95)
        
        output_filename = f"{target_language}_Translation_{session_id}.docx"
        output_result = run_output_agent(session_id, output_filename)
        
        progress_bar.progress(100)
        status_text.text("✅ Translation completed successfully!")
        
        return session_id, output_filename
        
    except Exception as e:
        st.error(f"Pipeline error: {str(e)}")
        return None, None


def get_download_path(session_id, filename):
    """Get the full path to the generated document"""
    file_manager = DocumentFileManager()
    session_dir = Path(file_manager.base_output_dir) / session_id
    return session_dir / filename


def display_translation_summary(session_id):
    """Display translation summary and statistics"""
    try:
        file_manager = DocumentFileManager()
        
        # Load translation summary
        summary_path = file_manager.get_session_file(session_id, "02_translation_summary.json")
        if os.path.exists(summary_path):
            with open(summary_path, 'r', encoding='utf-8') as f:
                summary = json.load(f)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Translation Statistics")
                stats = summary.get('stats', {})
                
                if stats.get('title_translated'):
                    st.write("✅ Document title translated")
                
                headers = stats.get('headers_translated', {})
                if headers:
                    st.write(f"📝 Main headers: {headers.get('main_headers', 0)}")
                    st.write(f"📝 Sub headers: {headers.get('sub_headers', 0)}")
                
                content = stats.get('content_translated', {})
                if content:
                    for content_type, count in content.items():
                        if count > 0:
                            st.write(f"📄 {content_type.replace('_', ' ').title()}: {count}")
                
                tables = stats.get('tables_translated', 0)
                if tables > 0:
                    st.write(f"📋 Tables processed: {tables}")
            
            with col2:
                st.subheader("🎯 Quality Notes")
                notes = summary.get('translation_quality_notes', [])
                for note in notes:
                    st.write(f"• {note}")
                    
    except Exception as e:
        st.warning(f"Could not load translation summary: {str(e)}")


def extract_document_preview(file_path: Path) -> str:
    """Extract text preview from DOCX document"""
    try:
        from docx import Document
        doc = Document(file_path)
        
        text_parts = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text.strip())
                if len(' '.join(text_parts)) > 1000:  # Limit preview length
                    break
        
        return ' '.join(text_parts)
    except Exception as e:
        return f"Preview error: {str(e)}"


def main():
    """Main Streamlit application"""
    setup_page_config()
    
    # Header
    st.title("🌐 Document Translation System")
    st.markdown("""
    **Transform your documents with AI-powered translation while preserving professional formatting**
    
    Supports DOCX and TXT files with intelligent styling and layout preservation.
    """)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # File upload
        st.subheader("📁 Upload Document")
        uploaded_file = st.file_uploader(
            "Choose a document to translate",
            type=['docx', 'txt'],
            help="Supported formats: DOCX, TXT"
        )
        
        # Language selection
        st.subheader("🌍 Target Language")
        languages = get_supported_languages()
        target_language = st.selectbox(
            "Select target language",
            options=list(languages.keys()),
            help="Choose the language to translate your document to"
        )
        
        # Translation style
        st.subheader("🎨 Style Profile")
        style_profile = st.selectbox(
            "Select styling",
            options=["Professional"],
            help="Professional styling with proper fonts and formatting"
        )
        
        # Info section
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        This system uses advanced AI to:
        - 📊 Analyze document structure
        - 🌐 Translate content intelligently  
        - 🎨 Apply professional styling
        - 📝 Generate publication-ready documents
        """)
    
    # Main content area
    if uploaded_file is not None:
        # Display file info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📄 File Name", uploaded_file.name)
        with col2:
            st.metric("📏 File Size", f"{uploaded_file.size / 1024:.1f} KB")
        with col3:
            st.metric("🎯 Target Language", target_language)
        
        st.markdown("---")
        
        # Translation button
        if st.button("🚀 Start Translation", type="primary", use_container_width=True):
            
            # Save uploaded file
            file_path = save_uploaded_file(uploaded_file)
            if not file_path:
                st.error("Failed to save uploaded file")
                return
            
            # Create progress tracking
            progress_container = st.container()
            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                start_time = time.time()
                
                # Run translation pipeline
                session_id, output_filename = run_translation_pipeline(
                    file_path, languages[target_language], progress_bar, status_text
                )
                
                end_time = time.time()
                
                if session_id and output_filename:
                    # Success!
                    st.success(f"🎉 Translation completed in {end_time - start_time:.1f} seconds!")
                    
                    # Enhanced Download & Preview Section
                    st.markdown("---")
                    st.subheader("📥 Your Translated Document")
                    
                    download_path = get_download_path(session_id, output_filename)
                    
                    if download_path.exists():
                        # File information
                        file_size = download_path.stat().st_size / 1024
                        modification_time = datetime.fromtimestamp(download_path.stat().st_mtime)
                        
                        # Create columns for better layout
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"""
                            **📄 File Name:** `{output_filename}`  
                            **📊 File Size:** {file_size:.1f} KB  
                            **🕒 Generated:** {modification_time.strftime('%Y-%m-%d %H:%M:%S')}  
                            **🌐 Language:** {target_language}  
                            **📋 Session:** `{session_id}`
                            """)
                        
                        with col2:
                            # Download button
                            with open(download_path, "rb") as file:
                                st.download_button(
                                    label="⬇️ Download Document",
                                    data=file.read(),
                                    file_name=output_filename,
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    use_container_width=True,
                                    type="primary"
                                )
                            
                            # Copy file path button
                            if st.button("📋 Copy File Path", use_container_width=True):
                                st.code(str(download_path))
                                st.success("File path ready to copy!")
                        
                        # Document Preview Section
                        st.markdown("---")
                        with st.expander("👁️ Document Preview", expanded=False):
                            try:
                                preview_text = extract_document_preview(download_path)
                                if preview_text:
                                    st.markdown("**First 500 characters of translated content:**")
                                    st.text_area(
                                        "Preview", 
                                        preview_text[:500] + "..." if len(preview_text) > 500 else preview_text,
                                        height=200,
                                        disabled=True
                                    )
                                else:
                                    st.info("Preview not available for this document type.")
                            except Exception as e:
                                st.warning(f"Could not generate preview: {str(e)}")
                        
                        # Enhanced Action Buttons
                        st.markdown("---")
                        st.markdown("**🚀 Quick Actions:**")
                        action_col1, action_col2, action_col3 = st.columns(3)
                        
                        with action_col1:
                            if st.button("📂 Open Output Folder", use_container_width=True):
                                folder_path = download_path.parent
                                try:
                                    import subprocess
                                    subprocess.run(f'explorer "{folder_path}"', shell=True)
                                    st.success("Output folder opened!")
                                except:
                                    st.info(f"Output folder: {folder_path}")
                        
                        with action_col2:
                            if st.button("📄 Open Document", use_container_width=True):
                                try:
                                    import subprocess
                                    subprocess.run(f'start "" "{download_path}"', shell=True)
                                    st.success("Document opened!")
                                except:
                                    st.info("Please download and open the document manually.")
                        
                        with action_col3:
                            if st.button("🔄 Translate Another", use_container_width=True):
                                st.rerun()
                        
                        # Display translation summary
                        st.markdown("---")
                        display_translation_summary(session_id)
                        
                        # Detailed session info
                        with st.expander("🔍 Session Details"):
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.write(f"**Session ID:** `{session_id}`")
                                st.write(f"**Processing Time:** {end_time - start_time:.1f} seconds")
                                st.write(f"**Output Directory:** `output/{session_id}/`")
                            with col_b:
                                st.write(f"**Original File:** `{uploaded_file.name}`")
                                st.write(f"**Target Language:** {target_language}")
                                st.write(f"**File Type:** {uploaded_file.type}")
                            
                    else:
                        st.error("Generated document not found. Please try again.")
                else:
                    st.error("Translation failed. Please check your document and try again.")
                
                # Cleanup temp file
                try:
                    os.remove(file_path)
                except:
                    pass
    
    else:
        # Welcome message
        st.markdown("### 👋 Welcome to the Document Translation System")
        st.markdown("""
        Get started by uploading a document using the sidebar. Our AI-powered system will:
        
        1. **📊 Analyze** your document's structure and formatting
        2. **🌐 Translate** content while preserving meaning and context  
        3. **🎨 Style** the document with professional formatting
        4. **📝 Generate** a publication-ready translated document
        
        ---
        
        #### 🚀 Features
        - **Smart Translation**: Context-aware translation that preserves technical terms
        - **Format Preservation**: Maintains original styling, fonts, and layout
        - **Professional Output**: Publication-ready documents with proper typography
        - **Multi-Language Support**: 11+ languages with native font support
        - **Fast Processing**: Complete translation in under 30 seconds
        
        #### 📁 Supported Formats
        - **DOCX**: Microsoft Word documents with full formatting
        - **TXT**: Plain text files with automatic styling
        
        Upload a document to begin! 📤
        """)


if __name__ == "__main__":
    main()
