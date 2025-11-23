#server.py
import os
import logging
from flask import Flask, jsonify, request, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
try:
    from flask_cors import CORS
except ImportError:
    # Provide a clear error so the developer knows to activate the venv or install the package
    logging.error(
        "Missing dependency: flask-cors.\n"
        "Make sure the project's virtual environment is activated and install the package:\n"
        "  /c/Users/91988/Hack_io/.venv/Scripts/python.exe -m pip install flask-cors\n"
        "or activate the venv and run:\n"
        "  source /c/Users/91988/Hack_io/.venv/Scripts/activate && pip install flask-cors"
    )
    raise
from sqlalchemy.dialects.postgresql import JSONB
from datetime import timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# Import timetable generation function and faculty mapping from algorithm
try:
    from algorithm import store_section_timetables, faculties as algorithm_faculties, get_faculty_for_subject
except Exception as e:
    logging.exception("Failed to import from algorithm")
    raise ImportError("could not import required functions from algorithm") from e

# Simple .env loader (handles spaces)
def load_local_env(path):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

# Load environment variables
load_local_env(os.path.join(os.path.dirname(__file__), ".env"))

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set in .env")

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Configure SQLAlchemy and Session
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')  # Change in production
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # Session timeout

db = SQLAlchemy(app)

# Models
class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sections = db.Column(JSONB, nullable=False)  # Store sections as JSON array
    college_id = db.Column(db.String(50), db.ForeignKey('admin.college_id'), nullable=False)
    
    # Add unique constraint for name within the same college AND make it a proper composite key
    __table_args__ = (
        db.UniqueConstraint('name', 'college_id', name='unique_department_per_college'),
        db.Index('idx_dept_name_college', 'name', 'college_id', unique=True)
    )

class Admin(db.Model):
    __tablename__ = 'admin'
    college_id = db.Column(db.String(50), primary_key=True)
    admin_name = db.Column(db.String(100), nullable=False)
    college_name = db.Column(db.String(200), nullable=False)
    admin_password = db.Column(db.String(100), nullable=False)

class SectionTimetable(db.Model):
    __tablename__ = 'section_timetables'
    id = db.Column(db.Integer, primary_key=True)
    section_name = db.Column(db.String(10), nullable=False)
    dept_name = db.Column(db.String(100), nullable=False)
    college_id = db.Column(db.String(50), nullable=False)
    timetable = db.Column(JSONB, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    
    __table_args__ = (
        db.ForeignKeyConstraint(
            ['dept_name', 'college_id'],
            ['departments.name', 'departments.college_id'],
            name='fk_timetable_department',
            onupdate='CASCADE',
            ondelete='CASCADE'
        ),
        # Add unique constraint for section within a department
        db.UniqueConstraint('section_name', 'dept_name', 'college_id', name='unique_section_dept'),
        # Add index for faster lookups
        db.Index('idx_timetable_lookup', 'dept_name', 'college_id', 'created_at')
    )

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(100), nullable=False)
    subject_code = db.Column(db.String(20), nullable=False)
    dept_name = db.Column(db.String(100), nullable=False)
    college_id = db.Column(db.String(50), nullable=False)
    faculty_name = db.Column(db.String(100), nullable=False)  # Faculty assigned to this subject
    section = db.Column(db.String(10), nullable=False)
    hours = db.Column(db.Integer, nullable=False)
    lab = db.Column(db.Boolean, nullable=False, default=False)
    last = db.Column(db.Boolean, nullable=False, default=False)

    __table_args__ = (
        db.UniqueConstraint('subject_code', 'college_id', name='unique_subject_per_college'),
        db.ForeignKeyConstraint(
            ['dept_name', 'college_id'],
            ['departments.name', 'departments.college_id'],
            name='fk_subject_department',
            onupdate='CASCADE',
            ondelete='RESTRICT'
        ),
        db.ForeignKeyConstraint(
            ['college_id'],
            ['admin.college_id'],
            name='fk_subject_college',
            onupdate='CASCADE',
            ondelete='RESTRICT'
        )
    )

    def to_dict(self):
        return {
            'id': self.id,
            'subject_name': self.subject_name,
            'subject_code': self.subject_code,
            'dept_name': self.dept_name,
            'college_id': self.college_id,
            'faculty_name': self.faculty_name,
            'section': self.section,
            'hours': self.hours,
            'lab': bool(self.lab),
            'last': bool(self.last)
        }


class SubjectConstraint(db.Model):
    """Stores both strict (fixed) and forbidden placement constraints for subjects."""
    __tablename__ = 'subject_constraints'
    id = db.Column(db.Integer, primary_key=True)
    college_id = db.Column(db.String(50), nullable=False)
    dept_name = db.Column(db.String(100), nullable=False)
    section = db.Column(db.String(10), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    day = db.Column(db.String(10), nullable=False)
    period = db.Column(db.Integer, nullable=False)
    constraint_type = db.Column(db.String(20), nullable=False)  # 'strict' | 'forbidden'
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    __table_args__ = (
        db.UniqueConstraint('dept_name', 'section', 'subject', 'day', 'period', 'constraint_type', 'college_id', name='unique_subject_constraint'),
        db.Index('idx_constraint_lookup', 'dept_name', 'section', 'constraint_type'),
        db.ForeignKeyConstraint(
            ['dept_name', 'college_id'],
            ['departments.name', 'departments.college_id'],
            name='fk_constraint_department',
            onupdate='CASCADE',
            ondelete='CASCADE'
        )
    )

    def to_dict(self):
        return {
            'id': self.id,
            'college_id': self.college_id,
            'dept_name': self.dept_name,
            'section': self.section,
            'subject': self.subject,
            'day': self.day,
            'period': self.period,
            'constraint_type': self.constraint_type,
            'created_at': self.created_at.isoformat() if self.created_at is not None else None
        }

class Faculty(db.Model):
    __tablename__ = 'faculty'
    faculty_id = db.Column(db.String(50), primary_key=True)
    faculty_name = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100), nullable=False)
    dept_name = db.Column(db.String(100), nullable=False)
    faculty_password = db.Column(db.String(100), nullable=False)
    college_id = db.Column(db.String(50), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('faculty_id', 'college_id', name='unique_faculty_per_college'),
        db.ForeignKeyConstraint(
            ['dept_name', 'college_id'],
            ['departments.name', 'departments.college_id'],
            name='fk_faculty_department',
            onupdate='CASCADE',
            ondelete='RESTRICT'
        ),
        db.ForeignKeyConstraint(
            ['college_id'],
            ['admin.college_id'],
            name='fk_faculty_college',
            onupdate='CASCADE',
            ondelete='RESTRICT'
        )
    )

    def to_dict(self):
        """Convert faculty object to dictionary for JSON responses"""
        return {
            'faculty_id': self.faculty_id,
            'faculty_name': self.faculty_name,
            'designation': self.designation,
            'dept_name': self.dept_name,
            'college_id': self.college_id
        }

