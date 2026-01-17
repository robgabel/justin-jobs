from typing import Dict, Any
import io
from pypdf import PdfReader


class ResumeParser:
    """Parse resume files and extract text content."""

    @staticmethod
    def parse_pdf(file_content: bytes) -> str:
        """Extract text from PDF resume."""
        try:
            pdf_file = io.BytesIO(file_content)
            reader = PdfReader(pdf_file)

            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"

            return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")

    @staticmethod
    def parse_text(file_content: bytes) -> str:
        """Extract text from plain text resume."""
        try:
            return file_content.decode("utf-8").strip()
        except Exception as e:
            raise ValueError(f"Failed to parse text file: {str(e)}")

    @staticmethod
    def extract_resume_info(resume_text: str) -> Dict[str, Any]:
        """
        Extract structured information from resume text.
        This is a simple implementation - can be enhanced with Claude API.
        """
        lines = resume_text.split("\n")

        info = {
            "raw_text": resume_text,
            "sections": {},
            "skills": [],
            "education": [],
            "experience": [],
        }

        current_section = None
        section_content = []

        common_sections = [
            "experience",
            "education",
            "skills",
            "projects",
            "summary",
            "objective",
        ]

        for line in lines:
            line_lower = line.lower().strip()

            # Check if line is a section header
            is_section = False
            for section in common_sections:
                if section in line_lower and len(line_lower) < 30:
                    if current_section and section_content:
                        info["sections"][current_section] = "\n".join(section_content)

                    current_section = section
                    section_content = []
                    is_section = True
                    break

            if not is_section and current_section:
                section_content.append(line)

        # Add last section
        if current_section and section_content:
            info["sections"][current_section] = "\n".join(section_content)

        return info
