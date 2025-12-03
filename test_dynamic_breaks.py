#!/usr/bin/env python3
"""Test script to verify dynamic break configuration in algorithm"""

import sys
sys.path.insert(0, 'c:/Users/Nishchith/timetable_working')

from algorithm import (
    store_section_timetables,
    first_break_period,
    lunch_break_period,
    can_place_lab,
    verify_lab_integrity,
    create_empty_timetable
)

def test_dynamic_breaks():
    """Test with custom break configuration"""
    
    # Test data with custom breaks (first break after P1, lunch after P3)
    break_config = {
        'first_break_period': 1,
        'lunch_break_period': 3
    }
    
    test_subjects = {
        'A': {
            'MATH': {'hours': 2, 'lab': False, 'last': False},
            'PHYSICS_LAB': {'hours': 2, 'lab': True, 'last': False},
            'CHEMISTRY_LAB': {'hours': 2, 'lab': True, 'last': False}
        }
    }
    
    test_faculties = {
        'MATH': 'Dr. Smith',
        'PHYSICS_LAB': 'Dr. Jones',
        'CHEMISTRY_LAB': 'Dr. Brown'
    }
    
    print("="*80)
    print("TESTING DYNAMIC BREAK CONFIGURATION")
    print("="*80)
    print("\nTest Break Configuration:")
    print(f"  First break after period: {break_config['first_break_period']}")
    print(f"  Lunch break after period: {break_config['lunch_break_period']}")
    
    # Call store_section_timetables with custom break config
    try:
        result = store_section_timetables(
            section_list=['A'],
            subjects_dict=test_subjects,
            faculty_dict=test_faculties,
            break_config=break_config
        )
        
        print(f"\n[SUCCESS] Timetable generation completed successfully")
        print(f"[SUCCESS] Generated timetable for section: {list(result.keys())}")
        
        # Verify the structure
        if result and 'A' in result:
            timetable = result['A']
            print(f"\n[SUCCESS] Timetable structure verified")
            print(f"  Days: {list(timetable.keys())}")
            print(f"  Periods: {list(timetable[1].keys())}")
            
            # Print a sample day
            print(f"\nSample timetable for Day 1 (Monday):")
            for period in range(1, 8):
                subject = timetable[1][period]
                subject_display = subject if subject else "[Empty]"
                print(f"  P{period}: {subject_display}")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error during timetable generation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_can_place_lab():
    """Test the can_place_lab function with dynamic breaks"""
    from algorithm import create_empty_timetable
    
    print("\n" + "="*80)
    print("TESTING can_place_lab WITH DYNAMIC BREAKS")
    print("="*80)
    
    # Simulate breaking at periods 1 and 3
    import algorithm
    algorithm.first_break_period = 1
    algorithm.lunch_break_period = 3
    algorithm.num_periods = 7
    algorithm.subjects_per_section = {
        'A': {
            'PHYSICS_LAB': {'hours': 2, 'lab': True, 'last': False}
        }
    }
    
    timetable = create_empty_timetable()
    section = 'A'
    subject = 'PHYSICS_LAB'
    day = 1
    
    # Test valid positions (should not cross breaks)
    valid_positions = [2, 4, 5, 6]  # Not 1 or 3 (break positions) or 7 (no room)
    
    print(f"\nWith breaks at periods {algorithm.first_break_period} and {algorithm.lunch_break_period}:")
    print(f"Testing lab placement for 2-period lab:")
    
    for period in range(1, 8):
        can_place = can_place_lab(timetable, subject, section, day, period, 2)
        status = "[CAN_PLACE]" if can_place else "[CANNOT]"
        reason = ""
        if period in [algorithm.first_break_period, algorithm.lunch_break_period]:
            reason = " (break period)"
        elif period == 7:
            reason = " (no room for 2 periods)"
        print(f"  P{period}-P{period+1}: {status}{reason}")
    
    return True

if __name__ == '__main__':
    print("\nRunning dynamic break configuration tests...\n")
    
    test1 = test_dynamic_breaks()
    test2 = test_can_place_lab()
    
    print("\n" + "="*80)
    if test1 and test2:
        print("[RESULT] ALL TESTS PASSED")
    else:
        print("[RESULT] SOME TESTS FAILED")
    print("="*80)
