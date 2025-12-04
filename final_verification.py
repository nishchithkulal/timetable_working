#!/usr/bin/env python3
"""Final verification test"""

import sys
sys.path.insert(0, 'c:/Users/91988/timetable_working')

from algorithm import store_section_timetables

# Test with realistic data
sections = ['A', 'B', 'C']
subjects = {
    'A': {
        'MATH': {'hours': 6, 'lab': False, 'last': False},
        'ENGLISH': {'hours': 4, 'lab': False, 'last': False},
        'SCIENCE': {'hours': 4, 'lab': False, 'last': False},
        'REMEDIAL': {'hours': 3, 'lab': False, 'last': False},
    },
    'B': {
        'MATH': {'hours': 5, 'lab': False, 'last': False},
        'HISTORY': {'hours': 4, 'lab': False, 'last': False},
        'PE': {'hours': 3, 'lab': False, 'last': False},
        'REMEDIAL': {'hours': 2, 'lab': False, 'last': False},
    },
    'C': {
        'ENGLISH': {'hours': 4, 'lab': False, 'last': False},
        'ART': {'hours': 4, 'lab': False, 'last': False},
        'MUSIC': {'hours': 3, 'lab': False, 'last': False},
        'REMEDIAL': {'hours': 2, 'lab': False, 'last': False},
    },
}

faculties = {
    'MATH': 'Dr. Smith',
    'ENGLISH': 'Dr. Jones',
    'SCIENCE': 'Dr. Brown',
    'HISTORY': 'Dr. Wilson',
    'PE': 'Dr. White',
    'ART': 'Dr. Green',
    'MUSIC': 'Dr. Blue',
}

print("\n" + "="*70)
print("FINAL VERIFICATION TEST - Timetable Generation")
print("="*70)

result = store_section_timetables(
    section_list=sections,
    subjects_dict=subjects,
    faculty_dict=faculties,
    break_config={'first_break_period': 2, 'lunch_break_period': 4}
)

print("\nResults:\n")

all_pass = True
for section in sections:
    print(f"Section {section}:")
    for subject in sorted(subjects[section].keys()):
        expected_hours = subjects[section][subject]['hours']
        actual_hours = sum(1 for d in range(1, 6) for p in range(1, 8) 
                          if result[section][d][p] == subject)
        match = "PASS" if actual_hours == expected_hours else "FAIL"
        status = "[OK]" if actual_hours == expected_hours else "[FAIL]"
        print(f"  {status} {subject:15} {actual_hours:2}/{expected_hours:2}")
        if actual_hours != expected_hours:
            all_pass = False
    
    # Check for empty slots
    empty_count = sum(1 for d in range(1, 6) for p in range(1, 8) 
                     if result[section][d][p] is None)
    total_slots = 5 * 7
    filled = total_slots - empty_count
    print(f"  {filled}/{total_slots} slots filled, {empty_count} empty\n")

print("="*70)
if all_pass:
    print("[OK] ALL TESTS PASSED - Timetable generation working correctly")
else:
    print("[FAIL] SOME TESTS FAILED")
print("="*70 + "\n")
