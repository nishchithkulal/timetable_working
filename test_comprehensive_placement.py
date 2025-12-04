#!/usr/bin/env python3
"""Test to verify all constraints are working"""

import sys
sys.path.insert(0, 'c:/Users/91988/timetable_working')

from algorithm import store_section_timetables

# Comprehensive test
sections = ['A', 'B', 'C']
subjects = {
    'A': {
        'MATH': {'hours': 4, 'lab': False, 'last': False},
        'ENGLISH': {'hours': 4, 'lab': False, 'last': False},
        'REMEDIAL': {'hours': 5, 'lab': False, 'last': False},
    },
    'B': {
        'SCIENCE': {'hours': 3, 'lab': False, 'last': False},
        'HISTORY': {'hours': 2, 'lab': False, 'last': False},
        'REMEDIAL': {'hours': 4, 'lab': False, 'last': False},
    },
    'C': {
        'PE': {'hours': 2, 'lab': False, 'last': False},
        'ART': {'hours': 3, 'lab': False, 'last': False},
        'REMEDIAL': {'hours': 3, 'lab': False, 'last': False},
    },
}

faculties = {
    'MATH': 'Dr. Smith',
    'ENGLISH': 'Dr. Jones',
    'SCIENCE': 'Dr. Brown',
    'HISTORY': 'Dr. Wilson',
    'PE': 'Dr. White',
    'ART': 'Dr. Green',
}

print("\nRunning timetable generation...")
result = store_section_timetables(
    section_list=sections,
    subjects_dict=subjects,
    faculty_dict=faculties,
    break_config={'first_break_period': 2, 'lunch_break_period': 4}
)

print("\n" + "="*60)
print("RESULTS")
print("="*60)

all_pass = True
for section in sections:
    print(f"\nSection {section}:")
    for subject in subjects[section]:
        expected_hours = subjects[section][subject]['hours']
        actual_hours = sum(1 for d in range(1, 6) for p in range(1, 8) 
                          if result[section][d][p] == subject)
        status = "PASS" if actual_hours == expected_hours else "FAIL"
        print(f"  {status}: {subject} = {actual_hours}/{expected_hours}")
        if actual_hours != expected_hours:
            all_pass = False

print("\n" + "="*60)
if all_pass:
    print("ALL SUBJECTS PLACED CORRECTLY")
else:
    print("SOME SUBJECTS FAILED TO PLACE")
print("="*60)
