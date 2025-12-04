#!/usr/bin/env python3
"""Test with subjects that require consecutive placement due to high hours"""

import sys
sys.path.insert(0, '.')

sections = ['A']
subjects_per_section = {
    'A': {
        'MATH': {'hours': 6, 'lab': False, 'last': False},  # 6 hours requires crossing both breaks
        'ENGLISH': {'hours': 4, 'lab': False, 'last': False},
        'CS_LAB': {'hours': 4, 'lab': True, 'last': False},  # 4-hour lab
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

print("Generating timetable with HIGH-HOUR subjects...")
print("Subjects requiring consecutive placement:")
print("  - MATH: 6 hours (needs both P2-P3 and P4-P5 plus 2 more periods)")
print("  - ENGLISH: 4 hours")
print("  - CS_LAB: 4 hours (2-period blocks)\n")

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
print("CONSECUTIVE CONSTRAINT ANALYSIS")
print("="*80)

print("\nAllowed consecutive pairs: P2-P3, P4-P5")
print("\nChecking for violations...\n")

violations_found = False

for day in range(1, algorithm.num_days + 1):
    for period in range(1, algorithm.num_periods):
        subject1 = timetable[day][period]
        subject2 = timetable[day][period + 1]
        
        if subject1 and subject2 and subject1 == subject2:
            info = algorithm.subjects_per_section['A'].get(subject1, {})
            is_lab = info.get('lab', False)
            
            if not is_lab:  # Theory subject
                allowed_pairs = [(2, 3), (4, 5)]
                if (period, period + 1) not in allowed_pairs:
                    print(f"[VIOLATION] {subject1} consecutive at {algorithm.days[day]} P{period}-P{period+1} (NOT ALLOWED)")
                    violations_found = True
                else:
                    print(f"[OK] {subject1} consecutive at {algorithm.days[day]} P{period}-P{period+1} (ALLOWED)")
            else:
                print(f"[OK] {subject1} (lab) consecutive at {algorithm.days[day]} P{period}-P{period+1} (labs allowed)")

if not violations_found:
    print("\n[PASS] No consecutive violations!")
else:
    print("\n[FAIL] Consecutive violations found!")

print("\n" + "="*80)
print("PLACEMENT SUMMARY")
print("="*80)

for subject, hours in counters.items():
    info = algorithm.subjects_per_section['A'].get(subject, {})
    expected = info.get('hours', 0)
    status = "[OK]" if hours == expected else "[FAIL]"
    print(f"{status} {subject}: {hours}/{expected} hours")
