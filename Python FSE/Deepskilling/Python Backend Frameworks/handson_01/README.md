# Hands-On 01: Web Framework Foundations & Django Project Setup

This folder contains the setup and files for Hands-On 01, introducing fundamental web framework concepts and scaffolding the base Django application.

## Tasks Covered
1. **Request-Response Cycle Exploration**: Detailed notes on the journey of an HTTP GET request, WSGI vs ASGI, MVC vs MVT, and Django middlewares are documented in `coursemanager/notes.py`.
2. **Project Scaffolding**: Setup of the main `coursemanager` Django project and creation of the `courses` app.
3. **Hello View Routing**: Wired a modular URL path mapping `/api/hello/` to a view returning `"Course Management API is running"`.

## How to Run
1. Navigate to the `coursemanager` directory:
   ```bash
   cd coursemanager
   ```
2. Activate the virtual environment:
   ```bash
   .\venv\Scripts\activate
   ```
3. Start the server:
   ```bash
   python manage.py runserver
   ```
4. Visit `http://127.0.0.1:8000/api/hello/` to test the endpoint.
