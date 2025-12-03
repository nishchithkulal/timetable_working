#!/usr/bin/env python3
"""Comprehensive test of dynamic break configuration"""

import sys
sys.path.insert(0, 'c:/Users/Nishchith/timetable_working')

from algorithm import can_place_lab, create_empty_timetable
import algorithm

def test_break_scenarios():
    """Test different break scenarios"""
    
    scenarios = [
        {'name': 'Standard (breaks at P2, P4)', 'first': 2, 'lunch': 4},
        {'name': 'Early breaks (breaks at P1, P3)', 'first': 1, 'lunch': 3},
        {'name': 'Late breaks (breaks at P3, P5)', 'first': 3, 'lunch': 5},
        {'name': 'Wide breaks (breaks at P1, P5)', 'first': 1, 'lunch': 5},
    ]
    
    for scenario in scenarios:
        print("\n" + "="*70)
        print(f"SCENARIO: {scenario['name']}")
        print(f"Breaks at periods: {scenario['first']}, {scenario['lunch']}")
        print("="*70)
        
        # Set up the algorithm state
        algorithm.first_break_period = scenario['first']
        algorithm.lunch_break_period = scenario['lunch']
        algorithm.num_periods = 7
        algorithm.subjects_per_section = {
            'A': {'TEST_LAB': {'hours': 2, 'lab': True, 'last': False}}
        }
        
        timetable = create_empty_timetable()
        section = 'A'
        subject = 'TEST_LAB'
        day = 1
        
        print("\nLab placement possibilities:")
        valid_count = 0
        invalid_count = 0
        
        for period in range(1, 8):
            can_place = can_place_lab(timetable, subject, section, day, period, 2)
            
            reason = ""
            if period in [scenario['first'], scenario['lunch']]:
                reason = f"[BREAK AT P{period}]"
                invalid_count += 1
            elif period == 7:
                reason = "[NO ROOM FOR 2 PERIODS]"
                invalid_count += 1
            else:
                reason = "[OK - NO BREAK BETWEEN]"
                if can_place:
                    valid_count += 1
                else:
                    invalid_count += 1
            
            status = "VALID  " if can_place else "INVALID"
            print(f"  P{period}-P{period+1}: {status} {reason}")
        
        print(f"\nValid placements: {valid_count}")
        print(f"Invalid placements: {invalid_count}")

def test_verify_lab_integrity():
    """Test the verify_lab_integrity function"""
    from algorithm import verify_lab_integrity, subjects_per_section
    
    print("\n" + "="*70)
    print("TESTING VERIFY_LAB_INTEGRITY WITH DYNAMIC BREAKS")
    print("="*70)
    
    # Set up with breaks at P2 and P4
    algorithm.first_break_period = 2
    algorithm.lunch_break_period = 4
    algorithm.num_periods = 7
    
    # Create test section with labs
    test_subjects = {
        'A': {
            'PHYSICS_LAB': {'hours': 2, 'lab': True, 'last': False},
            'CHEM_LAB': {'hours': 4, 'lab': True, 'last': False}
        }
    }
    algorithm.subjects_per_section = test_subjects
    
    # Valid placement: PHYSICS_LAB at P1-P2 (doesn't cross break)
    valid_timetable = create_empty_timetable()
    valid_timetable[1][1] = 'PHYSICS_LAB'
    valid_timetable[1][2] = 'PHYSICS_LAB'
    # CHEM_LAB at P5-P6-P7 and P1... wait, this won't work for integrity check
    # Let's just test the first lab
    
    print("\nTest 1: Valid lab placement P1-P2 (breaks at P2, P4)")
    result1 = verify_lab_integrity('A', valid_timetable)
    print(f"  Result: {'PASS' if result1 else 'FAIL'}")
    
    # Invalid placement: PHYSICS_LAB at P2-P3 (crosses break at P2)
    invalid_timetable = create_empty_timetable()
    invalid_timetable[1][2] = 'PHYSICS_LAB'
    invalid_timetable[1][3] = 'PHYSICS_LAB'
    
    print("\nTest 2: Invalid lab placement P2-P3 (break crosses at P2)")
    result2 = verify_lab_integrity('A', invalid_timetable)
    print(f"  Result: {'PASS' if not result2 else 'FAIL'}")
    
    # Another valid: P3-P4 (doesn't cross break)
    valid_timetable2 = create_empty_timetable()
    valid_timetable2[1][3] = 'PHYSICS_LAB'
    valid_timetable2[1][4] = 'PHYSICS_LAB'
    
    print("\nTest 3: Valid lab placement P3-P4 (breaks at P2, P4)")
    result3 = verify_lab_integrity('A', valid_timetable2)
    print(f"  Result: {'PASS' if result3 else 'FAIL'}")

if __name__ == '__main__':
    print("\n" + "#"*70)
    print("# COMPREHENSIVE BREAK CONFIGURATION TEST")
    print("#"*70)
    
    test_break_scenarios()
    test_verify_lab_integrity()
    
    print("\n" + "="*70)
    print("TESTING COMPLETE")
    print("="*70)
