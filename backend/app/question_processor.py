import hashlib
import os
import re
from typing import Dict, List, Optional


class QuestionProcessor:
    def __init__(self):
        self.current_section = None
        # Enable debug when SSC_DEBUG env var is truthy (1/true/yes)
        self.debug = str(os.getenv("SSC_DEBUG", "")).lower() in ("1", "true", "yes")

    def _log(self, msg: str) -> None:
        if self.debug:
            print(f"QuestionProcessor: {msg}")

    def _generate_question_id(self, text: str) -> str:
        return f"q_{hashlib.md5(text.encode()).hexdigest()[:8]}"

    def _is_question_start(self, line: str) -> bool:
        """Heuristic to decide whether a line starts a new question.

        We treat a line as a question start if:
        - it begins with 'Q' (e.g. 'Q.1', 'Q1.'), or
        - it begins with a number and contains a question mark, or
        - it contains a question mark anywhere (fallback).
        This avoids treating option lines like '1. 3' or '(A) London' as new questions.
        """
        s = line.strip()
        if not s:
            return False
        if re.match(r"^Q\.?\s*\d+", s, re.IGNORECASE):
            return True
        if re.match(r"^\d+\.", s) and "?" in s:
            return True
        if "?" in s:
            return True
        return False

    def _split_into_question_blocks(self, text: str) -> List[str]:
        # Detect and store section (multi-word allowed)
        section_match = re.search(r'Section\s*:?\s*([\w\s]+?)(?:\n|$)', text, re.IGNORECASE)
        if section_match:
            self.current_section = section_match.group(1).strip()
            self._log(f"Processing section: {self.current_section}")

        # Remove leading section line(s)
        text = re.sub(r'^Section\s*:.*?\n', '', text, flags=re.IGNORECASE | re.MULTILINE)

        # Build blocks by scanning lines and grouping until next question start
        lines = [line.rstrip() for line in text.splitlines()]
        blocks: List[str] = []
        current_block_lines: List[str] = []

        for i, line in enumerate(lines):
            # skip empty lines but preserve as separator
            if not line.strip():
                continue

            if self._is_question_start(line):
                # start a new block
                if current_block_lines:
                    blocks.append("\n".join(current_block_lines).strip())
                current_block_lines = [line.strip()]
            else:
                # continuation (option/answer line)
                if current_block_lines:
                    current_block_lines.append(line.strip())
                else:
                    # If no current block, treat this as orphan content; start a new block
                    current_block_lines = [line.strip()]

        # append last block
        if current_block_lines:
            blocks.append("\n".join(current_block_lines).strip())

        return blocks

    def _parse_question_block(self, block: str) -> Optional[Dict]:
        try:
            lines = [line.strip() for line in block.split('\n') if line.strip()]
            if not lines:
                return None

            # Extract question text from first line (remove leading Q/number prefixes)
            q_text_match = re.match(r"(?:Q\.?\s*)?(?:\d+\.?\s*)?(.*\?)?", lines[0])
            # Fallback: take whole first line if regex didn't capture a proper question
            question_text = lines[0]
            if q_text_match and q_text_match.group(1):
                question_text = q_text_match.group(1).strip()
            else:
                # if first line ends with '?', use it; otherwise strip numbering
                question_text = re.sub(r"^(?:Q\.?\s*)?(?:\d+\.?\s*)?", "", lines[0]).strip()

            self._log(f"Question text: {question_text}")

            # Collect options: various formats like '1. text', '(1) text', '(A) text', 'A. text', '1) text'
            options: List[str] = []
            for line in lines[1:]:
                # Match options: e.g. '1. text', '(1) text', 'A. text', '(A) text', '1) text'
                opt_match = re.match(r"^\(?\s*([1-4A-D])\s*[\.\)]\s*(.+)$", line, re.IGNORECASE)
                if opt_match:
                    options.append(opt_match.group(2).strip())

            # Find answer (look across lines)
            answer = None
            for line in lines[::-1]:
                ans_match = re.search(r"(?:Ans(?:wer)?|Answer)\s*:?[\s\(]*([1-4A-D])[\)]?", line, re.IGNORECASE)
                if ans_match:
                    answer = ans_match.group(1)
                    break

            if not (question_text and options):
                self._log("Skipping block: missing question text or options")
                return None

            result = {
                "question_id": self._generate_question_id(block),
                "text": question_text,
                "options": options,
                "correct_answer": answer,
                "subject": self.current_section or "Unknown",
            }
            return result
        except Exception as e:
            self._log(f"Error parsing block: {e}")
            return None

    def process_text_content(self, text: str) -> List[Dict]:
        """Process text content and extract questions.

        Returns:
            List[Dict]: List of parsed questions, each containing:
                - question_id: Unique identifier
                - text: Question text
                - options: List of answer options
                - correct_answer: The correct answer
                - subject: Question subject/section
        """
        self.current_section = None
        blocks = self._split_into_question_blocks(text)
        results: List[Dict] = []
        for block in blocks:
            parsed = self._parse_question_block(block)
            if parsed:
                results.append(parsed)

        self._log(f"Processed {len(results)} questions")
        return results


def create_question_processor() -> QuestionProcessor:
    """Compatibility helper used by other modules to create a processor instance."""
    return QuestionProcessor()
