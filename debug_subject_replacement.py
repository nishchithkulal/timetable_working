#!/usr/bin/env python3
"""Debug why subjects are being replaced with remedials"""

import sys
sys.path.insert(0, 'c:/Users/91988/timetable_working')

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

if result:
    print("Timetable:")
    print("     Mon    Tue    Wed    Thu    Fri")
    for period in range(1, 8):
        row = f"P{period}: "
        for day in range(1, 6):
            subject = result['A'][day][period] or "-"
            row += f"{subject[:6]:7}"
        print(row)
    
    # Count subjects
    math_count = sum(1 for d in range(1, 6) for p in range(1, 8) if result['A'][d][p] == "MATH")
    english_count = sum(1 for d in range(1, 6) for p in range(1, 8) if result['A'][d][p] == "ENGLISH")
    remedial_count = sum(1 for d in range(1, 6) for p in range(1, 8) if result['A'][d][p] == "REMEDIAL")
    
    print(f"\nCounts: MATH={math_count} (expected 4), ENGLISH={english_count} (expected 4), REMEDIAL={remedial_count} (expected 8)")
    
    if math_count < 4 or english_count < 4:
        print("❌ ISSUE: Subjects replaced with remedials!")
    else:
        print("✅ All subjects placed correctly")
