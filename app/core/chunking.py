from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter

def fixed_chunking(text: str, chunk_size: int = 800, overlap: int = 200):
    """Split text using CharacterTextSplitter (fixed chunking)"""
    splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=chunk_size,
        chunk_overlap=overlap
    )
    chunks = splitter.split_text(text)
    return chunks

def recursive_chunking(text: str, chunk_size: int = 800, overlap: int = 200):
    """Split Text using Recursive Character Text Splitter"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_text(text)
    return chunks