class FacultyTimetable(db.Model):
    """Stores generated personal faculty timetables"""
    __tablename__ = 'faculty_timetables'
    id = db.Column(db.Integer, primary_key=True)
    college_id = db.Column(db.String(50), nullable=False)
    dept_name = db.Column(db.String(100), nullable=False)
    section = db.Column(db.String(10), nullable=False)
    faculty_id = db.Column(db.String(50), nullable=False)
    faculty_name = db.Column(db.String(100), nullable=False)
    # Store timetable as JSON: {day: {period: subject, ...}, ...}
    timetable = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

    __table_args__ = (
        db.UniqueConstraint('college_id', 'dept_name', 'section', 'faculty_id', name='unique_faculty_timetable'),
        db.Index('idx_faculty_timetable_lookup', 'college_id', 'dept_name', 'faculty_id'),
        db.ForeignKeyConstraint(
            ['college_id'],
            ['admin.college_id'],
            name='fk_faculty_timetable_college',
            onupdate='CASCADE',
            ondelete='CASCADE'
        ),
        db.ForeignKeyConstraint(
            ['faculty_id', 'college_id'],
            ['faculty.faculty_id', 'faculty.college_id'],
            name='fk_faculty_timetable_faculty',
            onupdate='CASCADE',
            ondelete='CASCADE'
        )
    )

    def to_dict(self):
        return {
            'id': self.id,
            'college_id': self.college_id,
            'dept_name': self.dept_name,
            'section': self.section,
            'faculty_id': self.faculty_id,
            'faculty_name': self.faculty_name,
            'timetable': self.timetable,
            'created_at': self.created_at.isoformat() if self.created_at is not None else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at is not None else None
        }

# Create all database tables
with app.app_context():
    db.create_all()

def extract_faculty_timetables(section_timetables, faculties, subjects_per_section, dept_name, college_id):
    """Extract individual faculty timetables from section timetables.
    
    Returns a combined timetable (5 days × 9 periods) for each faculty showing all their classes.
    
    Args:
        section_timetables: {section: {day: {period: subject}}}
        faculties: {subject_name: faculty_name}
        subjects_per_section: {section: {subject_name: {hours, lab, last}}}
        dept_name: Department name
        college_id: College ID
    
    Returns:
        {faculty_name: [[...5 days...]]}  - 2D array format
    """
    faculty_timetables = {}
    
    # Iterate through each section and its timetable
    for section, section_tt in section_timetables.items():
        # Iterate through days and periods
        for day in section_tt:
            for period in section_tt[day]:
                subject = section_tt[day][period]
                
                # Skip empty slots and REMEDIAL
                if subject is None or subject == 'REMEDIAL':
                    continue
                
                # Get faculty for this subject
                faculty_name = faculties.get(subject)
                if not faculty_name:
                    continue
                
                # Initialize faculty timetable if not exists (as 5x9 2D array)
                if faculty_name not in faculty_timetables:
                    # Create 5 days × 9 periods array
                    faculty_timetables[faculty_name] = [
                        [None] * 9 for _ in range(5)
                    ]
                
                # Add this subject to the faculty's timetable
                # day is 1-5, period is 1-7, but we need to map to array indices (0-4) and (0-8)
                day_idx = day - 1
                period_idx = period - 1
                
                # Get current content
                current = faculty_timetables[faculty_name][day_idx][period_idx]
                
                # If slot is empty, add subject; if it has content, combine with section info
                if current is None:
                    faculty_timetables[faculty_name][day_idx][period_idx] = f"{subject}\n(Sec {section})"
                else:
                    # Multiple classes at same time (shouldn't happen, but handle it)
                    faculty_timetables[faculty_name][day_idx][period_idx] += f"\n{subject}\n(Sec {section})"
    
    logging.info(f"Extracted {len(faculty_timetables)} faculty timetables (combined format)")
    return faculty_timetables

def build_timetable_data_from_db(dept_name: str, college_id: str):
    """
    Fetch subject and faculty data from database and build the 3 data structures
    needed by the algorithm.
    
    Returns:
        tuple: (sections, subjects_per_section, faculties) or (None, None, None) if error
    """
    try:
        # Get department and sections
        department = Department.query.filter_by(name=dept_name, college_id=college_id).first()
        if not department:
            logging.error(f"Department not found: {dept_name}")
            return None, None, None
        
        sections = department.sections if department.sections else []
        if not sections:
            logging.error(f"Department {dept_name} has no sections defined")
            return None, None, None
        
        # Fetch all subjects for this department (using only columns that exist)
        subjects = Subject.query.filter_by(
            dept_name=dept_name,
            college_id=college_id
        ).all()
        
        if not subjects:
            logging.error(f"No subjects found for department {dept_name}")
            return None, None, None
        
        # Build subjects_per_section dictionary
        # Structure: {section: {subject_name: {hours, lab, last}, ...}, ...}
        subjects_per_section = {}
        faculties = {}
        
        for section in sections:
            subjects_per_section[section] = {}
        
        # Process each subject
        for subject in subjects:
            section = subject.section
            
            # Only include subjects for sections that exist in the department
            if section not in subjects_per_section:
                logging.warning(f"Subject {subject.subject_name} has section {section} not in department sections {sections}")
                continue
            
            subject_info = {
                'hours': subject.hours,
                'lab': bool(subject.lab),
                'last': bool(subject.last)
            }
            
            subjects_per_section[section][subject.subject_name] = subject_info
            
            # Build faculties mapping (pick first one if multiple rows)
            if subject.subject_name not in faculties:
                faculties[subject.subject_name] = subject.faculty_name
        
        # Add REMEDIAL subject for each section if not already present
        for section in sections:
            if 'REMEDIAL' not in subjects_per_section[section]:
                subjects_per_section[section]['REMEDIAL'] = {
                    'hours': 1,
                    'lab': False,
                    'last': False
                }
        
        logging.info(f"Built timetable data for {dept_name}:")
        logging.info(f"  Sections: {sections}")
        logging.info(f"  Subjects per section: {list(subjects_per_section.keys())}")
        logging.info(f"  Total subjects: {len(faculties)}")
        
        return sections, subjects_per_section, faculties
        
    except Exception as e:
        logging.exception("Error building timetable data from database")
        return None, None, None

