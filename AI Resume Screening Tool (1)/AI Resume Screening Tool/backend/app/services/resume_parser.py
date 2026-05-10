import PyPDF2
import pdfplumber
from docx import Document
import re

class ResumeParser:
    """Parse resume files and extract information"""
    
    def extract_text(self, file_path):
        """Extract text from PDF or DOCX"""
        if file_path.lower().endswith('.pdf'):
            return self._extract_from_pdf(file_path)
        elif file_path.lower().endswith('.docx'):
            return self._extract_from_docx(file_path)
        elif file_path.lower().endswith('.doc'):
            raise NotImplementedError("DOC format requires python-docx or libreoffice")
        else:
            raise ValueError(f"Unsupported file type")
    
    def _extract_from_pdf(self, file_path):
        """Extract text from PDF"""
        text = ""
        try:
            # Try pdfplumber first
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
            except Exception as e1:
                # Fallback to PyPDF2
                try:
                    with open(file_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        for page in pdf_reader.pages:
                            text += page.extract_text() + "\n"
                except Exception as e2:
                    raise Exception(f"PDF extraction failed: {str(e2)}")
        except Exception as e:
            raise Exception(f"Error extracting PDF: {str(e)}")
        
        # Return empty string if no text extracted (not an error)
        return text if text.strip() else "Unable to extract text from PDF"
    
    def _extract_from_docx(self, file_path):
        """Extract text from DOCX"""
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            raise Exception(f"Error extracting DOCX: {str(e)}")
        return text
    
    def extract_candidate_info(self, text):
        """Extract basic candidate information"""
        info = {}
        
        # Simple email extraction
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_match = re.search(email_pattern, text)
        info['email'] = email_match.group(0) if email_match else None
        
        # Simple phone extraction
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, text)
        info['phone'] = phone_match.group(0) if phone_match else None
        
        # Get first line as name (simple approach)
        lines = text.split('\n')
        info['name'] = lines[0].strip() if lines else 'Unknown'
        
        return info
