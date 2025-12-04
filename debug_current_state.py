#!/usr/bin/env python3
"""Debug script to check current subject placement"""

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
    print("\nTimetable for Section A:")
    print("Day | P1 | P2 | P3 | P4 | P5 | P6 | P7")
    print("-" * 50)
    for day in range(1, 6):
        row = f" {day}  |"
        for period in range(1, 8):
            subj = result['A'][day][period]
            if subj is None:
                subj = "EMPTY"
            row += f" {subj:10} |"
        print(row)
    
    print("\nCounts:")
    math_count = sum(1 for d in range(1, 6) for p in range(1, 8) if result['A'][d][p] == "MATH")
    english_count = sum(1 for d in range(1, 6) for p in range(1, 8) if result['A'][d][p] == "ENGLISH")
    remedial_count = sum(1 for d in range(1, 6) for p in range(1, 8) if result['A'][d][p] == "REMEDIAL")
    empty_count = sum(1 for d in range(1, 6) for p in range(1, 8) if result['A'][d][p] is None)
    
    print(f"MATH: {math_count}/4")
    print(f"ENGLISH: {english_count}/4")
    print(f"REMEDIAL: {remedial_count}/8")
    print(f"EMPTY: {empty_count}")
    print(f"TOTAL: {math_count + english_count + remedial_count + empty_count}")
