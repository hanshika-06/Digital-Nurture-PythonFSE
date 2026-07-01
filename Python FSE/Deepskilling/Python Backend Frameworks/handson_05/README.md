# Hands-On 05: Flask with SQLAlchemy ORM & Database Integration

This folder contains the database-connected version of the Flask Course Management API.

## Tasks Covered
1. **Flask-SQLAlchemy Setup**: Initialized and bound a SQLite database configuration in `app.py`.
2. **Schema Models**: Configured Flask-SQLAlchemy models matching the database schema (`Department`, `Course`, `Student`, `Enrollment`) in `courses/models.py`.
3. **Database Migrations**: Connected `Flask-Migrate` in `extensions.py`/`app.py` to handle structural schema edits.
4. **ORM Routing**: Updated Flask routing endpoints inside `courses/routes.py` to query and perform SQL operations via the ORM.

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
4. Initialize and apply database migrations:
   ```bash
   flask db init
   flask db migrate -m "initial schema"
   flask db upgrade
   ```
5. Start server (`python app.py`) and interact with database-connected endpoints.
