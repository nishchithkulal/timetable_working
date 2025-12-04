#!/usr/bin/env python3
"""Test to check for consecutive theory subject violations"""

import sys
sys.path.insert(0, '.')

# Set up test data
sections = ['A', 'B']
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
    }
}

faculties = {
    'MATH': 'Dr. Smith',
    'ENGLISH': 'Dr. Johnson',
    'CS_LAB': 'Dr. Jones',
    'PHYSICS': 'Dr. Brown',
    'CHEMISTRY': 'Dr. Williams',
    'BIO_LAB': 'Dr. Lee',
    'REMEDIAL': 'Dr. Admin'
}

# Import algorithm
import algorithm

# Set up algorithm globals
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

print("Generating timetables...")
print("Configuration:")
print("  Breaks at P2 and P4")
print("  Non-labs can ONLY be consecutive at P2-P3 and P4-P5 (crossing breaks)")
print("  Non-labs CANNOT be consecutive at P1-P2, P3-P4, P5-P6, P6-P7\n")

all_timetables = {}
all_counters = {}

for section in sections:
    timetable, counters = algorithm.insertion_algorithm(section, all_timetables)
    timetable, counters, success = algorithm.smart_optimize(section, timetable, counters, all_timetables)
    all_timetables[section] = timetable
    all_counters[section] = counters

print("\n" + "="*80)
print("CONSECUTIVE CONSTRAINT CHECK")
print("="*80)

violations_found = False

# Check each section for consecutive violations
for section in sections:
    print(f"\nSection {section}:")
    timetable = all_timetables[section]
    
    for day in range(1, algorithm.num_days + 1):
        for period in range(1, algorithm.num_periods):
            subject1 = timetable[day][period]
            subject2 = timetable[day][period + 1]
            
            # Check if same subject appears consecutively
            if subject1 and subject2 and subject1 == subject2:
                # Get subject info
                info = algorithm.subjects_per_section[section].get(subject1, {})
                is_lab = info.get('lab', False)
                
                if not is_lab:  # Only check theory subjects
                    # Check if this is an allowed consecutive pair
                    allowed_pairs = [(2, 3), (4, 5)]  # Crossing breaks
                    
                    if (period, period + 1) not in allowed_pairs:
                        print(f"  [VIOLATION] {subject1} appears consecutively at {algorithm.days[day]} P{period}-P{period+1} (NOT allowed)")
                        violations_found = True
                    else:
                        print(f"  [OK] {subject1} appears consecutively at {algorithm.days[day]} P{period}-P{period+1} (allowed - crossing break)")
                        
                        # Also show what subjects are around it
                        before = timetable[day][period-1] if period > 1 else "N/A"
                        after = timetable[day][period+2] if period+2 <= algorithm.num_periods else "N/A"
                        print(f"       Context: {before} -> {subject1} -> {subject1} -> {after}")

if not violations_found:
    print("\n[OK] No consecutive theory violations found!")
else:
    print("\n[FAIL] Consecutive theory violations detected!")

print("\n" + "="*80)
print("COMPLETE TIMETABLE VIEW")
print("="*80)

for section in sections:
    print(f"\nSection {section}:")
    timetable = all_timetables[section]
    
    for day in range(1, algorithm.num_days + 1):
        print(f"  {algorithm.days[day]}: ", end="")
        for period in range(1, algorithm.num_periods + 1):
            subject = timetable[day][period]
            if subject:
                print(f"P{period}={subject[:3]} ", end="")
        print()
