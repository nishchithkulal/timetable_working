#!/usr/bin/env python3
"""Debug the faculty gap constraint logic"""

import sys
sys.path.insert(0, 'c:/Users/91988/timetable_working')

# Patch the constraint function to add debug output
import algorithm

original_check = algorithm.check_faculty_consecutive_gap

def debug_check_faculty_consecutive_gap(faculty, day, period, timetable):
    result = original_check(faculty, day, period, timetable)
    # Print debug info for specific case
    if faculty == "Dr. Johnson" and day == 1:  # Monday
        faculty_periods = []
        for check_period in range(1, 8):
            subject = timetable[day][check_period]
            if subject and subject != "REMEDIAL":
                try:
                    for section in ["A", "B", "C"]:
                        subj_fac = algorithm.get_faculty_for_subject(section, subject)
                        if subj_fac == faculty:
                            faculty_periods.append(check_period)
                            break
                except:
                    pass
        print(f"  DEBUG: {faculty} P{period}: faculty_periods={faculty_periods}, result={result}")
    return result

algorithm.check_faculty_consecutive_gap = debug_check_faculty_consecutive_gap

# Also patch check_faculty_at_period
original_check_at = algorithm.check_faculty_at_period

def debug_check_faculty_at_period(faculty, day, period, timetable):
    result = original_check_at(faculty, day, period, timetable)
    if faculty == "Dr. Johnson" and day == 1 and 0 < period <= 8:
        print(f"    DEBUG check_faculty_at_period: {faculty} P{period} = {result}")
    return result

algorithm.check_faculty_at_period = debug_check_faculty_at_period

# Now run the generation
from algorithm import store_section_timetables

sections = ['A', 'B']
subjects = {
    'A': {
        'MATH': {'hours': 4, 'lab': False, 'last': False},
        'PHYSICS_LAB': {'hours': 2, 'lab': True, 'last': False},
        'REMEDIAL': {'hours': 6, 'lab': False, 'last': False},
    },
    'B': {
        'CHEMISTRY': {'hours': 4, 'lab': False, 'last': False},
        'BIOLOGY_LAB': {'hours': 2, 'lab': True, 'last': False},
        'REMEDIAL': {'hours': 6, 'lab': False, 'last': False},
    },
}

faculties = {
    'MATH': 'Dr. Smith',
    'PHYSICS_LAB': 'Dr. Johnson',
    'CHEMISTRY': 'Dr. Brown',
    'BIOLOGY_LAB': 'Dr. Blue',
}

break_config = {
    'first_break_period': 2,
    'lunch_break_period': 4
}

print("\nGenerating timetable with debug output...")
print("=" * 80)

try:
    result = store_section_timetables(
        section_list=sections,
        subjects_dict=subjects,
        faculty_dict=faculties,
        break_config=break_config
    )
    
    if result:
        print("\n✅ Timetable generated")
        # Check what got placed
        for section in ['A']:
            print(f"\nSection {section}:")
            print("     Mon    Tue    Wed    Thu    Fri")
            for period in range(1, 8):
                row = f"P{period}: "
                for day in range(1, 6):
                    subject = result[section][day][period] or "-"
                    if subject == "REMEDIAL":
                        subject = "REM"
                    row += f"{subject[:6]:7}"
                print(row)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
