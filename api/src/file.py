from pdf2image import convert_from_path
import os

class File:
    """
    A class used to represent a File and perform operations on it.

    Methods
    -------
    pdf_to_png(storename)
        Converts a PDF file to PNG images, one for each page, and returns a dictionary with the storename and paths to the images.

    clean_pngs(document)
        Deletes the PNG images generated from a PDF file based on the paths provided in the document dictionary.
    """

    def pdf_to_png(self, storename):
        file = {'storename': storename, 'pages': []}
        fname = '.'.join(storename.split('.')[:-1])
        pages = convert_from_path(storename, 500)
        for page, obj in enumerate(pages):
            pfname = ''.join([fname, '_', str(page), '.png'])
            obj.save(pfname, 'PNG')
            file['pages'].append({'page': page, 'path': pfname})
        return file

    def clean_pngs(self, document):
        for page in document['pages']:
            if os.path.exists(page['path']):
                os.remove(page['path'])

