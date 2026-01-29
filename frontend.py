import streamlit as st
import os
from pathlib import Path
import tempfile
import shutil
from converter import process_images_to_docx

st.set_page_config(
    page_title="Handwritten Notes to DOCX Converter",
    layout="wide"
)
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-size: 1.1rem;
        padding: 0.5rem;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #145a8c;
    }
    .success-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .info-box {
        padding: 1rem;
        border-radius: 5px;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

if 'converted_file' not in st.session_state:
    st.session_state.converted_file = None
if 'processing' not in st.session_state:
    st.session_state.processing = False

st.markdown('<div class="main-header">Handwritten Notes to DOCX Converter</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Convert your handwritten notes images into structured Word documents</div>', unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    <strong>ℹ How it works:</strong>
    <ul>
        <li>Upload one or more images of your handwritten notes</li>
        <li>The system will extract text and detect diagrams automatically</li>
        <li>A structured Word document will be generated with extracted text and diagrams</li>
    </ul>
    <strong>Supported formats:</strong> JPG, JPEG, PNG
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Upload Images")
    
    uploaded_files = st.file_uploader(
        "Drag and drop images here, or click to browse",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        help="Upload images of your handwritten notes. You can select multiple files at once."
    )
    
    if uploaded_files:
        st.success(f"{len(uploaded_files)} file(s) uploaded successfully")
        with st.expander("Preview Uploaded Images", expanded=False):
            preview_cols = st.columns(min(3, len(uploaded_files)))
            for idx, uploaded_file in enumerate(uploaded_files[:6]):  # Show max 6 previews
                col_idx = idx % 3
                with preview_cols[col_idx]:
                    st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)
            
            if len(uploaded_files) > 6:
                st.info(f"+ {len(uploaded_files) - 6} more images...")
        
        st.markdown("---")
        output_filename = st.text_input(
            "Output Filename",
            value="handwritten_notes.docx",
            help="Enter the name for your output Word document"
        )
        
        if not output_filename.endswith('.docx'):
            output_filename += '.docx'
        
        convert_button = st.button("Convert to DOCX", type="primary", disabled=st.session_state.processing)
        
        if convert_button:
            st.session_state.processing = True
            st.session_state.converted_file = None
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir_path = Path(temp_dir)
                image_paths = []
                for uploaded_file in uploaded_files:
                    file_path = temp_dir_path / uploaded_file.name
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    image_paths.append(str(file_path))
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("Processing images...")
                    progress_bar.progress(20)
                    
                    status_text.text("Extracting text and diagrams...")
                    progress_bar.progress(40)
                    
                    output_path = temp_dir_path / output_filename
                    process_images_to_docx(image_paths, str(output_path))
                    
                    progress_bar.progress(80)
                    status_text.text("Generating Word document...")
                    
                    with open(output_path, "rb") as f:
                        st.session_state.converted_file = {
                            'data': f.read(),
                            'name': output_filename
                        }
                    
                    progress_bar.progress(100)
                    status_text.text("Conversion complete!")
                    
                    st.success("Document created successfully!")
                    
                except Exception as e:
                    st.error(f"Error during conversion: {str(e)}")
                    st.exception(e)
                finally:
                    st.session_state.processing = False
        
        if st.session_state.converted_file:
            st.markdown("---")
            st.subheader("Download Your Document")
            
            st.download_button(
                label="Download DOCX",
                data=st.session_state.converted_file['data'],
                file_name=st.session_state.converted_file['name'],
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary"
            )
            
            st.markdown("""
            <div class="success-box">
                Your document is ready! Click the button above to download.
            </div>
            """, unsafe_allow_html=True)

with col2:
    st.subheader("Features")
    st.markdown("""
    **What this tool does:**
    
    **Text Extraction**
    - Extracts handwritten text from images
    - Preserves text structure and formatting
    - Handles multiple pages
    
    **Diagram Detection**
    - Automatically detects diagrams and figures
    - Crops and extracts diagrams separately
    - Embeds diagrams in the document
    
    **Document Generation**
    - Creates professional Word documents
    - Organizes content by page
    - Separates text and diagrams clearly
    
    ---
    
    **Tips for best results:**
    - Use clear, high-resolution images
    - Ensure good lighting and contrast
    - Upload pages in the correct order
    - Avoid blurry or distorted images
    """)

    if uploaded_files:
        st.markdown("---")
        st.subheader("Current Session")
        st.metric("Images Uploaded", len(uploaded_files))
        
        total_size = sum(file.size for file in uploaded_files) / (1024 * 1024)  # Convert to MB
        st.metric("Total Size", f"{total_size:.2f} MB")

st.markdown("---")