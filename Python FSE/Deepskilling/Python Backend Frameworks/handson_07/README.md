# Hands-On 07: FastAPI — Dependency Injection, CRUD & OpenAPI Documentation

This folder contains the database-connected, full-CRUD Course Management REST API built in FastAPI.

## Tasks Covered
1. **Full CRUD Operations**: Implemented RESTful database CRUD operations for `Department`, `Course`, `Student`, and `Enrollment` models.
2. **Background Tasks**: Implemented FastAPI `BackgroundTasks` to send simulated enrollment email confirmations after the response is dispatched.
3. **OpenAPI Customization**: Custom registered metadata description in `FastAPI()` config and structured Swagger route group tagging.

## How to Run
1. Navigate to the `fastapi_coursemanager` directory:
   ```bash
   cd fastapi_coursemanager
   ```
2. Activate the virtual environment:
   ```bash
   .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the server:
   ```bash
   uvicorn main:app --reload
   ```
5. Open `http://127.0.0.1:8000/docs` to test endpoints and read OpenAPI specifications.
