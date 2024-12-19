from textractcaller.t_call import call_textract, Textract_Features
from textractprettyprinter.t_pretty_print import Pretty_Print_Table_Format, Textract_Pretty_Print, get_string
from file import File
import boto3
import json
import csv
import io
import os

class Textract:
    
    def __init__(self, region_name='eu-west-1'):
        """
        Initializes the Textract client with the specified AWS region and credentials.

        Args:
            region_name (str): The AWS region name to use for the Textract client. Defaults to 'eu-west-1'.

        Attributes:
            client (boto3.client): The Textract client initialized with the specified region and credentials.
            file (File): An instance of the File class.
        """
        self.client = boto3.client(
            'textract',
            region_name=os.environ.get('AWS_DEFAULT_REGION', region_name),
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        )
        self.file = File()
    
    def extract(self, storename):
        """
        Extracts text and table data from a PDF file using Amazon Textract and converts it to a CSV format.
        Args:
            storename (str): The name of the PDF file to be processed.
        Returns:
            str: A CSV string containing the extracted data if successful.
            dict: A dictionary with an error message if an exception occurs.
        Raises:
            Exception: If an error occurs during the Textract processing or file handling.
        """
        document = ''
        csv_data = list()
        fname = '.'.join(storename.split('.')[:-1])
        png = self.file.pdf_to_png(f"./uploads/{storename}")
        try:
            for page in png['pages']:
                with open(page['path'], 'rb') as input_document:
                    # Calling Textract to analyze the form content
                    
                    textract_json = call_textract(
                        features=[Textract_Features.LAYOUT, Textract_Features.FORMS, Textract_Features.TABLES],
                        boto3_textract_client=self.client,
                        input_document=input_document.read(),
                    )
                    with open(f"./uploads/{fname}.json", 'w') as out:
                        out.write(json.dumps(textract_json, indent=4))
                
                    '''
                    # Use mock from textract
                    #with open(f"./uploads/{fname}.json", 'rb') as file:
                    with open(f"./uploads/textract.json", 'rb') as file:
                        textract_json = json.loads(file.read())
                    '''
                    
                    # Get the CSV data from the Textract JSON
                    csv_string = get_string(
                        output_type=[Textract_Pretty_Print.TABLES],
                        table_format=Pretty_Print_Table_Format.csv,
                        textract_json=textract_json
                    )
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
                "error": "Something else went wrong with Textract"
            }
