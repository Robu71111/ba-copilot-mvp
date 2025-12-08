"""
Document Parser Module
======================
Handles parsing of different document formats:
- .txt (plain text)
- .docx (Microsoft Word)
- .pdf (Adobe PDF)

Extracts text content for further processing.
"""

import io
from docx import Document
from PyPDF2 import PdfReader


class DocumentParser:
    """Parse various document formats and extract text"""
    
    @staticmethod
    def parse_txt(file_content):
        """
        Parse plain text file
        
        Args:
            file_content: File bytes or string
            
        Returns:
            Extracted text as string
        """
        try:
            if isinstance(file_content, bytes):
                text = file_content.decode('utf-8')
            else:
                text = file_content
            
            return text.strip()
        
        except Exception as e:
            raise Exception(f"Error parsing TXT file: {str(e)}")
    
    
    @staticmethod
    def parse_docx(file_content):
        """
        Parse Microsoft Word document (.docx)
        
        Args:
            file_content: File bytes from uploaded file
            
        Returns:
            Extracted text as string
        """
        try:
            # Read file content
            doc = Document(io.BytesIO(file_content))
            
            # Extract all paragraphs
            full_text = []
            for para in doc.paragraphs:
                if para.text.strip():  # Only add non-empty paragraphs
                    full_text.append(para.text)
            
            # Join paragraphs with double newline
            text = '\n\n'.join(full_text)
            
            return text.strip()
        
        except Exception as e:
            raise Exception(f"Error parsing DOCX file: {str(e)}")
    
    
    @staticmethod
    def parse_pdf(file_content):
        """
        Parse PDF document
        
        Args:
            file_content: File bytes from uploaded file
            
        Returns:
            Extracted text as string
        """
        try:
            # Create PDF reader
            pdf_reader = PdfReader(io.BytesIO(file_content))
            
            # Extract text from all pages
            full_text = []
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text.strip():
                    full_text.append(text)
            
            # Join pages with separator
            text = '\n\n--- Page Break ---\n\n'.join(full_text)
            
            return text.strip()
        
        except Exception as e:
            raise Exception(f"Error parsing PDF file: {str(e)}")
    
    
    @staticmethod
    def parse_document(file_name, file_content):
        """
        Auto-detect file type and parse accordingly
        
        Args:
            file_name: Name of the uploaded file
            file_content: File bytes
            
        Returns:
            Extracted text as string
        """
        # Get file extension
        extension = file_name.lower().split('.')[-1]
        
        # Parse based on extension
        if extension == 'txt':
            return DocumentParser.parse_txt(file_content)
        
        elif extension == 'docx':
            return DocumentParser.parse_docx(file_content)
        
        elif extension == 'pdf':
            return DocumentParser.parse_pdf(file_content)
        
        else:
            raise ValueError(f"Unsupported file format: .{extension}. Supported formats: .txt, .docx, .pdf")
    
    
    @staticmethod
    def validate_text(text, min_length=50):
        """
        Validate extracted text
        
        Args:
            text: Extracted text
            min_length: Minimum required length
            
        Returns:
            (is_valid, message)
        """
        if not text or not text.strip():
            return False, "No text content found in the document"
        
        if len(text.strip()) < min_length:
            return False, f"Text too short (minimum {min_length} characters required)"
        
        return True, "Text validation successful"


# Create parser instance
parser = DocumentParser()