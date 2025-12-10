# Document Translator

A multi-agent AI pipeline for translating Word documents while preserving formatting and structure.

## Features

- **Multi-Language Support**: Translate to 10+ languages 
- **Format Preservation**: Maintains original document structure, tables, headers, and styling
- **Professional Output**: Applies language-specific fonts and formatting rules
- **Azure OpenAI Integration**: Powered by GPT-4 for high-quality translations

## Quick Start

1. **Setup Environment**
   ```bash
   pip install -r requirements.txt
   cp .env.example .env  # Add your Azure OpenAI credentials
   ```

2. **Run Translation**
   ```bash
   python test_complete_pipeline.py
   ```

3. **Select Language & Document**
   - Choose target language from interactive menu
   - Provide path to your .docx file
   - Find translated document in `output/` folder

## Architecture

4-agent CrewAI pipeline:
- **Parser**: Extracts document structure and content
- **Translation**: Translates text using Azure OpenAI
- **Style**: Applies language-specific formatting and fonts
- **Output**: Generates final Word document

## Supported Languages

English, Spanish, French, German, Italian, Portuguese, Chinese, Japanese, Korean, Russian  +

## Requirements

- Python 3.8+
- Azure OpenAI API access
- Microsoft Word documents (.docx)
