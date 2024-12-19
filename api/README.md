# Demo OCR (api)

## Description
A simple Flask-based API that provides a OCR api for TLAB Technical Challenge.

---

## Requirements
Ensure you have the following installed:
- Python 3.8+
- pip (Python package manager)
- virtualenv (recommended for creating isolated Python environments)

---

## Running the API
1. Start the Flask development server:
    ```bash
    flask run
    ```

2. The API will be accessible at `http://127.0.0.1:5000/` by default.

---

## API Endpoints
| Method | Endpoint       | Description                      |
|--------|----------------|----------------------------------|
| GET    | /upload        | Upload a file.                   |
| POST   | /extract       | Extract info by OCR engine.      |

---

## License
This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgements
- [Flask documentation](https://flask.palletsprojects.com/)

---

## Contact
For questions or feedback, reach out at [your email] or create an issue in this repository.