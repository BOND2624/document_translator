# Multi-Agent Document Translation Pipeline

A sophisticated document translation pipeline built with CrewAI and Azure OpenAI, featuring 5 specialized agents for comprehensive document processing.

## 🚀 Features

- **Multi-format support**: DOCX and TXT files
- **Formatting preservation**: Maintains fonts, colors, styles, and layout
- **Multi-language support**: Handles RTL/LTR languages
- **Quality assurance**: Built-in validation and quality reporting
- **Modular architecture**: Step-by-step agent development and testing

## 🏗️ Architecture

The pipeline consists of 5 specialized agents:

1. **Parser Agent** ✅ - Extract text + structure from documents, preserve formatting metadata
2. **Translation Agent** 🔄 - Translate content using LLM while maintaining context
3. **Style Agent** 🔄 - Analyze and adapt formatting for target language
4. **Output Agent** 🔄 - Generate styled documents in DOCX format
5. **QA Agent** 🔄 - Validate translation accuracy and style consistency

## 📋 Prerequisites

- Python 3.8+
- Azure OpenAI account and API key
- Azure OpenAI deployment (GPT-4 recommended)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd doc_translation
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure Azure OpenAI:
```bash
cp config.env.example config.env
# Edit config.env with your Azure OpenAI credentials
```

## ⚙️ Configuration

Edit `config.env` with your Azure OpenAI settings:

```env
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
```

## 🧪 Testing

### Test Parser Agent (Current)

```bash
python test_parser.py
```

This will:
- Create test documents (DOCX and TXT)
- Test document parsing functionality
- Validate formatting extraction
- Display parsing results

### Expected Output

```
📊 Found 4 paragraphs
📊 Found 1 tables
📊 Fonts used: ['Arial', 'Default']
📊 Has formatting: True
```

## 📁 Project Structure

```
doc_translation/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   └── agents/
│       ├── __init__.py
│       ├── parser_agent.py    # ✅ Document parsing agent
│       ├── translation_agent.py  # 🔄 Coming next
│       ├── style_agent.py     # 🔄 Coming next
│       ├── output_agent.py    # 🔄 Coming next
│       └── qa_agent.py        # 🔄 Coming next
├── input/                     # Input documents
├── output/                    # Generated documents
├── temp/                      # Temporary files
├── test_parser.py            # Parser agent test
├── requirements.txt          # Dependencies
├── config.env               # Environment configuration
└── README.md               # This file
```

## 🔧 Current Status

### ✅ Parser Agent (Completed)

The Parser Agent can:
- Parse DOCX and TXT files
- Extract text content with paragraph structure
- Preserve formatting metadata (fonts, colors, styles)
- Handle tables with cell-level formatting
- Generate comprehensive JSON structure for document reconstruction

### 🔄 Next Steps

1. **Translation Agent**: Implement LLM-based translation with context preservation
2. **Style Agent**: Add formatting analysis and language-specific adaptations
3. **Output Agent**: Create DOCX generation with preserved formatting
4. **QA Agent**: Add quality validation and reporting
5. **Pipeline Integration**: Combine all agents into a complete workflow

## 🚀 Getting Started

1. Install dependencies and configure Azure OpenAI
2. Run the parser test to validate setup:
   ```bash
   python test_parser.py
   ```
3. Review the parsed document structure
4. Proceed to the next agent implementation

## 📊 Data Flow

```
Document → Parser Agent → Translation Agent → Style Agent → Output Agent → QA Agent
    ↓           ↓              ↓               ↓             ↓           ↓
  Raw File   JSON Structure  Translated   Styled Content  DOCX File  Quality Report
```

## 🎯 Usage Example

```python
from src.agents.parser_agent import create_parser_agent, create_parsing_task
from crewai import Crew

# Create agent and task
agent = create_parser_agent()
task = create_parsing_task("input/document.docx")

# Create and run crew
crew = Crew(agents=[agent], tasks=[task])
result = crew.kickoff()
```

## 🤝 Contributing

This project is built step-by-step. Each agent is developed, tested, and validated before moving to the next one.

## 📝 License

[Add your preferred license here]

## 📞 Support

[Add contact information or support channels] 