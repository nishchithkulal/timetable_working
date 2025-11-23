# app/models/database.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB

db = SQLAlchemy()

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sections = db.Column(JSONB, nullable=False)
    college_id = db.Column(db.String(50), db.ForeignKey('admin.college_id'), nullable=False)
    
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
        db.UniqueConstraint('section_name', 'dept_name', 'college_id', name='unique_section_dept'),
        db.Index('idx_timetable_lookup', 'dept_name', 'college_id', 'created_at')
    )

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(100), nullable=False)
    subject_code = db.Column(db.String(20), nullable=False)
    dept_name = db.Column(db.String(100), nullable=False)
    college_id = db.Column(db.String(50), nullable=False)
    faculty_name = db.Column(db.String(100), nullable=False)
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
    period = db.Column(db.String(10), nullable=False)
    constraint_type = db.Column(db.String(20), nullable=False)
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

class BreakConfiguration(db.Model):
    """Stores break timings (2 normal breaks + 1 lunch break) for each department"""
    __tablename__ = 'break_configurations'
    id = db.Column(db.Integer, primary_key=True)
    college_id = db.Column(db.String(50), nullable=False)
    dept_name = db.Column(db.String(100), nullable=False)
    first_break_period = db.Column(db.String(10), nullable=False, default='2')  # Period number for first break (e.g., '2')
    lunch_break_period = db.Column(db.String(10), nullable=False, default='4')  # Period number for lunch break (e.g., '4')
    second_break_period = db.Column(db.String(10), nullable=False, default='6')  # Period number for second break (e.g., '6')
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

    __table_args__ = (
        db.UniqueConstraint('college_id', 'dept_name', name='unique_break_config_per_dept'),
        db.ForeignKeyConstraint(
            ['dept_name', 'college_id'],
            ['departments.name', 'departments.college_id'],
            name='fk_break_config_department',
            onupdate='CASCADE',
            ondelete='CASCADE'
        ),
        db.Index('idx_break_config_lookup', 'college_id', 'dept_name')
    )

    def to_dict(self):
        return {
            'id': self.id,
            'college_id': self.college_id,
            'dept_name': self.dept_name,
            'first_break_period': self.first_break_period,
            'lunch_break_period': self.lunch_break_period,
            'second_break_period': self.second_break_period,
            'created_at': self.created_at.isoformat() if self.created_at is not None else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at is not None else None
        }
