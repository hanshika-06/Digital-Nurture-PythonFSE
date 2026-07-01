# Hands-On 04: Flask — App Structure, Routing, Jinja2 & Blueprints

This folder contains the Course Management API rebuilt from scratch in Flask, highlighting differences in framework architectures.

## Tasks Covered
1. **Application Factory Pattern**: Structured the application using `create_app()` in `app.py` loading configurations from a `Config` class.
2. **Blueprints for Routing**: Decoupled routes using a `courses_bp` Flask Blueprint inside `courses/routes.py` with `/api/courses/` prefix.
3. **Structured Responses**: Implemented `make_response_json(data, status_code)` to envelop success payloads consistently under `{"status": "success", "data": data}`.
4. **JSON Error Handlers**: Custom registered global handlers for `404` and `500` error status codes returning JSON objects.

## How to Run
1. Navigate to the `flask_coursemanager` directory:
   ```bash
   cd flask_coursemanager
   ```
2. Activate the virtual environment:
   ```bash
   .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the application:
   ```bash
   python app.py
   ```
5. Navigate to `http://127.0.0.1:5000/api/courses/` in your browser.
