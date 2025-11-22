# Database Schema Validation Report

**Generated:** November 21, 2025  
**Status:** ✅ FUNCTIONAL | ⚠️  DATA INTEGRITY GAPS IDENTIFIED

---

## Executive Summary

The database schema is **operationally functional** for the current timetable generation system. All critical tables are properly defined with appropriate primary keys, indexes, and most foreign key relationships. However, **3 MEDIUM-severity gaps** exist in referential integrity that could lead to data consistency issues as the system scales.

---

## Entity Hierarchy

```
Admin (college_id)
├── Department (college_id FK)
│   ├── Subject (dept_name, college_id FK)
│   ├── SectionTimetable (dept_name, college_id FK)
│   ├── Faculty (dept_name, college_id FK)
│   └── SubjectConstraint (dept_name, college_id - NO FK)
└── FacultyTimetable (college_id FK)
```

---

## Detailed Schema Analysis

### ✅ CORRECT IMPLEMENTATIONS

#### 1. **Admin Table**
- **Structure**: College-wide root entity
- **PK**: `college_id` (String, 50)
- **Columns**: admin_name, college_name, admin_password
- **Status**: ✅ Correct
- **Justification**: 
  - Simple, efficient primary key
  - Immutable identifier for college
  - No foreign keys needed (root entity)

#### 2. **Department Table**
- **Structure**: Departments within a college
- **PK**: `id` (Integer)
- **FK**: `college_id` → `Admin.college_id`
- **Unique Constraint**: `(name, college_id)` - ensures no duplicate departments per college
- **Status**: ✅ Correct
- **Justification**:
  - Composite unique constraint prevents duplicate dept names within same college
  - Good for multi-tenant support
  - Cascade on delete ensures clean removal
  - JSONB sections array allows flexible section management

#### 3. **Subject Table**
- **Structure**: Courses taught in departments
- **PK**: `id` (Integer)
- **FK**: 
  - `(dept_name, college_id)` → `Department.name, college_id`
  - `college_id` → `Admin.college_id`
- **Unique Constraint**: `(subject_code, college_id)`
- **Columns**: subject_name, subject_code, faculty_name, hours, lab (boolean), last (boolean)
- **Status**: ✅ Correct (with caveat)
- **Justification**:
  - Composite FK ensures subject only exists in valid departments
  - Cascading restricts prevent accidental department deletion
  - Metadata columns (hours, lab, last) properly support constraint logic
  - ⚠️ **Caveat**: See Issue #4 below regarding faculty_name

#### 4. **Faculty Table**
- **Structure**: Faculty members per department
- **PK**: `faculty_id` (String, 50)
- **FK**: 
  - `(dept_name, college_id)` → `Department.name, college_id`
  - `college_id` → `Admin.college_id`
- **Unique Constraint**: `(faculty_id, college_id)` - same faculty ID can't exist in two colleges
- **Status**: ✅ Correct
- **Justification**:
  - Proper multi-tenancy support
  - Composite FK ensures faculty belongs to valid department
  - Faculty can't be orphaned (RESTRICT prevents deletion)

#### 5. **SectionTimetable Table**
- **Structure**: Generated timetables for sections
- **PK**: `id` (Integer)
- **FK**: `(dept_name, college_id)` → `Department.name, college_id`
- **Unique Constraint**: `(section_name, dept_name, college_id)` - one timetable per section
- **Indexes**: `idx_timetable_lookup` on (dept_name, college_id, created_at)
- **Status**: ✅ Correct
- **Justification**:
  - Composite FK ensures timetable belongs to valid department
  - Unique constraint prevents duplicate timetables for same section
  - Index optimized for query patterns (dept + college lookups)
  - ⚠️ **Caveat**: See Issue #3 below regarding section validation

