# pdf_text_extractor.py

import fitz  # PyMuPDF
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file using PyMuPDF.

    Args:
        file_path (str): Absolute or relative path to the PDF file.

    Returns:
        str: The extracted full text concatenated from all pages.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        ValueError: If the file is not a valid PDF or cannot be opened.
        Exception: For other unexpected errors.
    """
    if not os.path.isfile(file_path):
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    try:
        with fitz.open(file_path) as doc:
            if doc.page_count == 0:
                logger.warning(f"No pages found in PDF: {file_path}")
                return ""

            full_text = []
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text:
                    full_text.append(text)
                else:
                    logger.debug(f"No text extracted from page {page_num} in {file_path}")

            result = "\n".join(full_text).strip()

            if not result:
                logger.warning(f"No text extracted from PDF file: {file_path}")

            logger.info(f"Extracted {len(result)} characters from {file_path} ({doc.page_count} pages)")
            return result

    except RuntimeError as re:
        # PyMuPDF throws RuntimeError on invalid PDF
        logger.error(f"Invalid PDF file {file_path}: {re}")
        raise ValueError(f"Invalid PDF file: {file_path}") from re

    except Exception as e:
        logger.exception(f"Unexpected error extracting PDF text from {file_path}: {e}")
        raise
