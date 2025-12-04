#!/usr/bin/env python3
"""Test to check for violations in generated timetables"""

import sys
sys.path.insert(0, '.')

# Set up test data
sections = ['A']
subjects_per_section = {
    'A': {
        'MATH': {'hours': 2, 'lab': False, 'last': False},
        'ENGLISH': {'hours': 2, 'lab': False, 'last': False},
        'CS_LAB': {'hours': 2, 'lab': True, 'last': False},
        'REMEDIAL': {'hours': 1, 'lab': False, 'last': False}
    }
}
faculties = {
    'MATH': 'Dr. Smith',
    'ENGLISH': 'Dr. Smith',  # Same faculty as Math
    'CS_LAB': 'Dr. Jones',
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

# Generate timetable through full flow
print("Generating timetable for Section A...")
print("Note: All subjects have Dr. Smith for MATH and Dr. Smith for ENGLISH (same faculty)")
print("       This tests if faculty conflict detection works\n")

timetable, counters = algorithm.insertion_algorithm('A', {})
print(f"\nAfter insertion_algorithm:")
print(f"  Counters: {counters}")

timetable, counters, success = algorithm.smart_optimize('A', timetable, counters, {})
print(f"\nAfter smart_optimize:")
print(f"  Counters: {counters}")
print(f"  Success: {success}")

print("\nGenerated timetable:")
for day in range(1, algorithm.num_days + 1):
    print(f"\n{algorithm.days[day]}:")
    has_subject = False
    for period in range(1, algorithm.num_periods + 1):
        subject = timetable[day][period]
        if subject:
            has_subject = True
            faculty = algorithm.faculties.get(subject, "Unknown")
            print(f"  P{period}: {subject} (Faculty: {faculty})")
    if not has_subject:
        print("  (empty)")

# Check for violations
print("\n" + "="*80)
print("VIOLATION CHECK")
print("="*80)

violations_found = False

# Build faculty schedule
faculty_schedule = {}
for day in range(1, algorithm.num_days + 1):
    for period in range(1, algorithm.num_periods + 1):
        subject = timetable[day][period]
        if subject and subject != 'REMEDIAL':
            faculty = algorithm.faculties.get(subject, None)
            if faculty:
                key = ('A', day, period)
                if key in faculty_schedule:
                    # This should never happen - cell is already occupied
                    print(f"ERROR: Cell {algorithm.days[day]} P{period} already has {faculty_schedule[key]}, trying to add {subject}")
                    violations_found = True
                else:
                    faculty_schedule[key] = faculty

# Check for faculty at same period in same section
print("\nChecking for faculty conflicts...")
faculty_periods = {}  # Track which periods each faculty is busy
for (section, day, period), faculty in faculty_schedule.items():
    key = (faculty, day, period)
    if key in faculty_periods:
        print(f"VIOLATION: Faculty {faculty} is scheduled at {algorithm.days[day]} P{period} in multiple subjects!")
        print(f"  Subjects: {faculty_periods[key]} and {timetable[day][period]}")
        violations_found = True
    else:
        faculty_periods[key] = timetable[day][period]

# Check for same subject appearing twice at same period (cell overlap)
print("\nChecking for cell overlaps...")
for day in range(1, algorithm.num_days + 1):
    for period in range(1, algorithm.num_periods + 1):
        subject = timetable[day][period]
        if subject:
            count = sum(1 for d in range(1, algorithm.num_days + 1) for p in range(1, algorithm.num_periods + 1) if timetable[d][p] == subject and d == day and p == period)
            if count > 1:
                print(f"VIOLATION: Subject {subject} appears {count} times at {algorithm.days[day]} P{period}")
                violations_found = True

# Check for consecutive non-lab subjects (outside break-crossing periods)
print("\nChecking consecutive placement violations...")
for day in range(1, algorithm.num_days + 1):
    for period in range(1, algorithm.num_periods):
        subject1 = timetable[day][period]
        subject2 = timetable[day][period + 1]
        
        if subject1 and subject2 and subject1 == subject2:
            # Check if this is an allowed consecutive pair (crossing a break)
            info = algorithm.subjects_per_section.get('A', {}).get(subject1, {})
            if not info.get('lab', False):  # Theory subject
                allowed_pairs = [(2, 3), (4, 5)]
                if (period, period + 1) not in allowed_pairs:
                    print(f"VIOLATION: Theory subject {subject1} is consecutively placed at {algorithm.days[day]} P{period}-P{period+1} (not allowed)")
                    violations_found = True

if not violations_found:
    print("\n[OK] No violations found!")
else:
    print("\n[FAIL] Violations detected!")

print(f"\nPlacement summary:")
for subject, hours in counters.items():
    info = algorithm.subjects_per_section['A'].get(subject, {})
    expected = info.get('hours', 0)
    status = "[OK]" if hours == expected else "[FAIL]"
    print(f"  {status} {subject}: {hours}/{expected} hours placed")
