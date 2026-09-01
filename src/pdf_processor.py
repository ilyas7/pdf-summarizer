# src/pdf_processor.py
"""PDF processing and AI summarization logic."""

import re
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import PyPDF2
from openai import OpenAI
from openai.types.chat import ChatCompletion

from .config import Config
from .models import PageContent, ProcessingResult, IntervalSummary

class PDFProcessor:
    """Main PDF processing class."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize PDF processor with OpenAI client."""
        self.api_key = api_key or Config.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        self.client = OpenAI(api_key=self.api_key)
        self.config = Config
        
    def extract_text_from_pdf(self, pdf_path: Path) -> List[str]:
        """Extract text from each page of PDF."""
        pages_text = []
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                # Limit pages if configured
                if Config.MAX_PAGES:
                    total_pages = min(total_pages, Config.MAX_PAGES)
                
                for i in range(total_pages):
                    page = pdf_reader.pages[i]
                    text = page.extract_text()
                    # Clean text
                    text = re.sub(r'\s+', ' ', text).strip()
                    pages_text.append(text if text else "[Empty page]")
                    
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        
        return pages_text
    
    def process_page(self, page_text: str, page_num: int) -> List[str]:
        """Process a single page using AI."""
        if not page_text.strip() or page_text == "[Empty page]":
            return []
        
        try:
            # Truncate if too long
            if len(page_text) > Config.MAX_TOKENS * 4:
                page_text = page_text[:Config.MAX_TOKENS * 4]
            
            completion = self.client.beta.chat.completions.parse(
                model=Config.MODEL_NAME,
                messages=[
                    {
                        "role": "system", 
                        "content": "Extract key knowledge points from this page. Return only the knowledge points in a structured format."
                    },
                    {"role": "user", "content": page_text}
                ],
                response_format=PageContent,
            )
            
            result = completion.choices[0].message.parsed
            return result.knowledge if result.has_content else []
            
        except Exception as e:
            print(f"Error processing page {page_num}: {e}")
            return []
    
    def generate_summary(self, knowledge_base: List[str], is_final: bool = True) -> str:
        """Generate comprehensive summary from knowledge base."""
        if not knowledge_base:
            return "No knowledge extracted from the document."
        
        # Prepare knowledge text
        if len(knowledge_base) > 50:
            knowledge_text = "\n".join([f"- {k}" for k in knowledge_base[:50]])
            knowledge_text += f"\n... and {len(knowledge_base) - 50} more points"
        else:
            knowledge_text = "\n".join([f"- {k}" for k in knowledge_base])
        
        try:
            system_prompt = (
                "Create a comprehensive, well-structured summary from the knowledge points provided. "
                "Format in markdown with clear sections. Include main themes, key concepts, and important details."
            )
            
            completion = self.client.chat.completions.create(
                model=Config.ANALYSIS_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Knowledge points:\n{knowledge_text}"}
                ],
                max_tokens=2000
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "Error generating summary."
    
    def save_summary(self, summary: str, prefix: str) -> Path:
        """Save summary to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_summary_{timestamp}.md"
        filepath = Config.SUMMARIES_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        return filepath
    
    def process_pdf(self, pdf_path: Path, progress_callback=None) -> ProcessingResult:
        """Main processing function."""
        # Extract text from PDF
        pages_text = self.extract_text_from_pdf(pdf_path)
        total_pages = len(pages_text)
        
        knowledge_base = []
        interval_summaries = []
        
        for i, page_text in enumerate(pages_text, 1):
            # Update progress
            if progress_callback:
                progress_callback(i, total_pages)
            
            # Process page
            knowledge = self.process_page(page_text, i)
            knowledge_base.extend(knowledge)
            
            # Generate interval summary
            if i % Config.ANALYSIS_INTERVAL == 0:
                interval_summary = self.generate_summary(knowledge_base, is_final=False)
                interval_path = self.save_summary(interval_summary, f"interval_{i}")
                interval_summaries.append(
                    IntervalSummary(
                        page=i,
                        summary=interval_summary,
                        path=str(interval_path)
                    )
                )
        
        # Generate final summary
        final_summary = self.generate_summary(knowledge_base, is_final=True)
        final_path = self.save_summary(final_summary, "final")
        
        # Save knowledge base
        knowledge_path = Config.KNOWLEDGE_DIR / f"knowledge_base_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(knowledge_path, 'w', encoding='utf-8') as f:
            json.dump(knowledge_base, f, indent=2)
        
        return ProcessingResult(
            total_pages=total_pages,
            knowledge_points=len(knowledge_base),
            final_summary=final_summary,
            final_summary_path=str(final_path),
            interval_summaries=interval_summaries,
            knowledge_base=knowledge_base
        )