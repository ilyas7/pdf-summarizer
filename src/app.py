# src/app.py
"""Streamlit application for PDF Summarizer."""

import streamlit as st
import tempfile
from pathlib import Path
import json
from datetime import datetime

from .config import Config
from .pdf_processor import PDFProcessor
from .models import ProcessingResult

# Page configuration
st.set_page_config(
    page_title="PDF Summarizer",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
    }
    .download-btn {
        width: 100%;
        margin: 5px 0;
    }
    .stats-container {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'processed' not in st.session_state:
        st.session_state.processed = False
    if 'result' not in st.session_state:
        st.session_state.result = None

def render_header():
    """Render application header."""
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("📚 PDF Summarizer")
    st.markdown("### AI-Powered Knowledge Extraction & Summarization")
    st.markdown("Upload a PDF and get comprehensive summaries page by page")
    st.markdown('</div>', unsafe_allow_html=True)

def render_sidebar():
    """Render sidebar with configuration."""
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key. It will not be stored."
        )
        
        st.markdown("---")
        st.header("📊 Settings")
        
        interval = st.number_input(
            "Analysis Interval",
            min_value=1,
            max_value=50,
            value=Config.ANALYSIS_INTERVAL,
            help="Number of pages between interval summaries"
        )
        
        max_pages = st.number_input(
            "Max Pages (optional)",
            min_value=0,
            max_value=500,
            value=0,
            help="0 = process all pages"
        )
        
        st.markdown("---")
        if st.button("🗑️ Clear Cache"):
            st.cache_data.clear()
            st.success("Cache cleared!")
        
        return api_key, interval, max_pages

def render_stats(result: ProcessingResult):
    """Render processing statistics."""
    st.markdown('<div class="stats-container">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📄 Total Pages", result.total_pages)
    with col2:
        st.metric("💡 Knowledge Points", result.knowledge_points)
    with col3:
        st.metric("📊 Interval Summaries", len(result.interval_summaries))
    with col4:
        st.metric("⏱️ Processed", result.processed_at.strftime("%H:%M:%S"))
    st.markdown('</div>', unsafe_allow_html=True)

def render_download_section(result: ProcessingResult):
    """Render download buttons for different formats."""
    st.header("📥 Download Results")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Markdown", "Text", "JSON", "HTML"])
    
    with tab1:
        st.download_button(
            label="📥 Download Markdown",
            data=result.final_summary,
            file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    with tab2:
        st.download_button(
            label="📥 Download Text",
            data=result.final_summary,
            file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with tab3:
        json_data = json.dumps(result.dict(), indent=2, default=str)
        st.download_button(
            label="📥 Download JSON",
            data=json_data,
            file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with tab4:
        html_content = generate_html_preview(result)
        st.download_button(
            label="📥 Download HTML",
            data=html_content,
            file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            mime="text/html",
            use_container_width=True
        )

def generate_html_preview(result: ProcessingResult) -> str:
    """Generate HTML preview of the summary."""
    # Implementation similar to previous version
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>PDF Summary</title>
<style>
body {{ font-family: Arial; max-width: 800px; margin: 0 auto; padding: 20px; }}
h1 {{ color: #2c3e50; }}
</style>
</head>
<body>
<h1>📚 PDF Summary Report</h1>
<p>Generated: {result.processed_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
<h2>Final Summary</h2>
{result.final_summary}
</body>
</html>"""

def render_interval_summaries(result: ProcessingResult):
    """Render interval summaries in expandable sections."""
    if result.interval_summaries:
        st.header("📊 Interval Summaries")
        for interval in result.interval_summaries:
            with st.expander(f"📝 Summary after page {interval.page}"):
                st.markdown(interval.summary)

def main():
    """Main application function."""
    initialize_session_state()
    
    # Render header
    render_header()
    
    # Get configuration from sidebar
    api_key, interval, max_pages = render_sidebar()
    
    # Update config if changed
    if interval != Config.ANALYSIS_INTERVAL:
        Config.ANALYSIS_INTERVAL = interval
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload a PDF document to analyze"
    )
    
    if uploaded_file and api_key:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = Path(tmp_file.name)
        
        # Process button
        if st.button("🚀 Process PDF", type="primary", use_container_width=True):
            try:
                # Initialize processor
                processor = PDFProcessor(api_key=api_key)
                
                # Create progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def update_progress(current, total):
                    progress = current / total
                    progress_bar.progress(progress)
                    status_text.text(f"Processing page {current}/{total}...")
                
                # Process PDF
                with st.spinner("Processing PDF..."):
                    result = processor.process_pdf(tmp_path, update_progress)
                
                # Store in session state
                st.session_state.result = result
                st.session_state.processed = True
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                # Display results
                st.success("✅ Processing complete!")
                
                # Show statistics
                render_stats(result)
                
                # Show final summary
                st.header("🎯 Final Summary")
                with st.expander("Click to view full summary", expanded=True):
                    st.markdown(result.final_summary)
                
                # Show interval summaries
                render_interval_summaries(result)
                
                # Download section
                render_download_section(result)
                
            except Exception as e:
                st.error(f"❌ Error processing PDF: {str(e)}")
                
            finally:
                # Cleanup
                try:
                    tmp_path.unlink()
                except:
                    pass
    
    elif uploaded_file and not api_key:
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar.")
    
    else:
        st.info("👈 Upload a PDF file and enter your OpenAI API key to begin.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    ### 📖 How it works:
    1. **Upload PDF** - Upload your document
    2. **AI Analysis** - Each page is analyzed for knowledge points
    3. **Generate Summary** - Creates comprehensive summaries at intervals
    4. **Download Results** - Get summaries in multiple formats
    """)

if __name__ == "__main__":
    main()