# Constraints Implementation Summary

## Overview
Complete database-driven constraint management system has been implemented with persistent storage, dynamic UI, and full algorithm integration.

## Database Changes

### SubjectConstraint Model (Already Existed)
Located in `app/models/database.py`, stores:
- `id`: Primary key
- `college_id`: Foreign key to Admin
- `dept_name`: Department name
- `section`: Section identifier (A, B, C, etc.)
- `subject`: Subject name
- `day`: Day number (1-5 for Mon-Fri)
- `period`: Period number (1-7)
- `constraint_type`: "strict" or "forbidden"
- `created_at`: Timestamp

Unique constraint ensures no duplicate constraints per college/dept/section/subject/day/period/type.

## Backend API Endpoints

### 1. POST `/add-constraint`
Adds a single constraint to the database.

**Request Body:**
```json
{
    "college_id": "C-123",
    "dept_name": "CSD",
    "section": "A",
    "subject": "MATHS",
    "day": 1,
    "period": 1,
    "constraint_type": "strict"
}
```

**Response:** `201 Created` with constraint ID
```json
{
    "ok": true,
    "constraint_id": 42
}
```

### 2. DELETE `/delete-constraint/<id>`
Removes a specific constraint by ID.

**Response:** `200 OK`
```json
{
    "ok": true
}
```

### 3. GET `/get-constraints-for-dept`
Fetches all constraints for a department, optionally filtered by section.

**Query Parameters:**
- `college_id` (required)
- `dept_name` (required)
- `section` (optional)

**Response:** `200 OK`
```json
{
    "ok": true,
    "strict": [
        {
            "id": 1,
            "section": "A",
            "subject": "MATHS",
            "day": 1,
            "period": 1
        }
    ],
    "forbidden": [
        {
            "id": 2,
            "section": "A",
            "subject": "PHYSICS",
            "day": 2,
            "period": 2
        }
    ]
}
```

## Algorithm Integration

### Function Signature Update
Modified `store_section_timetables()` in `algorithm.py`:

```python
def store_section_timetables(
    section_list=None, 
    subjects_dict=None, 
    faculty_dict=None,
    strict_constraints=None,
    forbidden_constraints=None
)
```

### Constraint Format
Constraints are passed as dictionaries with this structure:

**Strict Placements (Fixed):**
```python
strict_constraints = {
    "A": {
        "MATHS": [(1, 1), (3, 2)],      # Day 1 Period 1, Day 3 Period 2
        "PHYSICS": [(2, 3), (4, 4)]     # Day 2 Period 3, Day 4 Period 4
    },
    "B": { ... }
}
```

**Forbidden Placements (Not Allowed):**
```python
forbidden_constraints = {
    "A": {
        "CHEMISTRY": [(5, 6), (5, 7)],  # Cannot assign on Friday P6 or P7
        "BIOLOGY": [(1, 1), (1, 2)]     # Cannot assign on Monday P1 or P2
    },
    "B": { ... }
}
```

### Database to Algorithm Conversion
New function in `server.py`:

```python
def build_constraints_from_db(dept_name: str, college_id: str):
    """
    Fetch constraints from database and build the constraint dictionaries
    in the format expected by the algorithm.
    """
```

This function:
1. Queries all constraints for a department
2. Organizes them by section, subject, and placement
3. Returns (strict_constraints, forbidden_constraints) tuples
4. Returns empty dicts if no constraints found

## Frontend UI in admin_dashboard.html

### Constraint Management Card
Located after "Generate Timetable" card:
- Select Department dropdown
- Select Section dropdown (appears after dept selection)
- Constraint type selector (Strict/Forbidden)
- Subject dropdown (auto-populated from selected dept)
- Day selector (Mon-Fri, numeric 1-5)
- Period selector (P1-P7)
- Add Constraint button
- Display lists for existing constraints with delete buttons

### Features
✅ Cascading dropdowns (Dept → Section, Dept → Subject)
✅ Real-time constraint display
✅ Delete constraints with confirmation
✅ Visual organization (blue for strict, red for forbidden)
✅ Inline delete buttons for each constraint
✅ Form validation
✅ Success/error messages

