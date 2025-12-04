#!/usr/bin/env python3
"""Test to demonstrate faculty consecutive class violation"""

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

# BOTH MATH and ENGLISH are taught by Dr. Smith
faculties = {
    'MATH': 'Dr. Smith',
    'ENGLISH': 'Dr. Smith',  # SAME FACULTY
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

print("="*80)
print("FACULTY CONSECUTIVE CLASS VIOLATION TEST")
print("="*80)
print("\nScenario:")
print("  - Dr. Smith teaches both MATH and ENGLISH")
print("  - Requirement: Faculty must have at least 1 gap between classes")
print("  - Violation: Dr. Smith teaching at P3 and P4 consecutively\n")

timetable, counters = algorithm.insertion_algorithm('A', {})
timetable, counters, success = algorithm.smart_optimize('A', timetable, counters, {})

print("\n" + "="*80)
print("TIMETABLE")
print("="*80)

for day in range(1, algorithm.num_days + 1):
    print(f"\n{algorithm.days[day]}:")
    for period in range(1, algorithm.num_periods + 1):
        subject = timetable[day][period]
        faculty = algorithm.faculties.get(subject, 'N/A') if subject else 'N/A'
        print(f"  P{period}: {subject if subject else '(empty)':<12} Faculty: {faculty}")

print("\n" + "="*80)
print("FACULTY CONSECUTIVE CLASS VIOLATION CHECK")
print("="*80)
print("\nRequirement: Faculty must have at least 1 gap between their classes\n")

violations_found = False

# Build faculty schedule for each day
for day in range(1, algorithm.num_days + 1):
    # Get all periods where each faculty teaches
    faculty_periods = {}
    
    for period in range(1, algorithm.num_periods + 1):
        subject = timetable[day][period]
        if subject and subject != 'REMEDIAL':
            faculty = algorithm.faculties.get(subject, None)
            if faculty:
                if faculty not in faculty_periods:
                    faculty_periods[faculty] = []
                faculty_periods[faculty].append(period)
    
    # Check for consecutive periods for each faculty
    for faculty, periods in faculty_periods.items():
        periods_sorted = sorted(periods)
        
        for i in range(len(periods_sorted) - 1):
            gap = periods_sorted[i + 1] - periods_sorted[i]
            
            if gap == 1:  # Consecutive periods (no gap)
                print(f"[VIOLATION] {faculty} teaches at {algorithm.days[day]} P{periods_sorted[i]} and P{periods_sorted[i+1]} (NO GAP)")
                print(f"             Teaching: {timetable[day][periods_sorted[i]]} and {timetable[day][periods_sorted[i+1]]}")
                violations_found = True
            else:
                print(f"[OK] {faculty} at {algorithm.days[day]} P{periods_sorted[i]} and P{periods_sorted[i+1]} (gap of {gap-1} period(s))")

if not violations_found:
    print("\n[PASS] No faculty consecutive class violations!")
else:
    print("\n[FAIL] Faculty consecutive class violations found!")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)

for subject, hours in counters.items():
    info = algorithm.subjects_per_section['A'].get(subject, {})
    expected = info.get('hours', 0)
    status = "[OK]" if hours == expected else "[FAIL]"
    print(f"{status} {subject}: {hours}/{expected} hours")