@app.route('/generate-timetable', methods=['POST'])
def generate_timetable():
    try:
        data = request.get_json()
        dept_name = data.get('dept_name')
        college_id = data.get('college_id')
        
        if not dept_name or not college_id:
            return jsonify({'ok': False, 'error': 'Department name and college ID are required'}), 400
        
        logging.info(f"Generating timetables for {dept_name} in college {college_id}")
        
        try:
            # Fetch and build timetable data from database
            sections, subjects_per_section, faculties = build_timetable_data_from_db(dept_name, college_id)
            
            if sections is None or subjects_per_section is None or faculties is None:
                return jsonify({'ok': False, 'error': 'Failed to fetch timetable configuration from database'}), 400
            
            logging.info(f"Successfully fetched data. Sections: {sections}, Subjects: {len(subjects_per_section)}")
            
            # Suppress algorithm debug output by redirecting stderr
            import sys
            import io
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = io.StringIO()
            sys.stderr = io.StringIO()
            
            try:
                # Generate timetables using the algorithm with dynamic data
                section_timetables = store_section_timetables(
                    section_list=sections,
                    subjects_dict=subjects_per_section,
                    faculty_dict=faculties
                )
            finally:
                # Restore stdout/stderr
                sys.stdout = old_stdout
                sys.stderr = old_stderr
            
            if not section_timetables:
                logging.error(f"Algorithm returned empty timetables for {dept_name}")
                return jsonify({'ok': False, 'error': 'Timetable generation returned empty results'}), 400
            
            # Delete existing timetables for this department
            SectionTimetable.query.filter_by(dept_name=dept_name, college_id=college_id).delete()
            db.session.commit()
            
            # Store timetables for each section
            inserted_ids = []
            for section, timetable in section_timetables.items():
                new_timetable = SectionTimetable(
                    section_name=section,
                    dept_name=dept_name,
                    college_id=college_id,
                    timetable=timetable
                )
                db.session.add(new_timetable)
                db.session.flush()  # Get the ID before commit
                inserted_ids.append(new_timetable.id)
            
            db.session.commit()
            logging.info("Inserted timetables with ids=%s for sections=%s", inserted_ids, list(section_timetables.keys()))
            
            # Extract and store faculty timetables
            faculty_timetables = extract_faculty_timetables(section_timetables, faculties, subjects_per_section, dept_name, college_id)
            
            # Delete existing faculty timetables for this department
            FacultyTimetable.query.filter_by(dept_name=dept_name, college_id=college_id).delete()
            db.session.commit()
            
            # Store faculty timetables
            faculty_ids = []
            for faculty_name, timetable in faculty_timetables.items():
                # Get faculty_id from Faculty table
                faculty_record = Faculty.query.filter_by(faculty_name=faculty_name, college_id=college_id).first()
                if not faculty_record:
                    logging.warning(f"Faculty {faculty_name} not found in database for college {college_id}, skipping")
                    continue
                
                faculty_id = faculty_record.faculty_id
                
                # Store as a single combined timetable (not section-wise)
                new_faculty_tt = FacultyTimetable(
                    college_id=college_id,
                    dept_name=dept_name,
                    section='ALL',  # Mark as combined timetable
                    faculty_id=faculty_id,
                    faculty_name=faculty_name,
                    timetable=timetable
                )
                db.session.add(new_faculty_tt)
                db.session.flush()
                faculty_ids.append(new_faculty_tt.id)
            
            db.session.commit()
            logging.info("Inserted faculty timetables with ids=%s", faculty_ids)
            
            return jsonify({
                'ok': True,
                'message': 'Timetables generated and stored successfully',
                'ids': inserted_ids,
                'faculty_ids': faculty_ids,
                'sections': list(section_timetables.keys())
            }), 201
        
        except Exception as algo_error:
            logging.exception("Error during timetable generation")
            db.session.rollback()
            return jsonify({'ok': False, 'error': f'Timetable generation failed: {str(algo_error)}'}), 500

    except Exception as e:
        db.session.rollback()
        logging.exception("Failed to generate/store timetables")
        return jsonify({'ok': False, 'error': str(e)}), 500

def convert_timetable_dict_to_array(timetable_data):
    """Convert timetable to 2D array format [5 days][7 periods].
    Handles both:
    1. Nested dict format {day: {period: subject}} (from algorithm.py original)
    2. Already-array format [[...], ...] (from database storage)
    """
    if not timetable_data:
        return [[None] * 7 for _ in range(5)]
    
    # If already an array of arrays, return as-is (just validate structure)
    if isinstance(timetable_data, list):
        # Ensure it's a proper 2D array with 5 days and 7 periods per day
        if len(timetable_data) == 5:
            validated = []
            for day in timetable_data:
                if isinstance(day, list):
                    # Ensure day has exactly 7 periods
                    day_copy = day[:7] + [None] * (7 - len(day)) if len(day) < 7 else day[:7]
                    validated.append(day_copy)
                else:
                    validated.append([None] * 7)
            return validated
        else:
            # Wrong number of days, rebuild
            return [[None] * 7 for _ in range(5)]
    
    # If it's a dictionary, convert from dict format to array format
    if isinstance(timetable_data, dict):
        timetable_array = []
        for day in range(1, 6):  # 5 days
            day_array = []
            # Try both integer and string keys since JSON converts int keys to strings
            day_key = day if day in timetable_data else str(day)
            
            if day_key in timetable_data:
                day_periods = timetable_data[day_key]
                for period in range(1, 8):  # 7 periods
                    if isinstance(day_periods, dict):
                        # Try both int and string period keys
                        period_value = day_periods.get(period)
                        if period_value is None:
                            period_value = day_periods.get(str(period))
                        day_array.append(period_value)
                    else:
                        day_array.append(None)
            else:
                day_array = [None] * 7
            timetable_array.append(day_array)
        
        return timetable_array
    
    # Fallback for unexpected formats
    return [[None] * 7 for _ in range(5)]