### JavaScript Functions
- `onConstraintDeptChange()`: Load sections when dept selected
- `loadSubjectsForDept()`: Populate subject dropdown
- `loadConstraintsForSection()`: Fetch existing constraints
- `displayConstraints()`: Render constraint lists
- `addConstraint()`: Save new constraint to DB
- `deleteConstraint()`: Remove constraint from DB

## Timetable Generation Flow

1. **Admin selects department** in "Generate Timetable" section
2. **Constraints can be managed** in "Manage Constraints" section
3. **Generate button clicked** → POST `/generate-timetable`
4. **Backend function flow:**
   - `build_timetable_data_from_db()` - Fetch subjects/faculty
   - `build_constraints_from_db()` - **NEW** - Fetch constraints
   - `store_section_timetables()` with all parameters including constraints
   - Algorithm respects constraints during generation
5. **Timetables stored and displayed**

## Day/Period Numbering System

- **Days**: 1=Monday, 2=Tuesday, 3=Wednesday, 4=Thursday, 5=Friday
- **Periods**: 1-7 (teaching periods only, breaks are handled internally)
- **Format in DB**: Numeric (1-5 for days, 1-7 for periods)
- **Display**: Human-readable names in UI (Monday, Period 1, etc.)

## Data Flow Diagram

```
admin_dashboard.html
    ↓
POST /add-constraint → SubjectConstraint table
GET /get-constraints-for-dept ← SubjectConstraint table
DELETE /delete-constraint ← SubjectConstraint table
    ↓
POST /generate-timetable
    ↓
build_constraints_from_db() → {strict: {...}, forbidden: {...}}
    ↓
store_section_timetables(..., strict_constraints, forbidden_constraints)
    ↓
Algorithm respects constraints during generation
    ↓
SectionTimetable + FacultyTimetable tables updated
```

## Testing Checklist

- [ ] Can add strict constraint (subject on fixed day/period)
- [ ] Can add forbidden constraint (subject blocked from day/period)
- [ ] Constraints display in UI correctly
- [ ] Can delete constraints
- [ ] Timetable generation includes constraint logic
- [ ] Multiple constraints per subject work correctly
- [ ] Different sections have independent constraints
- [ ] Different departments have independent constraints
- [ ] Constraints persist after page reload

## Important Notes

1. **No new database table needed** - Uses existing SubjectConstraint
2. **Backward compatible** - Algorithm works with or without constraints
3. **Day/Period format** - Always numeric in DB and algorithm (1-based indexing)
4. **Cascading deletes** - Removing a department auto-deletes its constraints
5. **Collision detection** - Same constraint can't be added twice
6. **UI updates** - Constraint lists refresh after add/delete operations

## Example Usage

### Adding a Strict Constraint
1. Select Department: "CSD"
2. Select Section: "A"
3. Constraint Type: "Strict (Fixed Placement)"
4. Subject: "MATHS"
5. Day: "Monday" (value=1)
6. Period: "Period 1" (value=1)
7. Click "Add Constraint"
8. Result: MATHS must be scheduled for Section A on Monday Period 1

### Adding a Forbidden Constraint
1. Select Department: "CSD"
2. Select Section: "B"
3. Constraint Type: "Forbidden (Not Allowed)"
4. Subject: "LAB"
5. Day: "Friday" (value=5)
6. Period: "Period 7" (value=7)
7. Click "Add Constraint"
8. Result: LAB cannot be scheduled for Section B on Friday Period 7

## File Changes Summary

| File | Changes |
|------|---------|
| `algorithm.py` | Modified `store_section_timetables()` signature, updated `convert_day_to_index()` for numeric days |
| `server.py` | Added 3 new endpoints, added `build_constraints_from_db()` function, modified `generate-timetable` to use constraints |
| `admin_dashboard.html` | Added constraint management UI card, added 200+ lines of JS for constraint management |
| `app/models/database.py` | No changes (SubjectConstraint already existed) |
