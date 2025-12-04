#!/usr/bin/env python3
"""Debug why MATH is not being placed"""

import sys
sys.path.insert(0, 'c:/Users/91988/timetable_working')

import algorithm

# Patch to see what happens when we try to place MATH/ENGLISH
original_insertion = algorithm.insertion_algorithm

def debug_insertion(section, all_timetables):
    print(f"\n[INSERTION] Starting insertion for {section}")
    
    # Manually trace through the algorithm
    timetable = algorithm.create_empty_timetable()
    counters = {subj: 0 for subj in algorithm.subjects_per_section[section]}
    faculty_schedule = algorithm.get_faculty_schedule(all_timetables)
    
    subjects_to_place = [s for s, info in algorithm.subjects_per_section[section].items() if s != "REMEDIAL"]
    print(f"Subjects to place: {subjects_to_place}")
    
    regular_periods = [p for p in range(1, 8)]
    
    # Try to place first subject on first day
    day = 1
    period = 1
    
    if timetable[day][period] is None and not algorithm.is_locked_cell(section, day, period):
        for subject in subjects_to_place[:1]:  # Just try MATH
            info = algorithm.subjects_per_section[section][subject]
            if counters[subject] >= info["hours"]:
                print(f"  {subject}: already has enough hours ({counters[subject]} >= {info['hours']})")
                continue
            
            is_lab = info["lab"]
            faculty = algorithm.get_faculty_for_subject(section, subject)
            print(f"  Trying {subject} ({faculty}, lab={is_lab}) at {day}P{period}")
            
            if is_lab:
                print(f"    Is lab - checking if period+1 exceeds bounds")
                if period + 1 > algorithm.num_periods:
                    print(f"    SKIP: period+1 > num_periods")
                    continue
            else:
                # Theory subject
                print(f"    Is theory subject")
                # Check if cell occupied
                if timetable[day][period] is not None:
                    print(f"    SKIP: cell already occupied")
                    continue
                
                # Temp place for consecutive constraint check
                old_val = timetable[day][period]
                timetable[day][period] = subject
                
                consecutive_ok = algorithm.check_consecutive_constraint(timetable, subject, day, period, False)
                print(f"    Consecutive constraint: {consecutive_ok}")
                
                if consecutive_ok:
                    hard_conflict = algorithm.check_faculty_conflict(faculty, section, day, period, faculty_schedule)
                    print(f"    Faculty conflict: {hard_conflict}")
                    
                    if not hard_conflict:
                        gap_ok = algorithm.check_faculty_consecutive_gap(faculty, day, period, timetable)
                        print(f"    Faculty gap constraint: {gap_ok}")
                        
                        if gap_ok:
                            soft_conflict = algorithm.check_faculty_overload_soft_constraint(faculty, section, day, timetable)
                            print(f"    Soft constraint: {soft_conflict}")
                        else:
                            timetable[day][period] = old_val
                    else:
                        timetable[day][period] = old_val
                else:
                    timetable[day][period] = old_val
    
    # Now call the real function
    return original_insertion(section, all_timetables)

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
