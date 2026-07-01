# Hands-On 02: Django Models, ORM & Admin Interface

This folder contains the database models and customization of Django's built-in administration panel.

## Tasks Covered
1. **Schema Design**: Defined SQLAlchemy-like Django models inside `courses/models.py` representing `Department`, `Course`, `Student`, and `Enrollment` with relationships and validation metadata.
2. **Integrity Rule**: Configured a composite unique index (`unique_together`) on the `Enrollment` model to prevent duplicate entries for the same student-course pair.
3. **Django Admin Panel customization**: Customized `CourseAdmin` inside `courses/admin.py` to enable table sorting column views, search functionality, and side filters.

## How to Run
1. Navigate to the `coursemanager` directory:
   ```bash
   cd coursemanager
   ```
2. Activate the virtual environment:
   ```bash
   .\venv\Scripts\activate
   ```
3. Run migrations to initialize database:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
4. Create a superuser to access the admin site:
   ```bash
   python manage.py createsuperuser
   ```
5. Start server (`python manage.py runserver`) and navigate to `http://127.0.0.1:8000/admin/`.
