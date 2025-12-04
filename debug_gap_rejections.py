#!/usr/bin/env python3
"""Debug the gap constraint rejections"""

import sys
sys.path.insert(0, 'c:/Users/91988/timetable_working')

import algorithm

# Patch to see rejections
original_check_gap = algorithm.check_faculty_consecutive_gap
call_count = [0]
rejection_count = [0]

def debug_check_gap(faculty, day, period, timetable):
    result = original_check_gap(faculty, day, period, timetable)
    call_count[0] += 1
    if not result:
        rejection_count[0] += 1
        if rejection_count[0] <= 10:  # Only print first 10
            faculty_periods = []
            for check_period in range(1, 8):
                subject_at_period = timetable[day][check_period]
                if subject_at_period and subject_at_period != "REMEDIAL":
                    for section in ["A"]:
                        try:
                            subject_faculty = algorithm.get_faculty_for_subject(section, subject_at_period)
                            if subject_faculty == faculty:
                                faculty_periods.append(check_period)
                                break
                        except:
                            pass
            print(f"  [GAP REJECT] {faculty} P{period}: already teaching at {faculty_periods}")
    return result

algorithm.check_faculty_consecutive_gap = debug_check_gap

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

print("Running with gap constraint debug...\n")

result = store_section_timetables(
    section_list=sections,
    subjects_dict=subjects,
    faculty_dict=faculties,
    break_config=break_config
)

print(f"\n[STATS] Gap constraint checked {call_count[0]} times, rejected {rejection_count[0]}")
print(f"Rejection rate: {100*rejection_count[0]/call_count[0] if call_count[0] > 0 else 0:.1f}%")

if result:
    print("\nFirst section timetable:")
    print("     Mon    Tue    Wed    Thu    Fri")
    for period in range(1, 8):
        row = f"P{period}: "
        for day in range(1, 6):
            subject = result['A'][day][period] or "-"
            row += f"{subject[:6]:7}"
        print(row)
