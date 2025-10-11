# Document Translator

A multi-agent AI pipeline for translating Word documents while preserving formatting and structure. **Now supports FREE AI models!**

## Features

- **🆓 FREE AI Models**: Uses Groq and OpenRouter for cost-free translations
- **Multi-Language Support**: Translate to 12+ languages including RTL languages (Hebrew, Arabic, Urdu)
- **Format Preservation**: Maintains original document structure, tables, headers, and styling  
- **Professional Output**: Applies language-specific fonts and formatting rules
- **Multiple LLM Providers**: Choose from Groq (FREE), OpenRouter (FREE), or Azure OpenAI (PAID)

## Quick Start

1. **Setup Environment**
   ```bash
   pip install -r requirements.txt
   cp config.env.example config.env  # Add your FREE API key
   ```

2. **Get FREE API Key** (Choose one)
   - **Groq** (Recommended): https://console.groq.com/keys
   - **OpenRouter**: https://openrouter.ai/keys
   - No credit card required for either!

3. **Run Translation**
   ```bash
   python test_complete_pipeline.py
   ```

4. **Select Provider & Language**
   - Choose FREE LLM provider (Groq recommended)
   - Select target language from interactive menu
   - Provide path to your .docx file
   - Find translated document in `output/` folder

## LLM Providers

| Provider | Cost | Models | Speed | Setup |
|----------|------|--------|--------|-------|
| **Groq** | 🆓 FREE | Llama-3-70B, Mixtral | ⚡ Very Fast | [Get Key](https://console.groq.com/keys) |
| **OpenRouter** | 🆓 FREE Tier | Llama-3, Phi-3, Gemma | 🚀 Fast | [Get Key](https://openrouter.ai/keys) |
| **Azure OpenAI** | 💰 PAID | GPT-4, GPT-3.5 | 🐌 Slower | Azure Subscription |

## Architecture

4-agent CrewAI pipeline:
- **Parser**: Extracts document structure and content
- **Translation**: Translates text using your selected LLM
- **Style**: Applies language-specific formatting and fonts
- **Output**: Generates final Word document

## Supported Languages

English, Spanish, French, German, Italian, Portuguese, Chinese, Japanese, Korean, Russian, Arabic, Hebrew, Urdu + custom languages

## Requirements

- Python 3.8+
- FREE API key (Groq or OpenRouter recommended)
- Microsoft Word documents (.docx)
