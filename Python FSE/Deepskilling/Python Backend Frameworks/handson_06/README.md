# Hands-On 06: FastAPI — Path Parameters, Pydantic & Async Endpoints

This folder contains the Course Management API built in FastAPI, demonstrating async routing and input validation using Pydantic.

## Tasks Covered
1. **Pydantic Validation**: Defined BaseModel schemas in `schemas.py` (`CourseCreate`, `CourseUpdate`, `CourseResponse`) to auto-validate requests and serialize responses.
2. **Database Integration**: Wired an async SQLite connection (`sqlite+aiosqlite`) using SQLAlchemy.
3. **Async DB Queries**: Implemented full CRUD endpoints inside `main.py` utilizing async event loops and `await db.execute()` mappings.
4. **Interactive Docs**: Integrated OpenAPI documentation automatically visible at `/docs`.

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
4. Start the FastAPI application:
   ```bash
   uvicorn main:app --reload
   ```
5. Visit `http://127.0.0.1:8000/docs` to test endpoints via Swagger UI.
