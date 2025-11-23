# Project Structure Guide

## 🎯 Overview

Your project is now organized with a **proper MVC-like architecture** following Flask best practices:

```
app/
├── models/          (Database layer)
├── templates/       (View layer - HTML)
├── routes/          (Ready for Controller layer)
└── static/          (CSS, JS assets)
```

## 📁 Directory Structure

### `app/models/database.py` - Database Models
All database models in ONE organized file:
- `Department` - Departments/courses
- `Admin` - Administrators
- `Faculty` - Faculty members
- `Subject` - Subjects/courses
- `SectionTimetable` - Generated section timetables
- `SubjectConstraint` - Scheduling constraints
- `FacultyTimetable` - Generated faculty timetables

**Import anywhere:**
```python
from app.models.database import Faculty, Subject, db
from app.models import Department, Admin  # Also works
```

### `app/templates/` - HTML Templates
All HTML files are here:
- `index.html` - Homepage
- `admin_login.html`, `admin_dashboard.html` - Admin pages
- `faculty_login.html`, `faculty_dashboard.html` - Faculty pages
- `add_departments.html`, `add_faculty.html`, `add_subjects.html` - Management pages
- `view_timetables.html`, `set_constraints.html` - Timetable pages

### `app/static/js/` - JavaScript Files
- `auth.js` - Authentication JS
- Other JS files can be added here

### `app/static/css/` - (Create later)
Add CSS files here:
```
app/static/css/
├── style.css
├── admin.css
└── faculty.css
```

### `app/routes/` - API Routes (Future)
Structure ready for blueprints:
```
app/routes/
├── auth.py       (Login, register, logout)
├── admin.py      (Department, faculty, subject management)
├── timetable.py  (Timetable generation, viewing)
└── faculty.py    (Faculty views, my timetable)
```

## 🚀 Running the Project

```bash
# Same as before - no changes needed!
python server.py
```

OR use the new entry point when blueprints are added:
```bash
python run.py
```

## 💻 Coding Examples

### Importing Models
```python
# Import specific models
from app.models.database import Faculty, Department, db

# OR import from package
from app.models import Faculty, Department

# Using models
faculty = Faculty.query.filter_by(faculty_id='F001').first()
```

### Database Operations
```python
from app.models.database import db, Subject

# Add new subject
new_subject = Subject(
    subject_name='Python',
    subject_code='CS101',
    dept_name='CSE',
    college_id='C123',
    faculty_name='Dr. John',
    section='A',
    hours=3
)
db.session.add(new_subject)
db.session.commit()
```

### Flask Routes (Current - in server.py)
```python
from app.models import Faculty, Department

@app.route('/admin/dashboard')
def admin_dashboard():
    faculties = Faculty.query.all()
    return render_template('admin_dashboard.html', faculties=faculties)
```

### Flask Routes (Future - in blueprints)
```python
# app/routes/admin.py
from flask import Blueprint, render_template
from app.models import Faculty

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
def dashboard():
    faculties = Faculty.query.all()
    return render_template('admin_dashboard.html', faculties=faculties)
```

## 🔄 Migration Plan

### Phase 1 ✅ (DONE)
- [x] Extract models to `app/models/database.py`
- [x] Move templates to `app/templates/`
- [x] Move static files to `app/static/`
- [x] Update imports in `server.py`

### Phase 2 (NEXT)
- [ ] Create blueprints for routes
- [ ] Split routes by function:
  - `app/routes/auth.py` - Login endpoints
  - `app/routes/admin.py` - Admin management
  - `app/routes/timetable.py` - Timetable endpoints
  - `app/routes/faculty.py` - Faculty endpoints

### Phase 3 (OPTIONAL)
- [ ] Add `app/services/` for business logic
- [ ] Add `tests/` for unit tests
- [ ] Create `config.py` for environment configs

## 📝 File Changes

### OLD (Messy)
```
/
├── server.py (1838 lines!)
├── algorithm.py
├── index.html
├── admin_login.html
├── auth.js
└── ...
```

### NEW (Organized)
```
/
├── server.py (imports from app/)
├── app/
│   ├── models/database.py
│   ├── templates/*.html
│   └── static/js/*.js
└── ...
```

## ✅ Checklist for Future Work

- [ ] Test all endpoints after import changes
- [ ] Create route blueprints
- [ ] Add CSS organization
- [ ] Set up logging configuration
- [ ] Add environment-specific configs
- [ ] Create test suite

## 🎓 Key Benefits

1. **Maintainability** - Easy to find and update code
2. **Scalability** - Structure supports growth
3. **Collaboration** - Clear organization for teams
4. **Best Practices** - Follows Flask conventions
5. **Backward Compatible** - All existing code still works!

## 📚 Resources

- Flask Documentation: https://flask.palletsprojects.com/
- SQLAlchemy ORM: https://www.sqlalchemy.org/
- Project Structure: https://www.digitalocean.com/community/tutorials/how-to-structure-large-flask-applications

---

**Questions?** Check `PROJECT_STRUCTURE.md` for detailed documentation!
