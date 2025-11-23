# Project Structure Documentation

## New File Organization

The project has been restructured into a proper Flask application with the following directory layout:

```
Timetable/
├── app/                          # Main application package
│   ├── __init__.py              # App initialization
│   ├── models/                  # Database models
│   │   ├── __init__.py
│   │   └── database.py          # All database model definitions
│   ├── routes/                  # API routes (for future modularization)
│   │   └── __init__.py
│   ├── templates/               # HTML templates
│   │   ├── index.html
│   │   ├── admin_login.html
│   │   ├── admin_dashboard.html
│   │   ├── faculty_login.html
│   │   ├── faculty_dashboard.html
│   │   ├── authority_login.html
│   │   ├── authority_dashboard.html
│   │   ├── add_departments.html
│   │   ├── add_faculty.html
│   │   ├── add_subjects.html
│   │   ├── view_timetables.html
│   │   └── set_constraints.html
│   └── static/                  # Static files
│       └── js/
│           └── auth.js
│
├── server.py                    # Main Flask application server
├── run.py                       # Alternative entry point
├── algorithm.py                 # Timetable generation algorithm
├── init_db.py                   # Database initialization script
├── reset_db.py                  # Database reset script
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
└── README.md
```

## Key Changes

### 1. **Models** (`app/models/database.py`)
   - All database models are now organized in a single file:
     - `Department`
     - `Admin`
     - `SectionTimetable`
     - `Subject`
     - `SubjectConstraint`
     - `Faculty`
     - `FacultyTimetable`
   - Easier to manage, understand, and maintain

### 2. **Templates** (`app/templates/`)
   - All HTML files moved to centralized templates folder
   - Flask can serve them efficiently
   - Cleaner root directory

### 3. **Static Files** (`app/static/`)
   - JavaScript files moved to `app/static/js/`
   - CSS can be added to `app/static/css/` later
   - Professional organization

### 4. **Routes** (`app/routes/`)
   - Structure ready for route blueprints
   - Can split routes by function (auth, admin, faculty, timetable)
   - Currently, routes are still in `server.py` for backward compatibility

## How to Run

### Option 1 (Current - Keep using):
```bash
python server.py
```

### Option 2 (Future - With blueprints):
```bash
python run.py
```

## Database Models Location

**Before:**
```python
# server.py (1838 lines - too long!)
class Department(db.Model):
    ...
class Admin(db.Model):
    ...
```

**After:**
```python
# app/models/database.py (cleaner, organized)
from app.models.database import Department, Admin, ...
```

## Accessing Models in Code

```python
# Old way
from server import Department, Admin, Subject

# New way (can be used anywhere now)
from app.models.database import Department, Admin, Subject
# or
from app.models import Department, Admin, Subject
```

## Future Improvements

1. **Split Routes into Blueprints:**
   ```
   app/routes/
   ├── auth.py (login, register)
   ├── admin.py (department, faculty, subject management)
   ├── timetable.py (timetable generation)
   └── faculty.py (faculty views)
   ```

2. **Add Services/Helpers:**
   ```
   app/services/
   ├── timetable_service.py
   └── notification_service.py
   ```

3. **Configuration Management:**
   ```
   config.py (development, testing, production configs)
   ```

4. **Testing Structure:**
   ```
   tests/
   ├── test_models.py
   ├── test_routes.py
   └── fixtures.py
   ```

## Import Examples

### Models
```python
from app.models import Department, Faculty, Subject
from app.models.database import db
```

### Database Instance
```python
from app.models.database import db
db.session.add(new_record)
db.session.commit()
```

## Notes

- The restructuring maintains **100% backward compatibility** with existing code
- All routes in `server.py` work exactly as before
- Templates are now properly organized following Flask conventions
- Static files are in the right location for Flask to serve them efficiently
- The `db` instance is importable from `app.models.database`

## Summary

✅ **Models** → `app/models/database.py`
✅ **Templates** → `app/templates/`
✅ **Static JS/CSS** → `app/static/`
✅ **Routes** → Ready for splitting into blueprints in `app/routes/`
✅ **Server** → `server.py` (still works, imports from new structure)
✅ **Database** → Imported from modular location

This structure is production-ready and follows Flask best practices!
