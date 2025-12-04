#!/usr/bin/env python3
"""Test original working version"""

import sys
sys.path.insert(0, 'c:/Users/91988/timetable_working')

from algorithm import store_section_timetables

# Test case
sections = ['A']
subjects = {
    'A': {
        'MATH': {'hours': 4, 'lab': False, 'last': False},
        'ENGLISH': {'hours': 4, 'lab': False, 'last': False},
        'REMEDIAL': {'hours': 8, 'lab': False, 'last': False},
    },
}

faculties = {
    'MATH': 'Dr. Smith',
    'ENGLISH': 'Dr. Jones',
}

result = store_section_timetables(
    section_list=sections,
    subjects_dict=subjects,
    faculty_dict=faculties,
    break_config={'first_break_period': 2, 'lunch_break_period': 4}
)

if result:
    math_count = sum(1 for d in range(1, 6) for p in range(1, 8) if result['A'][d][p] == "MATH")
    english_count = sum(1 for d in range(1, 6) for p in range(1, 8) if result['A'][d][p] == "ENGLISH")
    remedial_count = sum(1 for d in range(1, 6) for p in range(1, 8) if result['A'][d][p] == "REMEDIAL")
    
    print("\nCounts:")
    print(f"MATH: {math_count}/4")
    print(f"ENGLISH: {english_count}/4")
    print(f"REMEDIAL: {remedial_count}/8")
