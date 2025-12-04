#!/usr/bin/env python3
"""Debug why P1-P2 is still being placed"""

import sys
sys.path.insert(0, 'c:/Users/91988/timetable_working')

# Patch the functions to add debug
import algorithm

original_insertion = algorithm.insertion_algorithm

def debug_insertion_algorithm(section, all_timetables):
    """Wrap insertion_algorithm to debug lab placement"""
    # Call original with monkeypatch for debugging
    
    # Store original can_place_lab
    original_can_place = algorithm.can_place_lab
    
    call_count = [0]
    
    def debug_can_place_lab(timetable, subject, section, day, period, slots_needed):
        result = original_can_place(timetable, subject, section, day, period, slots_needed)
        call_count[0] += 1
        if call_count[0] <= 3 and day == 1 and period <= 3:  # Only debug Monday, early periods, first few calls
            print(f"  [can_place_lab] {subject} at Mon P{period}: {result}")
        return result
    
    algorithm.can_place_lab = debug_can_place_lab
    
    # Store original get_first_break_period
    original_first_break = algorithm.get_first_break_period
    original_lunch_break = algorithm.get_lunch_break_period
    
    def debug_first_break():
        result = original_first_break()
        print(f"  [DEBUG] get_first_break_period() = {result}")
        return result
    
    def debug_lunch_break():
        result = original_lunch_break()
        print(f"  [DEBUG] get_lunch_break_period() = {result}")
        return result
    
    # Don't monkeypatch the breaks every call, just once
    print(f"\n  Break config: first_break={algorithm.get_first_break_period()}, lunch_break={algorithm.get_lunch_break_period()}")
    
    result = original_insertion(section, all_timetables)
    
    algorithm.can_place_lab = original_can_place
    return result

algorithm.insertion_algorithm = debug_insertion_algorithm

# Run
from algorithm import store_section_timetables

sections = ['A']
subjects = {
    'A': {
        'MATH': {'hours': 4, 'lab': False, 'last': False},
        'PHYSICS_LAB': {'hours': 2, 'lab': True, 'last': False},
        'REMEDIAL': {'hours': 6, 'lab': False, 'last': False},
    },
}

faculties = {
    'MATH': 'Dr. Smith',
    'PHYSICS_LAB': 'Dr. Johnson',
}

break_config = {
    'first_break_period': 2,
    'lunch_break_period': 4
}

print("\nGenerating with debug output...")
result = store_section_timetables(
    section_list=sections,
    subjects_dict=subjects,
    faculty_dict=faculties,
    break_config=break_config
)

if result:
    print("\n✅ Generated")
    print("\nResult for Section A:")
    print("     Mon    Tue    Wed    Thu    Fri")
    for period in range(1, 8):
        row = f"P{period}: "
        for day in range(1, 6):
            subject = result['A'][day][period] or "-"
            if subject == "REMEDIAL":
                subject = "REM"
            row += f"{subject[:6]:7}"
        print(row)
