from flask import Flask, request, make_response
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
from textract import Textract
from easyocrp import EasyOCR

import uuid
import time
import re

app = Flask(__name__)
cors = CORS(app) # allow CORS for all domains on all routes.
app.config['CORS_HEADERS'] = 'Content-Type'
textract = Textract()
easyocrp = EasyOCR()

@app.route('/')
def index():
    return "Health check!"

print(__name__)

@app.route('/upload', methods=['POST'])
@cross_origin()
def upload():
    for fname in request.files:
        uploaded_file = request.files.get(fname)
        if uploaded_file.filename != '':
            clean = re.sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", fname) # Clean the filename
            aname = secure_filename(clean).split('.') # Get the filename and extension sanitized
            uname = f"{aname[0]}_{int(time.time())}_{uuid.uuid4().hex}.{aname[1]}" # Create a unique filename
            uploaded_file.save('./uploads/%s' % uname)
            return uname

@app.route('/extract', methods=['POST'])
@cross_origin()
def extract():
    data = request.get_json()
    response = ''
    
    if data['filename'] and data['engine']:
        # Match the engine to predefined patterns
        match data['engine']:
            case "textract":
                response = textract.extract(data['storename'])
            case "easyocr":
                response = easyocrp.extract(data['storename'])
            case _:
                response = {
                    "error": "That's not a valid engine."
                }
    
    return response if type(response) == str else make_response(response)

if __name__ == '__main__':
    app.run(debug=True)
