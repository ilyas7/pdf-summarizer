# src/models.py
"""Pydantic models for PDF Summarizer."""

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class PageContent(BaseModel):
    """Response model for page content analysis."""
    has_content: bool = Field(description="Whether the page has relevant content")
    knowledge: List[str] = Field(default_factory=list, description="Extracted knowledge points")

class IntervalSummary(BaseModel):
    """Model for interval summary."""
    page: int
    summary: str
    path: str
    created_at: datetime = Field(default_factory=datetime.now)

class ProcessingResult(BaseModel):
    """Model for processing results."""
    total_pages: int
    knowledge_points: int
    final_summary: str
    final_summary_path: str
    interval_summaries: List[IntervalSummary]
    knowledge_base: List[str]
    processed_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }