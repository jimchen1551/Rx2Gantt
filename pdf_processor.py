import re
import fitz
import pandas as pd
from collections import defaultdict
from config import PDF_COLUMNS, COLUMN_BOUNDARIES

class PDFProcessor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path

    def contains_chinese(self, text):
        """Checks if the given text contains Chinese characters."""
        chinese_pattern = re.compile(r"[\u4e00-\u9fff]")
        return bool(chinese_pattern.search(text))

    def assign_to_column(self, x, text):
        """Assigns text to a column based on x-coordinate."""
        for i, (start, end) in enumerate(COLUMN_BOUNDARIES):
            if start <= x < end:
                return i
        return None

    def split_merged_elements(self, text, bbox):
        """Splits merged text elements into separate pieces."""
        pattern = r"([A-Za-z0-9]+)\s*([0-9]{4}-)"
        match = re.match(pattern, text)
        if match:
            part1, part2 = match.groups()
            x0, y0, x1, y1 = bbox
            return [
                (part1, (x0, y0, 392, y1)),
                (part2, (393, y0, x1, y1))
            ]
        return [(text, bbox)]

    def extract_data(self):
        """Extracts structured data from the PDF."""
        doc = fitz.open(self.pdf_path)
        data = []

        for page_number in range(len(doc)):
            page = doc[page_number]
            spans = []

            # Extract text and bounding boxes
            for block in page.get_text("dict")["blocks"]:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        bbox = span.get("bbox", [])
                        if text and not self.contains_chinese(text):
                            spans.extend(self.split_merged_elements(text, bbox))

            # Assign spans to rows and columns
            rows = defaultdict(lambda: [None] * len(PDF_COLUMNS))
            for text, bbox in spans:
                x0, y0, _, _ = bbox
                row_key = round(y0)
                col_index = self.assign_to_column(x0, text)
                if col_index is not None:
                    if rows[row_key][col_index]:
                        rows[row_key][col_index] += " " + text
                    else:
                        rows[row_key][col_index] = text

            # Collect rows without Chinese characters
            for row in sorted(rows.keys()):
                if not any(self.contains_chinese(cell) for cell in rows[row] if cell):
                    data.append(rows[row])

        # Create a DataFrame from the extracted data
        return pd.DataFrame(data, columns=PDF_COLUMNS)
