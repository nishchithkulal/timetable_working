#!/usr/bin/env python3
"""Debug remedial filling"""

import sys
sys.path.insert(0, 'c:/Users/91988/timetable_working')

import algorithm

# Patch insertion_algorithm to see what's happening
original_insertion = algorithm.insertion_algorithm

def debug_insertion(section, all_timetables):
    result_timetable, result_counters = original_insertion(section, all_timetables)
    
    print(f"\n[INSERTION RESULT] Section {section}:")
    print(f"  Subject counters: {result_counters}")
    
    # Count cells filled
    filled = sum(1 for d in range(1, 6) for p in range(1, 8) if result_timetable[d][p] is not None)
    empty = 35 - filled
    print(f"  Cells filled: {filled}, empty: {empty}")
    
    # Count by subject
    for subj in ["MATH", "ENGLISH", "REMEDIAL"]:
        count = sum(1 for d in range(1, 6) for p in range(1, 8) if result_timetable[d][p] == subj)
        print(f"  {subj}: {count}")
    
    return result_timetable, result_counters

algorithm.insertion_algorithm = debug_insertion

from algorithm import store_section_timetables

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

break_config = {
    'first_break_period': 2,
    'lunch_break_period': 4
}

result = store_section_timetables(
    section_list=sections,
    subjects_dict=subjects,
    faculty_dict=faculties,
    break_config=break_config
)
