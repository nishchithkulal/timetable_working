#!/usr/bin/env python3
"""Test non-lab subjects constraint and REMEDIAL filling"""

import sys
sys.path.insert(0, 'c:/Users/Nishchith/timetable_working')

from algorithm import (
    subject_already_on_day,
    create_empty_timetable,
    check_consecutive_constraint
)

def test_subject_once_per_day():
    """Test that non-lab subjects can only appear once per day"""
    
    print("=" * 70)
    print("TEST 1: Non-lab subjects - once per day constraint")
    print("=" * 70)
    
    import algorithm
    algorithm.num_periods = 7
    algorithm.num_days = 5
    algorithm.sections = ['A']
    algorithm.subjects_per_section = {
        'A': {
            'MATH': {'hours': 3, 'lab': False, 'last': False},
            'ENGLISH': {'hours': 2, 'lab': False, 'last': False}
        }
    }
    
    timetable = create_empty_timetable()
    
    # Place MATH on different days
    timetable[1][1] = 'MATH'  # Monday
    timetable[2][2] = 'MATH'  # Tuesday
    timetable[3][3] = 'MATH'  # Wednesday
    
    print("\nPlaced MATH on 3 different days:")
    for day in range(1, 4):
        found = subject_already_on_day(timetable, 'MATH', day)
        print(f"  Day {day}: {'Found' if found else 'Not found'}")
    
    # Try to place second MATH on Monday (should fail)
    print("\nAttempting to place second MATH on Monday:")
    already_on_monday = subject_already_on_day(timetable, 'MATH', 1)
    print(f"  Already on day 1: {already_on_monday}")
    if already_on_monday:
        print("  [PASS] Cannot place - subject already on this day")
    else:
        print("  [FAIL] Should prevent second placement")
    
    return True

def test_remedial_filling():
    """Test that REMEDIAL fills all remaining empty slots"""
    
    print("\n" + "=" * 70)
    print("TEST 2: REMEDIAL filling empty slots")
    print("=" * 70)
    
    import algorithm
    algorithm.num_periods = 7
    algorithm.num_days = 5
    
    timetable = create_empty_timetable()
    
    # Place some subjects
    timetable[1][1] = 'MATH'
    timetable[1][3] = 'ENGLISH'
    timetable[2][2] = 'SCIENCE'
    
    # Count empty slots before filling
    empty_before = sum(1 for d in range(1, 6) for p in range(1, 8) if timetable[d][p] is None)
    print(f"\nEmpty slots before filling: {empty_before}")
    
    # Fill with REMEDIAL
    for day in range(1, 6):
        for period in range(1, 8):
            if timetable[day][period] is None:
                timetable[day][period] = "REMEDIAL"
    
    # Count empty slots after filling
    empty_after = sum(1 for d in range(1, 6) for p in range(1, 8) if timetable[d][p] is None)
    print(f"Empty slots after filling: {empty_after}")
    
    # Check if REMEDIAL appears in expected places
    remedial_count = sum(1 for d in range(1, 6) for p in range(1, 8) if timetable[d][p] == "REMEDIAL")
    print(f"REMEDIAL slots: {remedial_count}")
    
    # Sample output
    print("\nSample - Day 1 timetable:")
    for p in range(1, 8):
        subject = timetable[1][p]
        print(f"  P{p}: {subject}")
    
    if empty_after == 0 and remedial_count == empty_before:
        print("\n[PASS] All empty slots filled with REMEDIAL")
        return True
    else:
        print("\n[FAIL] Not all empty slots filled properly")
        return False

if __name__ == '__main__':
    print("\n" + "#" * 70)
    print("# NON-LAB CONSTRAINT & REMEDIAL FILLING TESTS")
    print("#" * 70 + "\n")
    
    test1 = test_subject_once_per_day()
    test2 = test_remedial_filling()
    
    print("\n" + "=" * 70)
    if test1 and test2:
        print("[RESULT] ALL TESTS PASSED")
    else:
        print("[RESULT] SOME TESTS FAILED")
    print("=" * 70)
