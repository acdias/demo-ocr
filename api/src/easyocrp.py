from file import File
import re
import easyocr
import io
import csv

class EasyOCR:

    def __init__(self, gpu = False):
        """
        Initializes the EasyOCR Reader.

        Args:
            gpu (bool): Flag to indicate whether to use GPU for OCR processing. Defaults to False.

        Attributes:
            reader (easyocr.Reader): An instance of the EasyOCR Reader initialized with English language.
            file (File): An instance of the File class.
        """
        # Initialize EasyOCR Reader
        self.reader = easyocr.Reader(['en'], gpu)
        self.file = File()
    
    def extract(self, storename):
        """
        Extracts text from a PDF file, processes it, and returns the result as a CSV string.

        Args:
            storename (str): The name of the PDF file to be processed.

        Returns:
            str: A CSV string containing the extracted and processed text data.
            dict: An error message if an exception occurs during processing.

        Raises:
            Exception: If any error occurs during the extraction or processing of the PDF file.
        """
        document = ''
        csv_data = list()
        fname = '.'.join(storename.split('.')[:-1])
        png = self.file.pdf_to_png(f"./uploads/{storename}")
        try:
            for page in png['pages']:

                # Step 1: Extract text with bounding boxes
                extracted_data = self.extract_text_with_bounding_boxes(page['path'])
                # Step 2: Group text into rows based on Y-coordinates
                grouped_rows = self.group_text_by_rows(extracted_data)
                # Step 3: Write formatted data to CSV
                csv_string = self.write_rows_to_csv_string(grouped_rows)
                csv_file = io.StringIO(csv_string)
                csv_reader = csv.reader(csv_file)
                csv_data = csv_data + list(csv_reader)

            # Create a new CSV string from the combined data
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerows(csv_data)
            # Get the concatenated CSV string
            document = output.getvalue()
            # Clean the PNG files
            self.file.clean_pngs(png)
            return document
        except Exception as e:
            self.file.clean_pngs(png)
            return {
                "error": "Something else went wrong with EasyOCR"
            }
    
    def extract_text_with_bounding_boxes(self, image_path):
        """
        Extract text with bounding box coordinates from an image using EasyOCR.

        :param image_path: Path to the image file
        :return: List of tuples [(bbox, text), ...]
        """
        results = self.reader.readtext(image_path)  # Extract text with bounding boxes
        return results

    def group_text_by_rows(self, text_with_boxes, y_tolerance=10):
        """
        Group text by rows based on Y-axis positions.

        :param text_with_boxes: List of tuples [(bbox, text, confidence), ...]
        :param y_tolerance: Vertical tolerance to group words into the same row
        :return: List of grouped rows [[(x, text), ...], ...]
        """
        rows = []

        for bbox, text, _ in text_with_boxes:  # Ignore confidence value
            # Extract the average Y-coordinate (vertical center of the bounding box)
            y_center = (bbox[0][1] + bbox[2][1]) / 2  # Average Y-coordinate
            x_start = bbox[0][0]  # X-coordinate for sorting

            placed = False
            for row in rows:
                # Compare Y-coordinate with existing rows
                if abs(row['y'] - y_center) <= y_tolerance:
                    row['words'].append((x_start, text))
                    placed = True
                    break

            if not placed:
                # Start a new row if no row is found within the tolerance
                rows.append({'y': y_center, 'words': [(x_start, text)]})

        # Sort words in each row by X-coordinate
        for row in rows:
            row['words'].sort(key=lambda word: word[0])

        # Extract only the words for each row
        grouped_rows = [row['words'] for row in rows]

        return grouped_rows

    def write_rows_to_csv_string(self, rows):
        """
        Write grouped rows of text to a CSV string, preserving section headers, table layout,
        and adding spaces between sections.

        :param rows: List of grouped rows [[(x, text), ...], ...]
        :return: CSV string
        """
        def is_section_header(text):
            """Check if a line is a section header (e.g., starts with '1.' or is all uppercase)."""
            return re.match(r"^\d+\.\s+.*", text) or text.isupper()

        # Create an in-memory string buffer
        output = io.StringIO()
        writer = csv.writer(output)
        # writer.writerow(["Label", "Value"])  # Write header row (commented out if not needed)

        previous_label = ""  # To hold incomplete labels
        first_section = True  # To manage space after sections

        for row in rows:
            # Combine all words in the row into a single line of text
            combined_text = " ".join(word[1] for word in row).strip()  # Changed to row instead of row['words']

            # Handle section headers
            if is_section_header(combined_text):
                if not first_section:
                    writer.writerow(["", ""])  # Add an empty row for spacing between sections
                first_section = False

                writer.writerow([combined_text, ""])  # Write section header with empty value
                previous_label = ""  # Reset incomplete label
                continue

            # Handle label-value pairs
            if ":" in combined_text:
                label, value = combined_text.split(":", 1)
                label, value = label.strip(), value.strip()

                # Write the previous label with its value if it exists
                if previous_label:
                    writer.writerow([previous_label, ""])
                    previous_label = ""

                writer.writerow([label, value])  # Write current label and value
            elif previous_label:  # Append multi-line value to the previous label
                writer.writerow([previous_label, combined_text])
                previous_label = ""  # Reset
            else:
                # Store this line as a potential label for the next iteration
                previous_label = combined_text

        # Handle any leftover label
        if previous_label:
            writer.writerow([previous_label, ""])

        # Get the CSV string from the buffer
        csv_string = output.getvalue()

        # Close the buffer
        output.close()

        return csv_string
