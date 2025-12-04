#!/usr/bin/env python3
"""Test with multiple sections to test cross-section faculty conflicts"""

import sys
sys.path.insert(0, '.')

# Set up test data with TWO sections
sections = ['A', 'B']
subjects_per_section = {
    'A': {
        'MATH': {'hours': 2, 'lab': False, 'last': False},
        'ENGLISH': {'hours': 2, 'lab': False, 'last': False},
        'CS_LAB': {'hours': 2, 'lab': True, 'last': False},
        'REMEDIAL': {'hours': 1, 'lab': False, 'last': False}
    },
    'B': {
        'PHYSICS': {'hours': 2, 'lab': False, 'last': False},
        'CHEMISTRY': {'hours': 2, 'lab': False, 'last': False},
        'BIO_LAB': {'hours': 2, 'lab': True, 'last': False},
        'REMEDIAL': {'hours': 1, 'lab': False, 'last': False}
    }
}

# Dr. Smith teaches MATH in Section A and PHYSICS in Section B
faculties = {
    'MATH': 'Dr. Smith',
    'ENGLISH': 'Dr. Johnson',
    'CS_LAB': 'Dr. Jones',
    'PHYSICS': 'Dr. Smith',  # SAME FACULTY as MATH
    'CHEMISTRY': 'Dr. Williams',
    'BIO_LAB': 'Dr. Brown',
    'REMEDIAL': 'Dr. Admin'
}

# Import and set up algorithm
import algorithm

# Set global variables in algorithm
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

# Generate timetables for both sections
print("Generating timetables for Sections A and B...")
print("Note: Dr. Smith teaches MATH in Section A and PHYSICS in Section B")
print("      This tests if cross-section faculty conflict detection works\n")

all_timetables = {}
all_counters = {}

for section in sections:
    print(f"\n{'='*80}")
    print(f"Processing Section {section}")
    print(f"{'='*80}")
    
    timetable, counters = algorithm.insertion_algorithm(section, all_timetables)
    timetable, counters, success = algorithm.smart_optimize(section, timetable, counters, all_timetables)
    all_timetables[section] = timetable
    all_counters[section] = counters
    
    print(f"\nSection {section} timetable:")
    for day in range(1, algorithm.num_days + 1):
        print(f"\n  {algorithm.days[day]}:")
        has_subject = False
        for period in range(1, algorithm.num_periods + 1):
            subject = timetable[day][period]
            if subject and subject != 'REMEDIAL':
                has_subject = True
                faculty = algorithm.faculties.get(subject, "Unknown")
                print(f"    P{period}: {subject} (Faculty: {faculty})")
        if not has_subject:
            print("    (no theory classes)")

# Check for CROSS-SECTION violations
print("\n" + "="*80)
print("CROSS-SECTION VIOLATION CHECK")
print("="*80)

violations_found = False

# Build global faculty schedule across all sections
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
                        # Faculty is already teaching at this period in another section!
                        prev_section, prev_subject = global_faculty_schedule[key]
                        print(f"\nVIOLATION: Faculty {faculty} is scheduled at {algorithm.days[day]} P{period} in MULTIPLE SECTIONS!")
                        print(f"  Section {prev_section}: {prev_subject}")
                        print(f"  Section {section}: {subject}")
                        violations_found = True
                    else:
                        global_faculty_schedule[key] = (section, subject)

if not violations_found:
    print("\n[OK] No cross-section faculty conflicts found!")
else:
    print("\n[FAIL] Cross-section violations detected!")

print(f"\nPlacement summary:")
for section in sections:
    print(f"\nSection {section}:")
    for subject, hours in all_counters[section].items():
        info = algorithm.subjects_per_section[section].get(subject, {})
        expected = info.get('hours', 0)
        status = "[OK]" if hours == expected else "[FAIL]"
        print(f"  {status} {subject}: {hours}/{expected} hours placed")
