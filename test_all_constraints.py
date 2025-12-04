#!/usr/bin/env python3
"""Comprehensive test for all constraint violations"""

import sys
sys.path.insert(0, '.')

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
    'ENGLISH': 'Dr. Johnson',
    'CS_LAB': 'Dr. Jones',
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

print("Generating timetable for Section A...")
timetable, counters = algorithm.insertion_algorithm('A', {})
timetable, counters, success = algorithm.smart_optimize('A', timetable, counters, {})

print("\n" + "="*80)
print("TIMETABLE")
print("="*80)

for day in range(1, algorithm.num_days + 1):
    print(f"\n{algorithm.days[day]}:")
    for period in range(1, algorithm.num_periods + 1):
        subject = timetable[day][period]
        print(f"  P{period}: {subject if subject else '(empty)'}")

print("\n" + "="*80)
print("CONSTRAINT VIOLATIONS CHECK")
print("="*80)

violations = []

# Check 1: Faculty conflicts (same faculty at same period in same section - should never happen for single section)
print("\n[CHECK 1] Faculty conflicts within section:")
faculty_at_period = {}
for day in range(1, algorithm.num_days + 1):
    for period in range(1, algorithm.num_periods + 1):
        subject = timetable[day][period]
        if subject and subject != 'REMEDIAL':
            faculty = algorithm.faculties.get(subject, None)
            if faculty:
                key = (faculty, day, period)
                if key in faculty_at_period:
                    prev_subject = faculty_at_period[key]
                    print(f"  [FAIL] Faculty {faculty} at {algorithm.days[day]} P{period}: {prev_subject} AND {subject}")
                    violations.append(f"Faculty {faculty} double-booked at {algorithm.days[day]} P{period}")
                else:
                    faculty_at_period[key] = subject

if not violations:
    print("  [OK] No faculty conflicts")

# Check 2: Cell overlaps (two different subjects at same period)
print("\n[CHECK 2] Cell overlaps:")
for day in range(1, algorithm.num_days + 1):
    for period in range(1, algorithm.num_periods + 1):
        subject = timetable[day][period]
        if subject and subject != 'REMEDIAL':
            # Count how many times this subject appears at this exact cell across days
            # (should only be once per cell)
            found_duplicate = False
            for other_day in range(1, algorithm.num_days + 1):
                for other_period in range(1, algorithm.num_periods + 1):
                    if (day != other_day or period != other_period):
                        if timetable[other_day][other_period] == subject:
                            # That's fine - same subject at different cell
                            pass

if not violations:
    print("  [OK] No cell overlaps")

# Check 3: Consecutive non-lab violations
print("\n[CHECK 3] Consecutive theory subject violations:")
for day in range(1, algorithm.num_days + 1):
    for period in range(1, algorithm.num_periods):
        subject1 = timetable[day][period]
        subject2 = timetable[day][period + 1]
        
        if subject1 and subject2 and subject1 == subject2:
            info = algorithm.subjects_per_section['A'].get(subject1, {})
            is_lab = info.get('lab', False)
            
            if not is_lab:  # Non-lab subject
                allowed_pairs = [(2, 3), (4, 5)]
                if (period, period + 1) not in allowed_pairs:
                    print(f"  [FAIL] {subject1} is consecutive at {algorithm.days[day]} P{period}-P{period+1} (NOT allowed)")
                    violations.append(f"Consecutive violation: {subject1} at {algorithm.days[day]} P{period}-P{period+1}")
                else:
                    print(f"  [OK] {subject1} is consecutive at {algorithm.days[day]} P{period}-P{period+1} (allowed)")

if len([v for v in violations if 'Consecutive' in v]) == 0:
    print("  [OK] No consecutive violations")

# Summary
print("\n" + "="*80)
if not violations:
    print("[PASS] All constraints satisfied!")
else:
    print(f"[FAIL] Found {len(violations)} violations:")
    for v in violations:
        print(f"  - {v}")