@app.route('/get-timetables', methods=['GET', 'POST'])
def get_latest_timetables():
    try:
        if request.method == 'POST':
            data = request.get_json()
            dept_name = data.get('dept_name')
            college_id = data.get('college_id')
            
            if not dept_name or not college_id:
                return jsonify({'ok': False, 'error': 'Department name and college ID are required'}), 400
            
            timetables = SectionTimetable.query.filter_by(
                dept_name=dept_name,
                college_id=college_id
            ).all()
            
            if not timetables:
                return jsonify({'ok': False, 'error': 'No timetables found for this department'}), 404
            
            # Convert timetables to 2D array format for frontend display
            formatted_timetables = {}
            for t in timetables:
                try:
                    formatted_timetables[t.section_name] = convert_timetable_dict_to_array(t.timetable)
                    logging.info(f"Timetable for section {t.section_name} converted to array format")
                except Exception as e:
                    logging.error(f"Error formatting timetable for section {t.section_name}: {str(e)}")
                    formatted_timetables[t.section_name] = [[None] * 7 for _ in range(5)]
            
            return jsonify({
                'ok': True,
                'timetables': formatted_timetables
            }), 200
        else:
            # Handle GET request - get most recent timetables
            latest_time = db.session.query(db.func.max(SectionTimetable.created_at)).scalar()
            if not latest_time:
                return jsonify({'ok': False, 'error': 'No timetables found'}), 404
                
            latest_timetables = SectionTimetable.query.filter_by(created_at=latest_time).all()
            
            # Convert all timetables to 2D array format
            formatted_timetables = {}
            for t in latest_timetables:
                try:
                    formatted_timetables[t.section_name] = convert_timetable_dict_to_array(t.timetable)
                except Exception as e:
                    logging.error(f"Error converting timetable for section {t.section_name}: {str(e)}")
                    formatted_timetables[t.section_name] = [[None] * 7 for _ in range(5)]
            
            result = {
                'ok': True,
                'timetables': formatted_timetables,
                'created_at': latest_time.isoformat()
            }
        
        return jsonify(result), 200
        
    except Exception as e:
        logging.exception("Failed to retrieve timetables")
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/get-my-timetable', methods=['GET'])
def get_my_timetable():
    """Get combined timetable for the logged-in faculty member from faculty_timetables table."""
    try:
        faculty_id = session.get('faculty_id')
        college_id = session.get('college_id')
        
        if not faculty_id or not college_id:
            return jsonify({'ok': False, 'error': 'Faculty not logged in'}), 401
        
        # Get faculty name for reference
        faculty_record = Faculty.query.filter_by(faculty_id=faculty_id, college_id=college_id).first()
        if not faculty_record:
            return jsonify({'ok': False, 'error': 'Faculty record not found'}), 404
        
        # Get timetable for this faculty (should have section='ALL' for combined timetable)
        faculty_timetable = FacultyTimetable.query.filter_by(
            faculty_id=faculty_id,
            college_id=college_id,
            section='ALL'
        ).first()
        
        if not faculty_timetable:
            return jsonify({'ok': False, 'error': 'No timetable found for this faculty'}), 404
        
        # The timetable is already in 2D array format from storage
        timetable = faculty_timetable.timetable
        if isinstance(timetable, list):
            # Already in array format
            timetable_array = timetable
        else:
            # Convert if needed
            timetable_array = convert_timetable_dict_to_array(timetable)
        
        logging.info(f"Retrieved combined timetable for faculty {faculty_record.faculty_name} ({faculty_id})")
        
        return jsonify({
            'ok': True,
            'faculty_id': faculty_id,
            'faculty_name': faculty_record.faculty_name,
            'dept_name': faculty_record.dept_name,
            'timetable': timetable_array
        }), 200
        
    except Exception as e:
        logging.exception("Failed to retrieve faculty timetable")
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/get-faculty-timetables', methods=['GET'])
def get_faculty_timetables():
    """Get timetables for each faculty member by analyzing section timetables.
    Uses the algorithm's faculty mapping to determine which faculty teaches each subject."""
    try:
        dept_name = request.args.get('dept_name')
        college_id = request.args.get('college_id')
        
        if not dept_name or not college_id:
            return jsonify({'ok': False, 'error': 'Department name and college ID are required'}), 400
        
        # Get all section timetables for this department
        section_timetables = SectionTimetable.query.filter_by(
            dept_name=dept_name,
            college_id=college_id
        ).all()
        
        if not section_timetables:
            return jsonify({'ok': False, 'error': 'No timetables found for this department'}), 404
        
        logging.info(f"Found {len(section_timetables)} section timetables for {dept_name}")
        
        # Try to get faculty mappings from database first (Subject table)
        subjects = Subject.query.filter_by(
            dept_name=dept_name,
            college_id=college_id
        ).all()
        
        logging.info(f"Found {len(subjects)} subjects in database for {dept_name}")
        
        # Create a mapping of (subject_name, section) -> faculty_name from database
        subject_faculty_map_db = {}
        for subject in subjects:
            key = (subject.subject_name, subject.section)
            subject_faculty_map_db[key] = subject.faculty_name
        
        # Build faculty timetables by analyzing section timetables
        faculty_timetables = {}
        faculty_full_names = {}  # To store full faculty names if available
        
        for section_timetable in section_timetables:
            section_name = section_timetable.section_name
            # Convert timetable from storage format to 2D array
            timetable_array = convert_timetable_dict_to_array(section_timetable.timetable)
            
            logging.info(f"Processing section {section_name}")
            
            # Iterate through each time slot in the timetable
            for day_idx, day_data in enumerate(timetable_array):
                for period_idx, subject_slot in enumerate(day_data):
                    if subject_slot:  # If there's a subject in this slot
                        # Clean the subject name
                        subject_name = subject_slot.strip()
                        
                        # First, try to get faculty from database (Subject table)
                        lookup_key = (subject_name, section_name)
                        faculty_name = subject_faculty_map_db.get(lookup_key)
                        
                        # If not found in database, use the algorithm's faculty mapping
                        if not faculty_name and subject_name in algorithm_faculties:
                            faculty_data = algorithm_faculties[subject_name]
                            # If it's a list, pick the first one (or could randomize)
                            if isinstance(faculty_data, list):
                                faculty_name = faculty_data[0]
                            else:
                                faculty_name = faculty_data
                        
                        logging.debug(f"Slot {section_name}[Day {day_idx}][Period {period_idx}]: '{subject_name}' -> Faculty: {faculty_name}")
                        
                        if faculty_name:
                            # Initialize faculty timetable if not exists
                            if faculty_name not in faculty_timetables:
                                faculty_timetables[faculty_name] = [
                                    [None] * 7 for _ in range(5)
                                ]
                            
                            # Add this class to faculty's timetable with section info
                            faculty_timetables[faculty_name][day_idx][period_idx] = f"{subject_name}\n(Sec {section_name})"
                        else:
                            logging.warning(f"No faculty found for subject '{subject_name}' in section {section_name}")
        
        logging.info(f"Generated timetables for {len(faculty_timetables)} faculty members")
        
        if not faculty_timetables:
            logging.warning("No faculty timetables generated. Checking data...")
            logging.warning(f"  - Algorithm faculties count: {len(algorithm_faculties)}")
            logging.warning(f"  - Database subjects count: {len(subjects)}")
            return jsonify({
                'ok': True,
                'faculty_timetables': {},
                'faculty_list': []
            }), 200
        
        # Sort faculty by name for consistent display
        faculty_list = sorted(list(faculty_timetables.keys()))
        
        logging.info(f"Faculty list: {faculty_list}")
        
        return jsonify({
            'ok': True,
            'faculty_timetables': faculty_timetables,
            'faculty_list': faculty_list
        }), 200
        
    except Exception as e:
        logging.exception("Failed to retrieve faculty timetables")
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/get-faculty-timetables-db', methods=['GET'])
def get_faculty_timetables_db():
    """Get faculty timetables directly from faculty_timetables table"""
    try:
        dept_name = request.args.get('dept_name')
        college_id = request.args.get('college_id')
        
        if not dept_name or not college_id:
            return jsonify({'ok': False, 'error': 'Department name and college ID are required'}), 400
        
        # Query faculty timetables from the database table
        faculty_timetables_db = FacultyTimetable.query.filter_by(
            dept_name=dept_name,
            college_id=college_id
        ).all()
        
        if not faculty_timetables_db:
            return jsonify({
                'ok': True,
                'faculty_timetables': {},
                'message': 'No faculty timetables found in database'
            }), 200
        
        logging.info(f"Found {len(faculty_timetables_db)} faculty timetables for {dept_name}")
        
        # Convert to the format expected by frontend
        faculty_timetables = {}
        for ft in faculty_timetables_db:
            faculty_name = ft.faculty_name
            # Get the stored timetable (already in 2D array format or dict format)
            timetable_data = ft.timetable
            
            # If timetable is stored as dict, convert to 2D array format
            if isinstance(timetable_data, dict):
                # Dict format: {day: {period: subject}}
                days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
                array_timetable = []
                for day_idx, day in enumerate(days):
                    day_data = []
                    for period_idx in range(7):
                        subject = timetable_data.get(day, {}).get(str(period_idx), None)
                        day_data.append(subject)
                    array_timetable.append(day_data)
                faculty_timetables[faculty_name] = array_timetable
            else:
                # Already in array format
                faculty_timetables[faculty_name] = timetable_data
        
        return jsonify({
            'ok': True,
            'faculty_timetables': faculty_timetables
        }), 200
        
    except Exception as e:
        logging.exception("Failed to retrieve faculty timetables from database")
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/debug-faculty-timetables', methods=['GET'])
def debug_faculty_timetables():
    """Debug endpoint to check subject-faculty mappings for a department"""
    try:
        dept_name = request.args.get('dept_name')
        college_id = request.args.get('college_id')
        
        if not dept_name or not college_id:
            return jsonify({'ok': False, 'error': 'Department name and college ID are required'}), 400
        
        # Get all section timetables
        section_timetables = SectionTimetable.query.filter_by(
            dept_name=dept_name,
            college_id=college_id
        ).all()
        
        # Get all subjects
        subjects = Subject.query.filter_by(
            dept_name=dept_name,
            college_id=college_id
        ).all()
        
        # Get unique subjects from timetables
        timetable_subjects = set()
        for st in section_timetables:
            timetable_array = convert_timetable_dict_to_array(st.timetable)
            for day in timetable_array:
                for subject_slot in day:
                    if subject_slot:
                        timetable_subjects.add(subject_slot.strip())
        
        # Check which subjects are in timetables but not in Subject table
        subject_list = [(s.subject_name, s.section, s.faculty_name) for s in subjects]
        
        # Create section-wise subject list
        subject_by_section = {}
        for subject in subjects:
            key = subject.section
            if key not in subject_by_section:
                subject_by_section[key] = []
            subject_by_section[key].append({
                'subject_name': subject.subject_name,
                'faculty_name': subject.faculty_name
            })
        
        return jsonify({
            'ok': True,
            'section_timetables_count': len(section_timetables),
            'subjects_in_db_count': len(subjects),
            'unique_subjects_in_timetables': len(timetable_subjects),
            'subjects_by_section': subject_by_section,
            'all_timetable_subjects': sorted(list(timetable_subjects))
        }), 200
        
    except Exception as e:
        logging.exception("Failed to debug faculty timetables")
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/save-faculty-timetable', methods=['POST'])
def save_faculty_timetable():
    """Save a generated faculty timetable to the database"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['college_id', 'dept_name', 'section', 'faculty_id', 'faculty_name', 'timetable']
        for field in required_fields:
            if field not in data:
                return jsonify({'ok': False, 'error': f'Missing required field: {field}'}), 400
        
        college_id = data.get('college_id')
        dept_name = data.get('dept_name')
        section = data.get('section')
        faculty_id = data.get('faculty_id')
        faculty_name = data.get('faculty_name')
        timetable = data.get('timetable')
        
        # Validate that college exists
        college = Admin.query.filter_by(college_id=college_id).first()
        if not college:
            return jsonify({'ok': False, 'error': 'Invalid college ID'}), 400
        
        # Validate that department exists
        dept = Department.query.filter_by(name=dept_name, college_id=college_id).first()
        if not dept:
            return jsonify({'ok': False, 'error': 'Invalid department'}), 400
        
        # Validate section exists in department.sections (Issue #3 fix)
        valid_sections = dept.sections if dept.sections else []
        if section not in valid_sections:
            return jsonify({'ok': False, 'error': f'Invalid section: {section}. Valid sections: {valid_sections}'}), 400
        
        # Validate that faculty exists (Issue #2 fix - FK will enforce this, but validate early)
        faculty = Faculty.query.filter_by(faculty_id=faculty_id, college_id=college_id).first()
        if not faculty:
            return jsonify({'ok': False, 'error': f'Invalid faculty ID: {faculty_id}'}), 400
        
        # Check if timetable already exists for this faculty
        existing = FacultyTimetable.query.filter_by(
            college_id=college_id,
            dept_name=dept_name,
            section=section,
            faculty_id=faculty_id
        ).first()
        
        if existing:
            # Update existing record
            existing.timetable = timetable
            existing.faculty_name = faculty_name
            db.session.commit()
            logging.info(f"Updated faculty timetable for {faculty_name} (ID: {faculty_id}) in {dept_name}/{section}")
            return jsonify({
                'ok': True,
                'message': 'Faculty timetable updated successfully',
                'id': existing.id,
                'updated_at': existing.updated_at.isoformat() if existing.updated_at else None
            }), 200
        else:
            # Create new record
            faculty_timetable = FacultyTimetable(
                college_id=college_id,
                dept_name=dept_name,
                section=section,
                faculty_id=faculty_id,
                faculty_name=faculty_name,
                timetable=timetable
            )
            db.session.add(faculty_timetable)
            db.session.commit()
            logging.info(f"Saved new faculty timetable for {faculty_name} (ID: {faculty_id}) in {dept_name}/{section}")
            return jsonify({
                'ok': True,
                'message': 'Faculty timetable saved successfully',
                'id': faculty_timetable.id,
                'created_at': faculty_timetable.created_at.isoformat() if faculty_timetable.created_at else None
            }), 201
        
    except Exception as e:
        logging.exception("Failed to save faculty timetable")
        db.session.rollback()
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/get-faculty-timetable', methods=['GET'])
def get_faculty_timetable():
    """Retrieve a specific faculty timetable from the database"""
    try:
        college_id = request.args.get('college_id')
        dept_name = request.args.get('dept_name')
        faculty_id = request.args.get('faculty_id')
        section = request.args.get('section')
        
        if not all([college_id, dept_name, faculty_id]):
            return jsonify({'ok': False, 'error': 'Missing required parameters: college_id, dept_name, faculty_id'}), 400
        
        query = FacultyTimetable.query.filter_by(
            college_id=college_id,
            dept_name=dept_name,
            faculty_id=faculty_id
        )
        
        if section:
            query = query.filter_by(section=section)
        
        timetables = query.all()
        
        if not timetables:
            return jsonify({'ok': True, 'timetables': []}), 200
        
        return jsonify({
            'ok': True,
            'timetables': [t.to_dict() for t in timetables]
        }), 200
        
    except Exception as e:
        logging.exception("Failed to retrieve faculty timetable")
        return jsonify({'ok': False, 'error': str(e)}), 500

# Serve static files and handle root route
@app.route('/')
def serve_index():
    # Make index.html the default page
    try:
        return send_from_directory('.', 'index.html')
    except Exception as e:
        logging.error(f"index.html not found")
        return jsonify({'error': 'Default page not found'}), 404

@app.route('/<path:filename>')
def serve_static(filename):
    try:
        return send_from_directory('.', filename)
    except Exception as e:
        logging.error(f"File not found: {filename}")
        return jsonify({'error': 'File not found'}), 404

# Subject routes
@app.route('/add-subject', methods=['POST'])
def add_subject():
    try:
        data = request.get_json()
        new_subject = Subject(
            subject_name=data['subject_name'],
            subject_code=data['subject_code'],
            dept_name=data['dept_name'],
            college_id=data['college_id'],
            faculty_name=data['faculty_name'],
            section=data['section'],
            hours=data['hours'],
            lab=data['lab'],
            last=data['last']
        )
        db.session.add(new_subject)
        db.session.commit()
        return jsonify({'ok': True, 'subject': new_subject.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/get-subjects', methods=['GET'])
def get_subjects():
    try:
        # Support both college_id filter and dept_name/section filter
        college_id = request.args.get('college_id')
        dept_name = request.args.get('dept_name')
        section = request.args.get('section')
        
        logging.info(f"get-subjects called with: college_id={college_id}, dept_name={dept_name}, section={section}")
        
        if dept_name and section:
            # Filter by department and section
            subjects = Subject.query.filter_by(
                dept_name=dept_name,
                section=section
            ).all()
            logging.info(f"Found {len(subjects)} subjects for {dept_name}/{section}")
            # Return full metadata for each subject (no deduplication - allows multiple faculties)
            subject_list = [
                {
                    'name': subject.subject_name,
                    'code': subject.subject_code,
                    'hours': subject.hours,
                    'lab': bool(subject.lab),
                    'last': bool(subject.last),
                    'faculty': subject.faculty_name
                }
                for subject in subjects
            ]
            # Deduplicate by subject name, keep first occurrence (metadata is same)
            seen = set()
            unique_subjects = []
            for subj in subject_list:
                if subj['name'] not in seen:
                    seen.add(subj['name'])
                    unique_subjects.append(subj)
            unique_subjects = sorted(unique_subjects, key=lambda x: x['name'])
            logging.info(f"Subject metadata: {unique_subjects}")
        elif college_id:
            # Filter by college_id (old behavior)
            subjects = Subject.query.filter_by(college_id=college_id).all()
            unique_subjects = [subject.to_dict() for subject in subjects]
        else:
            return jsonify({'ok': False, 'error': 'Either college_id or (dept_name and section) is required'}), 400
        
        return jsonify({
            'ok': True,
            'subjects': unique_subjects
        }), 200
    except Exception as e:
        logging.exception("Failed to get subjects")
        return jsonify({'ok': False, 'error': str(e)}), 500


@app.route('/get-constraints', methods=['GET'])
def get_constraints():
    """Return saved strict and forbidden constraints for a department + section"""
    try:
        dept_name = request.args.get('dept_name')
        section = request.args.get('section')

        if not dept_name or not section:
            return jsonify({'ok': False, 'error': 'dept_name and section are required'}), 400

        constraints = SubjectConstraint.query.filter_by(dept_name=dept_name, section=section).all()

        strict = []
        forbidden = []
        for c in constraints:
            row = {'subject': c.subject, 'day': c.day, 'period': c.period}
            if c.constraint_type == 'strict':
                strict.append(row)
            else:
                forbidden.append(row)

        return jsonify({'ok': True, 'strict': strict, 'forbidden': forbidden}), 200
    except Exception as e:
        logging.exception('Failed to get constraints')
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/debug-subjects', methods=['GET'])
def debug_subjects():
    """Debug endpoint to check all subjects in database"""
    try:
        all_subjects = Subject.query.all()
        logging.info(f"Total subjects in database: {len(all_subjects)}")
        
        subject_list = []
        for subject in all_subjects:
            logging.info(f"Subject: {subject.subject_name}, Dept: {subject.dept_name}, Section: {subject.section}")
            subject_list.append({
                'subject_name': subject.subject_name,
                'dept_name': subject.dept_name,
                'section': subject.section,
                'faculty_name': subject.faculty_name
            })
        
        return jsonify({
            'ok': True,
            'total': len(subject_list),
            'subjects': subject_list
        }), 200
    except Exception as e:
        logging.exception("Failed to get debug subjects")
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/get-subject/<int:id>', methods=['GET'])
def get_subject(id):
    try:
        subject = Subject.query.get_or_404(id)
        return jsonify({'ok': True, 'subject': subject.to_dict()}), 200
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 404

@app.route('/update-subject/<int:id>', methods=['PUT'])
def update_subject(id):
    try:
        subject = Subject.query.get_or_404(id)
        data = request.get_json()
        
        subject.subject_name = data['subject_name']
        subject.subject_code = data['subject_code']
        subject.dept_name = data['dept_name']
        subject.faculty_name = data['faculty_name']
        subject.section = data['section']
        subject.hours = data['hours']
        subject.lab = data['lab']
        subject.last = data['last']
        
        db.session.commit()
        return jsonify({'ok': True, 'subject': subject.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/delete-subject/<int:id>', methods=['DELETE'])
def delete_subject(id):
    try:
        subject = Subject.query.get_or_404(id)
        db.session.delete(subject)
        db.session.commit()
        return jsonify({'ok': True, 'message': 'Subject deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/authority/login', methods=['POST'])
def login_authority():
    try:
        data = request.get_json()
        faculty_id = data.get('faculty_id')
        college_id = data.get('college_id')
        password = data.get('faculty_password')

        faculty = Faculty.query.filter_by(
            faculty_id=faculty_id,
            college_id=college_id
        ).first()

        if faculty and faculty.faculty_password == password:
            # Check if faculty has authority role
            if faculty.designation not in ['HOD', 'DEAN', 'PRINCIPAL']:
                return jsonify({
                    'ok': False,
                    'error': 'Unauthorized access. Only HOD, DEAN, or PRINCIPAL can login as authority.'
                }), 403

            return jsonify({
                'ok': True,
                'faculty_id': faculty.faculty_id,
                'faculty_name': faculty.faculty_name,
                'college_id': faculty.college_id,
                'dept_name': faculty.dept_name,
                'designation': faculty.designation
            }), 200
        else:
            return jsonify({
                'ok': False,
                'error': 'Invalid credentials'
            }), 401

    except Exception as e:
        logging.exception("Failed to login authority")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500

@app.route('/faculty/login', methods=['POST'])
def login_faculty():
    try:
        data = request.get_json()
        faculty_id = data.get('faculty_id')
        college_id = data.get('college_id')
        password = data.get('faculty_password')

        faculty = Faculty.query.filter_by(
            faculty_id=faculty_id,
            college_id=college_id
        ).first()

        if faculty and faculty.faculty_password == password:
            # Set Flask session variables
            session['faculty_id'] = faculty.faculty_id
            session['college_id'] = faculty.college_id
            session['faculty_name'] = faculty.faculty_name
            session['dept_name'] = faculty.dept_name
            session['designation'] = faculty.designation
            session.permanent = True  # Make session persistent
            
            # We already have dept_name in the faculty model
            dept_name = faculty.dept_name

            return jsonify({
                'ok': True,
                'faculty_id': faculty.faculty_id,
                'faculty_name': faculty.faculty_name,
                'college_id': faculty.college_id,
                'dept_name': dept_name,
                'designation': faculty.designation
            }), 200
        else:
            return jsonify({
                'ok': False,
                'error': 'Invalid credentials'
            }), 401

    except Exception as e:
        logging.exception("Failed to login faculty")
        return jsonify({
            'ok': False,
            'error': str(e)
        }), 500

@app.route('/admin/register', methods=['POST'])
def register_admin():
    try:
        data = request.form
        admin_name = data.get('admin_name')
        college_name = data.get('college_name')
        college_id = data.get('college_id')
        password = data.get('admin_password')

        # Check if all required fields are present
        if not all([admin_name, college_name, college_id, password]):
            return jsonify({'error': 'All fields are required'}), 400

        # Check if college_id already exists
        if Admin.query.filter_by(college_id=college_id).first():
            return jsonify({'error': 'College ID already registered'}), 400

        # Create new admin
        new_admin = Admin(
            admin_name=admin_name,
            college_name=college_name,
            college_id=college_id,
            admin_password=password
        )

        # Save to database
        try:
            db.session.add(new_admin)
            db.session.commit()
            return jsonify({
                'message': 'Registration successful! Please log in.',
                'admin_name': admin_name,
                'college_name': college_name,
                'college_id': college_id
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Database error. Please try again.'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/login', methods=['POST'])
def login_admin():
    try:
        data = request.form
        college_id = data.get('college_id')
        password = data.get('admin_password')

        if not college_id or not password:
            return jsonify({'error': 'College ID and password are required'}), 400

        # Find admin by college_id
        admin = Admin.query.filter_by(college_id=college_id).first()
        
        if not admin:
            return jsonify({'error': 'College ID not found'}), 401
        
        # Check password
        if admin.admin_password != password:  # In a real app, you'd use password hashing
            return jsonify({'error': 'Invalid password'}), 401

        # Store college_id in session
        session['college_id'] = admin.college_id
        session.permanent = True  # Use permanent session with the timeout we configured
        
        return jsonify({
            'message': 'Login successful',
            'admin_name': admin.admin_name,
            'college_name': admin.college_name,
            'college_id': admin.college_id
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Department routes
@app.route('/add_departments')
def add_departments_page():
    return send_from_directory('.', 'add_departments.html')

@app.route('/get-departments', methods=['GET'])
def get_departments():
    try:
        # Get college_id from query parameter
        college_id = request.args.get('college_id')
        if not college_id:
            return jsonify({'error': 'College ID is required'}), 400

        # Get departments for specific college
        departments = Department.query.filter_by(college_id=college_id).all()
        departments_list = [
            {
                'id': dept.id,
                'name': dept.name,
                'sections': dept.sections,
                'college_id': dept.college_id
            }
            for dept in departments
        ]
        return jsonify({'departments': departments_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/department/<int:dept_id>', methods=['PUT'])
def update_department(dept_id):
    try:
        department = Department.query.get(dept_id)
        if not department:
            return jsonify({'error': 'Department not found'}), 404

        data = request.get_json()
        
        if 'name' in data:
            # Check if new name already exists in another department in the same college
            existing = Department.query.filter(
                Department.name == data['name'],
                Department.id != dept_id,
                Department.college_id == department.college_id
            ).first()
            if existing:
                return jsonify({'error': 'Department name already exists in this college'}), 400
            department.name = data['name']
        
        if 'sections' in data:
            if not data['sections']:  # Check if sections array is empty
                return jsonify({'error': 'Department must have at least one section'}), 400
            department.sections = data['sections']

        db.session.commit()
        return jsonify({
            'message': 'Department updated successfully',
            'department': {
                'id': department.id,
                'name': department.name,
                'sections': department.sections
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/department/<int:dept_id>', methods=['DELETE'])
def delete_department(dept_id):
    try:
        department = Department.query.get(dept_id)
        if not department:
            return jsonify({'error': 'Department not found'}), 404

        # Check for associated subjects
        subjects = Subject.query.filter_by(dept_name=department.name, college_id=department.college_id).all()
        if subjects:
            return jsonify({
                'error': 'Cannot delete department. There are subjects associated with this department. Please delete or reassign all subjects first.'
            }), 400

        # Check for associated faculty
        faculty = Faculty.query.filter_by(dept_name=department.name, college_id=department.college_id).all()
        if faculty:
            return jsonify({
                'error': 'Cannot delete department. There are faculty members associated with this department. Please delete or reassign all faculty members first.'
            }), 400

        db.session.delete(department)
        db.session.commit()
        return jsonify({'message': 'Department deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        error_message = str(e)
        if 'foreign key constraint' in error_message.lower():
            return jsonify({
                'error': 'Cannot delete department because it has associated subjects or faculty members. Please remove all subjects and faculty members first.'
            }), 400
        return jsonify({'error': error_message}), 500

@app.route('/add-department', methods=['POST'])
def add_department():
    try:
        data = request.get_json()
        department_name = data.get('departmentName')
        sections = data.get('sections', [])
        college_id = data.get('college_id')

        if not department_name or not sections or not college_id:
            return jsonify({'error': 'Department name, sections, and college ID are required'}), 400

        # Check if department already exists for this college
        existing_dept = Department.query.filter_by(name=department_name, college_id=college_id).first()
        if existing_dept:
            return jsonify({'error': 'Department already exists in this college'}), 400

        # Create new department
        new_department = Department(
            name=department_name,
            sections=sections,
            college_id=college_id
        )

        db.session.add(new_department)
        db.session.commit()

        return jsonify({
            'message': 'Department added successfully',
            'department': {
                'id': new_department.id,
                'name': new_department.name,
                'sections': new_department.sections
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/get-faculty', methods=['GET'])
def get_faculty():
    try:
        # Get college_id from query parameter
        college_id = request.args.get('college_id')
        if not college_id:
            return jsonify({'error': 'College ID is required'}), 400

        # Get faculty members for specific college
        faculty_members = Faculty.query.filter_by(college_id=college_id).all()
        faculty_list = [faculty.to_dict() for faculty in faculty_members]
        
        return jsonify({'faculty': faculty_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-faculty/<faculty_id>', methods=['GET'])
def get_faculty_by_id(faculty_id):
    try:
        faculty = Faculty.query.get(faculty_id)
        if not faculty:
            return jsonify({'error': 'Faculty not found'}), 404
        
        return jsonify({'faculty': faculty.to_dict()}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/faculty/<faculty_id>', methods=['PUT'])
def update_faculty(faculty_id):
    try:
        faculty = Faculty.query.get(faculty_id)
        if not faculty:
            return jsonify({'error': 'Faculty not found'}), 404

        data = request.get_json()
        
        # Validate required fields are not empty if provided
        if 'faculty_name' in data:
            if not data['faculty_name'].strip():
                return jsonify({'error': 'Faculty name cannot be empty'}), 400
            faculty.faculty_name = data['faculty_name'].strip()
            
        if 'designation' in data:
            if data['designation'] not in ['HOD', 'DEAN', 'PRINCIPAL', 'PROFESSOR']:
                return jsonify({'error': 'Invalid designation'}), 400
            faculty.designation = data['designation']
        
        if 'dept_name' in data:
            if not data['dept_name'].strip():
                return jsonify({'error': 'Department name cannot be empty'}), 400
            # Verify department exists in the same college
            department = Department.query.filter_by(
                name=data['dept_name'],
                college_id=faculty.college_id
            ).first()
            if not department:
                return jsonify({'error': 'Department not found'}), 404
            faculty.dept_name = data['dept_name']

        if 'faculty_password' in data:
            if not data['faculty_password'].strip():
                return jsonify({'error': 'Password cannot be empty'}), 400
            faculty.faculty_password = data['faculty_password']

        db.session.commit()
        return jsonify({
            'message': 'Faculty updated successfully',
            'faculty': faculty.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/faculty/<faculty_id>', methods=['DELETE'])
def delete_faculty(faculty_id):
    try:
        faculty = Faculty.query.get(faculty_id)
        if not faculty:
            return jsonify({'error': 'Faculty not found'}), 404

        db.session.delete(faculty)
        db.session.commit()
        return jsonify({'message': 'Faculty deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/add-faculty', methods=['POST'])
def add_faculty():
    try:
        data = request.get_json()
        
        # Check if all required fields are present
        required_fields = ['faculty_id', 'faculty_name', 'designation', 'dept_name', 'faculty_password', 'college_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        # Validate designation
        if data['designation'] not in ['HOD', 'DEAN', 'PRINCIPAL', 'PROFESSOR']:
            return jsonify({'error': 'Invalid designation'}), 400

        # Check if faculty already exists
        existing_faculty = Faculty.query.filter_by(faculty_id=data['faculty_id']).first()
        if existing_faculty:
            return jsonify({'error': 'Faculty ID already exists'}), 400

        # Check if department exists
        department = Department.query.filter_by(name=data['dept_name'], college_id=data['college_id']).first()
        if not department:
            return jsonify({'error': 'Department not found'}), 404

        # Create new faculty
        new_faculty = Faculty(
            faculty_id=data['faculty_id'],
            faculty_name=data['faculty_name'],
            designation=data['designation'].upper(),
            dept_name=data['dept_name'],
            faculty_password=data['faculty_password'],
            college_id=data['college_id']
        )

        db.session.add(new_faculty)
        db.session.commit()

        return jsonify({
            'message': 'Faculty added successfully',
            'faculty': new_faculty.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/get_departments_for_admin', methods=['GET'])
def get_departments_for_admin():
    try:
        # Debug logging
        app.logger.info('Session contents: %s', dict(session))
        
        # Check if user is logged in
        college_id = session.get('college_id')
        app.logger.info('College ID from session: %s', college_id)
        
        if not college_id:
            return jsonify({'error': 'Not logged in'}), 401
            
        # Get all departments for the college
        departments = Department.query.filter_by(college_id=college_id).all()
        
        # Return department names
        department_names = [dept.name for dept in departments]
        return jsonify(department_names)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get departments that have timetables
@app.route('/get-departments-with-timetables', methods=['GET'])
def get_departments_with_timetables():
    try:
        college_id = request.args.get('college_id')
        if not college_id:
            return jsonify({'error': 'College ID is required'}), 400

        # Get distinct department names that have timetables
        departments = db.session.query(SectionTimetable.dept_name)\
            .filter_by(college_id=college_id)\
            .distinct()\
            .all()
        
        # Extract department names from query result
        dept_names = [dept[0] for dept in departments]
        
        return jsonify({
            'ok': True,
            'departments': dept_names
        }), 200
    except Exception as e:
        logging.exception("Failed to retrieve departments with timetables")
        return jsonify({'error': str(e)}), 500

@app.route('/get-all-departments', methods=['GET'])
def get_all_departments():
    """Get all departments in the system"""
    try:
        departments = db.session.query(Department).all()
        dept_list = []
        for dept in departments:
            dept_list.append({
                'id': dept.id,
                'name': dept.name,
                'college_id': dept.college_id
            })
        
        return jsonify({
            'ok': True,
            'departments': dept_list
        }), 200
    except Exception as e:
        logging.exception("Failed to retrieve departments")
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/save-constraints', methods=['POST'])
def save_constraints():
    """Save strict and forbidden placement constraints for subjects"""
    try:
        data = request.get_json()
        dept_name = data.get('dept_name')
        strict_constraints = data.get('strict_constraints', [])
        forbidden_constraints = data.get('forbidden_constraints', [])
        section = data.get('section')
        
        if not dept_name:
            return jsonify({'ok': False, 'error': 'Department name is required'}), 400
        
        # Here you would save the constraints to a database or config file
        # For now, we'll just log them and update the algorithm.py configuration
        logging.info(f"Strict constraints for {dept_name}: {strict_constraints}")
        logging.info(f"Forbidden constraints for {dept_name}: {forbidden_constraints}")
        
        # Update the algorithm constraints (in a production system, store in DB)
        # This is a simplified approach - you might want to store in DB
        # Validate no conflicts between strict and forbidden constraints
        conflicts = []
        for s in strict_constraints:
            for f in forbidden_constraints:
                if (s.get('subject') == f.get('subject') and
                    s.get('day') == f.get('day') and
                    s.get('period') == f.get('period')):
                    conflicts.append(f"{s.get('subject')} on {s.get('day')} P{s.get('period')}")

        if conflicts:
            logging.warning(f"Constraint save blocked due to conflicts: {conflicts}")
            return jsonify({'ok': False, 'error': 'Conflicting constraints: ' + ', '.join(conflicts)}), 400

        # Save constraints to DB
        try:
            # Validate department and section exist
            if not section:
                return jsonify({'ok': False, 'error': 'Section is required'}), 400

            dept = Department.query.filter_by(name=dept_name).first()
            if not dept:
                return jsonify({'ok': False, 'error': 'Department not found'}), 404

            # Build list of new constraints to insert
            new_constraints = []
            
            # Create strict constraints
            for c in strict_constraints:
                sc = SubjectConstraint(
                    college_id=dept.college_id,
                    dept_name=dept_name,
                    section=section,
                    subject=c.get('subject'),
                    day=c.get('day'),
                    period=int(c.get('period')),
                    constraint_type='strict'
                )
                new_constraints.append(sc)

            # Create forbidden constraints
            for c in forbidden_constraints:
                fc = SubjectConstraint(
                    college_id=dept.college_id,
                    dept_name=dept_name,
                    section=section,
                    subject=c.get('subject'),
                    day=c.get('day'),
                    period=int(c.get('period')),
                    constraint_type='forbidden'
                )
                new_constraints.append(fc)

            # Delete existing constraints for this department + section
            SubjectConstraint.query.filter_by(dept_name=dept_name, section=section).delete()
            
            # Add all new constraints
            for constraint in new_constraints:
                db.session.add(constraint)

            db.session.commit()
            
            logging.info(f"Saved {len(new_constraints)} constraints for {dept_name}/{section}")

            return jsonify({
                'ok': True,
                'message': 'Constraints saved successfully',
                'strict_count': len(strict_constraints),
                'forbidden_count': len(forbidden_constraints)
            }), 200
        except Exception as e:
            db.session.rollback()
            logging.exception('Failed to persist constraints')
            return jsonify({'ok': False, 'error': str(e)}), 500
    except Exception as e:
        logging.exception("Failed to save constraints")
        return jsonify({'ok': False, 'error': str(e)}), 500

# Error handler for 404 Not Found
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'The requested URL was not found on the server.'}), 404

if __name__ == '__main__':
    # Create all database tables
    with app.app_context():
        db.create_all()
    
    # Run the app on localhost:5000
    app.run(host='localhost', port=5000, debug=True)