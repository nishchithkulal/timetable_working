#!/usr/bin/env python3
"""Debug break configuration"""

import sys
sys.path.insert(0, 'c:/Users/91988/timetable_working')

import algorithm

# Call store with test data
from algorithm import store_section_timetables

sections = ['A']
subjects = {
    'A': {
        'MATH': {'hours': 2, 'lab': False, 'last': False},
        'LAB': {'hours': 2, 'lab': True, 'last': False},
        'REMEDIAL': {'hours': 10, 'lab': False, 'last': False},
    },
}

faculties = {
    'MATH': 'Dr. Smith',
    'LAB': 'Dr. Johnson',
}

break_config = {
    'first_break_period': 2,
    'lunch_break_period': 4
}

# Patch to see what breaks are configured
original_insertion = algorithm.insertion_algorithm

def debug_insertion(section, all_timetables):
    print(f"\nDEBUG in insertion_algorithm:")
    print(f"  first_break_period = {algorithm.get_first_break_period()}")
    print(f"  lunch_break_period = {algorithm.get_lunch_break_period()}")
    return original_insertion(section, all_timetables)

algorithm.insertion_algorithm = debug_insertion

result = store_section_timetables(
    section_list=sections,
    subjects_dict=subjects,
    faculty_dict=faculties,
    break_config=break_config
)

print("\n✅ Generated - checking lab placements:")
if result:
    print("\nSection A timetable:")
    print("     Mon    Tue    Wed    Thu    Fri")
    for period in range(1, 8):
        row = f"P{period}: "
        for day in range(1, 6):
            subject = result['A'][day][period] or "-"
            if subject == "REMEDIAL":
                subject = "REM"
            row += f"{subject[:6]:7}"
        print(row)