#### 6. **SubjectConstraint Table**
- **Structure**: Strict and forbidden placement constraints
- **PK**: `id` (Integer)
- **Columns**: college_id, dept_name, section, subject, day, period, constraint_type
- **Unique Constraint**: `(dept_name, section, subject, day, period, constraint_type, college_id)` - prevents duplicate constraints
- **Status**: ⚠️ Partially Correct
- **Justification**:
  - Proper unique constraint prevents duplicate rules
  - Good index for constraint lookups
  - ❌ **Missing**: No FK to Department (See Issue #1)

#### 7. **FacultyTimetable Table** (NEW)
- **Structure**: Stores generated personal faculty timetables
- **PK**: `id` (Integer)
- **FK**: `college_id` → `Admin.college_id`
- **Unique Constraint**: `(college_id, dept_name, section, faculty_id)` - one timetable per faculty
- **Columns**: faculty_id, faculty_name, timetable (JSON), created_at, updated_at
- **Status**: ⚠️ Partially Correct
- **Justification**:
  - Unique constraint prevents duplicate timetables
  - Timestamps support audit trail
  - ❌ **Missing**: No FK to Faculty table (See Issue #2)

---

## Issues Identified

### Issue #1: SubjectConstraint Missing FK to Department [MEDIUM]

**Current State:**
```python
college_id = db.Column(db.String(50), nullable=False)
dept_name = db.Column(db.String(100), nullable=False)
section = db.Column(db.String(10), nullable=False)
# NO Foreign Key Constraint
```

**Problem:**
- Constraints can be created for non-existent departments
- If a department is deleted, orphaned constraints remain in database
- No referential integrity at DB level

**Impact:**
- Data consistency issues over time
- Orphaned constraint records accumulate
- Manual cleanup required

**Recommendation:**
```python
__table_args__ = (
    db.ForeignKeyConstraint(
        ['dept_name', 'college_id'],
        ['departments.name', 'departments.college_id'],
        name='fk_constraint_department',
        onupdate='CASCADE',
        ondelete='CASCADE'  # Auto-delete constraints when dept deleted
    ),
    # ... other constraints
)
```

**Difficulty**: Easy  
**Priority**: Medium (affects data cleanup)

---

### Issue #2: FacultyTimetable Missing FK to Faculty [MEDIUM]

**Current State:**
```python
faculty_id = db.Column(db.String(50), nullable=False)
faculty_name = db.Column(db.String(100), nullable=False)
# NO Foreign Key Constraint to Faculty table
```

**Problem:**
- Timetables can exist for deleted faculty members
- Data duplication: faculty info stored in both Faculty and FacultyTimetable
- No cascading delete when faculty removed

**Impact:**
- Orphaned timetables remain after faculty deletion
- Manual cleanup required
- Hard to track which timetables are valid

**Recommendation:**
```python
__table_args__ = (
    db.ForeignKeyConstraint(
        ['faculty_id', 'college_id'],
        ['faculty.faculty_id', 'faculty.college_id'],
        name='fk_timetable_faculty',
        onupdate='CASCADE',
        ondelete='CASCADE'  # Auto-delete timetables when faculty deleted
    ),
    # ... other constraints
)
```

**Difficulty**: Medium (requires migration)  
**Priority**: Medium (affects data cleanup)

---

### Issue #3: SectionTimetable Not Validated Against Department.sections [LOW]

**Current State:**
```python
section_name = db.Column(db.String(10), nullable=False)  # Just stored, not validated
# Department.sections is JSONB array: ["A", "B", "C"]
```

**Problem:**
- Section timetable can be created for section_name that doesn't exist in Department.sections array
- Database doesn't enforce this relationship (JSONB is not relational)
- Application-level validation only (brittle)

**Example:**
```
Department "CSE" has sections: ["A", "B", "C"]
But timetable created for section "D" → Not caught at DB level
```

**Impact:**
- Invalid sections can appear in timetables
- No DB-level validation
- Requires application to enforce

**Recommendation:**
Add application-level validation in endpoints:
```python
@app.route('/generate-timetable', methods=['POST'])
def generate_timetable():
    section = data.get('section')
    dept = Department.query.filter_by(...).first()
    
    if section not in dept.sections:  # Validate before saving
        return jsonify({'error': 'Invalid section'}), 400
    # ... continue
```

**Difficulty**: Easy (application-level only)  
**Priority**: Low (UX issue, not data integrity)

---

### Issue #4: Subject.faculty_name Not Linked to Faculty Table [MEDIUM]

**Current State:**
```python
faculty_name = db.Column(db.String(100), nullable=False)  # Just a string
# No FK to Faculty.faculty_name
```

**Problem:**
- Subject stores faculty_name but it's not validated
- Faculty can be deleted but subject still references old name
- If faculty name changes, must update all Subject records manually
- Data duplication across Subject and Faculty tables

**Example:**
```
Faculty: Dr. Amit Kumar (faculty_id: AKK)
Subject: Mathematics → faculty_name: "Dr. Amit Kumar"

If faculty name changes to "Dr. A. Kumar", subject still shows old name
If faculty deleted, subject becomes orphaned
```

**Impact:**
- Data consistency issues when faculty records updated
- Hard to maintain referential integrity
- Manual updates required

**Recommendation - Option A (Better):**
Store `faculty_id` instead:
```python
faculty_id = db.Column(db.String(50), nullable=False)
faculty_name = db.Column(db.String(100), nullable=False)  # Cached copy for display

__table_args__ = (
    db.ForeignKeyConstraint(
        ['faculty_id', 'college_id'],
        ['faculty.faculty_id', 'faculty.college_id'],
        name='fk_subject_faculty',
        onupdate='CASCADE',
        ondelete='RESTRICT'  # Prevent faculty deletion if subjects exist
    ),
)
```

**Recommendation - Option B (Alternative):**
Create `FacultyName` lookup table (overkill for current use case)

**Difficulty**: Medium (requires migration and data updates)  
**Priority**: Medium (affects faculty management)

---

### Issue #5: Department.sections as JSONB (Not an Issue) [LOW - INFO ONLY]

**Current State:**
```python
sections = db.Column(JSONB, nullable=False)  # Array: ["A", "B", "C"]
```

**Analysis:**
- ✅ This is **intentional and correct**
- JSONB provides flexibility for adding/removing sections
- Normalized table would be overkill for this use case
- Application-level validation is sufficient

**Recommendation:**
Keep as-is; this design choice is sound.

---

## Summary Table

| Issue | Model | Severity | Type | Status | Fix Difficulty |
|-------|-------|----------|------|--------|-----------------|
| #1 | SubjectConstraint | MEDIUM | Missing FK | Actionable | Easy |
| #2 | FacultyTimetable | MEDIUM | Missing FK | Actionable | Medium |
| #3 | SectionTimetable | LOW | Missing Validation | Actionable | Easy |
| #4 | Subject | MEDIUM | Design Flaw | Actionable | Medium |
| #5 | Department | LOW | Design Choice | ✅ OK | N/A |

---

## Operational Assessment

### Current Capability
✅ **The database schema supports:**
- Multi-tenant operations (college_id segregation)
- Timetable generation and storage
- Constraint management
- Faculty schedule tracking
- Cascading operations where defined
- Efficient querying with proper indexes

### Data Integrity Concerns
⚠️ **The schema allows:**
1. Orphaned constraints if department deleted
2. Orphaned faculty timetables if faculty deleted
3. Invalid sections to be timetabled
4. Faculty name inconsistencies over time

### Risk Level
- **Production Environment**: MEDIUM RISK
- **Small Deployments**: LOW RISK (manual data management possible)
- **Large Multi-College**: HIGH RISK (needs fixes before scaling)

---

## Recommended Action Plan

### Phase 1 - Quick Wins (Implement First)
1. ✅ Add application-level validation for section names (Issue #3)
   - Effort: 30 minutes
   - Impact: Prevents invalid sections

2. ✅ Add FK to SubjectConstraint → Department (Issue #1)
   - Effort: 1 hour (includes migration)
   - Impact: Prevents orphaned constraints

### Phase 2 - Data Model Improvements (Implement When Adding Faculty Features)
3. ✅ Refactor Subject.faculty_name to use faculty_id + FK (Issue #4)
   - Effort: 2-3 hours (includes migration + data update)
   - Impact: Ensures faculty consistency

4. ✅ Add FK to FacultyTimetable → Faculty (Issue #2)
   - Effort: 1-2 hours (includes migration)
   - Impact: Prevents orphaned timetables

---

## Conclusion

**Overall Status: ✅ FUNCTIONAL WITH MANAGEABLE GAPS**

The database schema is well-designed for the current timetable generation system. It supports multi-tenancy, has proper indexing, and enforces most critical relationships. However, three medium-severity gaps exist in referential integrity that should be addressed before significant scaling.

**Recommendation**: Proceed with current implementation for MVP. Schedule referential integrity fixes for Phase 2 when adding faculty management features.

---

**Report Generated**: 2025-11-21  
**System**: Timetable Generation System v1.0
