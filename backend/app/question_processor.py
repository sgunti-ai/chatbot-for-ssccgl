import os
import re
import json
import hashlib
from typing import List, Dict, Optional
import PyPDF2
from .chroma_client import ChromaClient

class QuestionProcessor:
    def __init__(self, chroma_client: ChromaClient):
        self.chroma_client = chroma_client
        
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text_content += page.extract_text() + "\n"
                
                return text_content
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def extract_questions_from_text(self, text_content: str) -> List[Dict]:
        """Extract questions from text content"""
        questions = []
        
        # Normalize text - remove extra whitespaces and normalize line breaks
        text_content = re.sub(r'\n+', '\n', text_content)
        text_content = re.sub(r' +', ' ', text_content)
        
        # Split by sections
        sections = re.split(r'Section\s*:\s*', text_content, flags=re.IGNORECASE)
        
        for section in sections:
            if not section.strip():
                continue
                
            # Extract section name (first line after "Section :")
            section_lines = section.strip().split('\n')
            if not section_lines:
                continue
                
            section_name = section_lines[0].strip()
            section_content = '\n'.join(section_lines[1:])
            
            # Extract individual questions using multiple patterns
            question_blocks = self._split_into_question_blocks(section_content)
            
            for i, block in enumerate(question_blocks):
                question_data = self._parse_question_block(block, section_name, i + 1)
                if question_data and question_data.get('text'):
                    questions.append(question_data)
        
        return questions
    
    def _split_into_question_blocks(self, content: str) -> List[str]:
        """Split content into individual question blocks"""
        # Multiple patterns to detect question starts
        patterns = [
            r'Q\.\s*\d+',  # Q.1, Q.2, etc.
            r'Question\s*\d+',  # Question 1, Question 2, etc.
            r'\d+\.\s',  # 1. , 2. , etc.
        ]
        
        combined_pattern = '|'.join(patterns)
        splits = re.split(combined_pattern, content)
        
        # The first split is usually content before first question
        return splits[1:] if len(splits) > 1 else []
    
    def _parse_question_block(self, block: str, section: str, question_number: int) -> Optional[Dict]:
        """Parse individual question block"""
        try:
            lines = [line.strip() for line in block.split('\n') if line.strip()]
            if not lines:
                return None
            
            # Extract question text (first meaningful content)
            question_text = ""
            options = []
            correct_answer = None
            metadata = {}
            
            i = 0
            # Get question text (until we hit options or Ans)
            while i < len(lines):
                line = lines[i]
                if re.match(r'^(Ans|Options?|\(a\)|\(b\)|\(c\)|\(d\)|[✗✔X✅]|1\.|2\.|3\.|4\.)', line, re.IGNORECASE):
                    break
                question_text += " " + line
                i += 1
            
            question_text = question_text.strip()
            if not question_text:
                return None
            
            # Extract options
            while i < len(lines):
                line = lines[i]
                
                # Check for answer indicator
                ans_match = re.match(r'Ans\s*[:.]?\s*([^\n]+)', line, re.IGNORECASE)
                if ans_match:
                    correct_answer = ans_match.group(1).strip()
                    i += 1
                    continue
                
                # Check for options (1., 2., etc. or (a), (b), etc.)
                option_match = re.match(r'^([✗✔X✅\s]*)(\d+\.|\(a\)|\(b\)|\(c\)|\(d\))\s*(.+)', line, re.IGNORECASE)
                if option_match:
                    option_text = option_match.group(3).strip()
                    options.append(option_text)
                
                i += 1
            
            # If no structured options found, look for any lines that might be options
            if not options and i < len(lines):
                potential_options = lines[i:i+4]  # Next 4 lines might be options
                for opt in potential_options:
                    if len(opt) < 100:  # Reasonable option length
                        options.append(opt)
            
            # Generate unique ID
            question_id = hashlib.md5(f"{section}_{question_number}_{question_text}".encode()).hexdigest()[:12]
            
            # Prepare full text for embedding
            full_text = question_text
            if options:
                full_text += " Options: " + ", ".join(options)
            if correct_answer:
                full_text += f" Correct Answer: {correct_answer}"
            
            return {
                "id": f"q_{question_id}",
                "text": question_text,
                "options": options,
                "correct_answer": correct_answer,
                "subject": section,
                "question_number": question_number,
                "full_text": full_text,
                "metadata": metadata
            }
            
        except Exception as e:
            print(f"Error parsing question block: {e}")
            return None
    
    def process_pdf_file(self, pdf_path: str, namespace: str = "ssc-questions") -> int:
        """Process PDF file and upload questions to ChromaDB"""
        print(f"Processing PDF: {pdf_path}")
        
        # Extract text from PDF
        text_content = self.extract_text_from_pdf(pdf_path)
        print(f"Extracted {len(text_content)} characters from PDF")
        
        # Extract questions from text
        questions = self.extract_questions_from_text(text_content)
        print(f"Extracted {len(questions)} questions from text")
        
        # Upload to ChromaDB
        if questions:
            self.chroma_client.batch_insert_questions(questions, namespace)
            print(f"Successfully uploaded {len(questions)} questions to ChromaDB")
        
        return len(questions)
    
    def process_text_content(self, text_content: str, namespace: str = "ssc-questions") -> int:
        """Process text content and upload questions to ChromaDB"""
        print("Processing text content...")
        
        # Extract questions from text
        questions = self.extract_questions_from_text(text_content)
        print(f"Extracted {len(questions)} questions from text")
        
        # Upload to ChromaDB
        if questions:
            self.chroma_client.batch_insert_questions(questions, namespace)
            print(f"Successfully uploaded {len(questions)} questions to ChromaDB")
        
        return len(questions)
    
    def process_and_upload(self, file_content: str, namespace: str = "ssc-questions"):
        """Process file content (PDF path or text) and upload to ChromaDB"""
        try:
            # Check if it's a file path or direct text content
            if os.path.exists(file_content) and file_content.lower().endswith('.pdf'):
                # It's a PDF file path
                return self.process_pdf_file(file_content, namespace)
            else:
                # Assume it's text content
                return self.process_text_content(file_content, namespace)
        except Exception as e:
            print(f"Error processing content: {e}")
            raise
    
    def get_processing_stats(self, namespace: str = "ssc-questions") -> Dict:
        """Get statistics about processed questions"""
        # This would require additional methods in ChromaClient to count documents
        # For now, return basic stats
        return {
            "namespace": namespace,
            "status": "active",
            "message": "Processing completed successfully"
        }


# Utility function to create processor instance
def create_question_processor():
    """Factory function to create question processor with ChromaDB client"""
    from .chroma_client import ChromaClient
    chroma_client = ChromaClient()
    return QuestionProcessor(chroma_client)


# Example usage
if __name__ == "__main__":
    # Test the processor
    processor = create_question_processor()
    
    # Test with sample text
    sample_text = """
    Section : General Intelligence and Reasoning
    
    Q.1 What will come in place of the question mark (?) in the following equation?
    4515 × 5 - 431 + 3 + 821 = ?
    Ans
    X 1.1335
    X 2.1775  
    X 3.1575
    ✔ 4.1375
    
    Q.2 31 is related to 152 by certain logic. Following the same logic, 47 is related to 168.
    Ans
    X 1.180
    ✔ 2.187
    X 3.185
    X 4.190
    """
    
    count = processor.process_text_content(sample_text)
    print(f"Processed {count} questions")
    
    # Test search
    results = processor.chroma_client.semantic_search("profit and loss", top_k=3)
    for result in results:
        print(f"Question: {result['question']}")
        print(f"Similarity: {result['similarity_score']}")
        print("---")
