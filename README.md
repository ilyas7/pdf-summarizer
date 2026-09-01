# 📚 PDF Summarizer

AI-powered PDF knowledge extraction and summarization application.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28.0-FF4B4B.svg)](https://streamlit.io/)

## ✨ Features

- 📄 **PDF Upload**: Upload any PDF document
- 🤖 **AI-Powered Analysis**: Uses OpenAI GPT for knowledge extraction
- 📊 **Page-by-Page Processing**: Process each page individually
- 📝 **Multiple Download Formats**: Markdown, Text, JSON, HTML
- 💾 **Knowledge Base**: Extracted knowledge points saved as JSON
- 🔄 **Interval Summaries**: Generate summaries at specified intervals

## 🚀 Quick Start

### Local Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/pdf-summarizer.git
cd pdf-summarizer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Copy environment file
cp src/.env.example .env

# Edit .env with your OpenAI API key
nano .env

# Run the application
streamlit run src/app.py