# Hands-On 03: Django REST Views, URL Routing & Forms

This folder contains the RESTful API implementation for the Course Management system built using the Django REST Framework (DRF).

## Tasks Covered
1. **DRF Serializers**: Created ModelSerializers in `courses/serializers.py` to map Django database models directly to JSON representation structures.
2. **DRF ViewSets & Routers**:
   - Replaced basic view handlers with `ModelViewSet` classes for `Department`, `Course`, `Student`, and `Enrollment` models.
   - Configured `DefaultRouter` in `courses/urls.py` to automatically register all standard CRUD routes.
3. **Custom Action**: Implemented a custom action `@action` in `CourseViewSet` mapping to `GET /api/courses/{id}/students/` to list all students enrolled in a specific course using an database query join filter.

## How to Run
1. Navigate to the `coursemanager` directory:
   ```bash
   cd coursemanager
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
   python manage.py runserver
   ```
5. Test endpoints like `http://127.0.0.1:8000/api/courses/` or custom action `http://127.0.0.1:8000/api/courses/1/students/`.
