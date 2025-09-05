from PyPDF2 import PdfReader
from fastapi import HTTPException
import io


#Extracat text content from pdf
def extract_text_from_pdf(file_content: bytes) -> str:
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PdfReader(pdf_file)
        text_content = ''
        for i, page in enumerate(pdf_reader.pages):
            text_content += page.extract_text() +"\n"
        return text_content.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")
    

def extract_text_from_txt(file_content: bytes) -> str:
    """Extract text content from TXT bytes"""
    try:
        return file_content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            return file_content.decode('latin-1')
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading TXT file: {str(e)}")
            