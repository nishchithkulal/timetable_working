#!/usr/bin/env python3
"""Final comprehensive test of all constraints"""

import sys
sys.path.insert(0, '.')

# Multi-section scenario with shared faculty
sections = ['A', 'B', 'C']
subjects_per_section = {
    'A': {
        'MATH': {'hours': 4, 'lab': False, 'last': False},
        'ENGLISH': {'hours': 2, 'lab': False, 'last': False},
        'CS_LAB': {'hours': 2, 'lab': True, 'last': False},
        'REMEDIAL': {'hours': 1, 'lab': False, 'last': False}
    },
    'B': {
        'PHYSICS': {'hours': 4, 'lab': False, 'last': False},
        'CHEMISTRY': {'hours': 2, 'lab': False, 'last': False},
        'BIO_LAB': {'hours': 2, 'lab': True, 'last': False},
        'REMEDIAL': {'hours': 1, 'lab': False, 'last': False}
    },
    'C': {
        'HISTORY': {'hours': 2, 'lab': False, 'last': False},
        'GEOGRAPHY': {'hours': 2, 'lab': False, 'last': False},
        'GEO_LAB': {'hours': 2, 'lab': True, 'last': False},
        'REMEDIAL': {'hours': 1, 'lab': False, 'last': False}
    }
}

# Dr. Smith teaches MATH (A) and PHYSICS (B)
faculties = {
    'MATH': 'Dr. Smith',
    'ENGLISH': 'Dr. Johnson',
    'CS_LAB': 'Dr. Jones',
    'PHYSICS': 'Dr. Smith',  # SHARED
    'CHEMISTRY': 'Dr. Williams',
    'BIO_LAB': 'Dr. Lee',
    'HISTORY': 'Dr. Brown',
    'GEOGRAPHY': 'Dr. Miller',
    'GEO_LAB': 'Dr. Davis',
    'REMEDIAL': 'Dr. Admin'
}

import algorithm
algorithm.sections = sections
algorithm.subjects_per_section = subjects_per_section
algorithm.faculties = faculties
algorithm.strict_subject_placement = {}
algorithm.forbidden_subject_placement = {}
algorithm.break_config_state = {'first': 2, 'lunch': 4}
algorithm.break_periods = {'first': 2, 'lunch': 4}
algorithm.num_days = 5
algorithm.num_periods = 7
algorithm.days = {0: "", 1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri"}
algorithm.num_display_slots = 9

print("="*80)
print("COMPREHENSIVE MULTI-SECTION TIMETABLE GENERATION")
print("="*80)
print("\nScenario:")
print("  - 3 sections (A, B, C)")
print("  - Dr. Smith teaches MATH in Section A and PHYSICS in Section B")
print("  - Testing cross-section faculty conflicts and consecutive violations\n")

all_timetables = {}
all_counters = {}

for section in sections:
    timetable, counters = algorithm.insertion_algorithm(section, all_timetables)
    timetable, counters, success = algorithm.smart_optimize(section, timetable, counters, all_timetables)
    all_timetables[section] = timetable
    all_counters[section] = counters

print("\n" + "="*80)
print("CONSTRAINT VALIDATION")
print("="*80)

all_violations = []

# Check 1: Cross-section faculty conflicts
print("\n[CHECK 1] Cross-section faculty conflicts:")
global_faculty_schedule = {}
for section in sections:
    for day in range(1, algorithm.num_days + 1):
        for period in range(1, algorithm.num_periods + 1):
            subject = all_timetables[section][day][period]
            if subject and subject != 'REMEDIAL':
                faculty = algorithm.faculties.get(subject, None)
                if faculty:
                    key = (faculty, day, period)
                    if key in global_faculty_schedule:
                        prev_section, prev_subject = global_faculty_schedule[key]
                        msg = f"Faculty {faculty} at {algorithm.days[day]} P{period}: Section {prev_section}={prev_subject} AND Section {section}={subject}"
                        print(f"  [FAIL] {msg}")
                        all_violations.append(msg)
                    else:
                        global_faculty_schedule[key] = (section, subject)

if not [v for v in all_violations if 'Faculty' in v]:
    print("  [OK] No cross-section faculty conflicts")

# Check 2: Consecutive theory violations
print("\n[CHECK 2] Consecutive theory violations:")
for section in sections:
    for day in range(1, algorithm.num_days + 1):
        for period in range(1, algorithm.num_periods):
            subject1 = all_timetables[section][day][period]
            subject2 = all_timetables[section][day][period + 1]
            
            if subject1 and subject2 and subject1 == subject2:
                info = algorithm.subjects_per_section[section].get(subject1, {})
                is_lab = info.get('lab', False)
                
                if not is_lab:
                    allowed_pairs = [(2, 3), (4, 5)]
                    if (period, period + 1) not in allowed_pairs:
                        msg = f"Section {section}: {subject1} consecutive at {algorithm.days[day]} P{period}-P{period+1} (NOT allowed)"
                        print(f"  [FAIL] {msg}")
                        all_violations.append(msg)

if not [v for v in all_violations if 'consecutive' in v.lower()]:
    print("  [OK] No consecutive theory violations")

# Check 3: Completion
print("\n[CHECK 3] Timetable completion:")
for section in sections:
    incomplete_subjects = []
    for subject, hours in all_counters[section].items():
        info = algorithm.subjects_per_section[section].get(subject, {})
        expected = info.get('hours', 0)
        if hours < expected:
            incomplete_subjects.append(f"{subject} ({hours}/{expected})")
    
    if incomplete_subjects:
        msg = f"Section {section} incomplete: {', '.join(incomplete_subjects)}"
        print(f"  [FAIL] {msg}")
        all_violations.append(msg)
    else:
        print(f"  [OK] Section {section} 100% complete")

# Summary
print("\n" + "="*80)
if not all_violations:
    print("[PASS] ALL CONSTRAINTS SATISFIED!")
    print("="*80)
    print("\nGenerated Timetables:")
    for section in sections:
        print(f"\nSection {section}:")
        for day in range(1, algorithm.num_days + 1):
            subjects_on_day = [all_timetables[section][day][p] for p in range(1, algorithm.num_periods + 1) if all_timetables[section][day][p] and all_timetables[section][day][p] != 'REMEDIAL']
            if subjects_on_day:
                print(f"  {algorithm.days[day]}: {', '.join(subjects_on_day)}")
else:
    print(f"[FAIL] Found {len(all_violations)} violations:")
    print("="*80)
    for v in all_violations:
        print(f"  - {v}")
