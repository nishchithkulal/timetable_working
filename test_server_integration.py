#!/usr/bin/env python3
"""Test server integration with dynamic break configuration"""

import sys
sys.path.insert(0, 'c:/Users/Nishchith/timetable_working')

from server import get_break_configuration
from algorithm import store_section_timetables, can_place_lab, create_empty_timetable

def test_server_integration():
    """Simulate server calling algorithm with break config from DB"""
    
    print("\n" + "="*70)
    print("SERVER INTEGRATION TEST")
    print("="*70)
    
    # Simulate database break configuration
    mock_break_config = {
        'first_break_period': 2,
        'lunch_break_period': 4
    }
    
    print("\nSimulated Database Break Configuration:")
    print(f"  First break after period: {mock_break_config['first_break_period']}")
    print(f"  Lunch break after period: {mock_break_config['lunch_break_period']}")
    
    # Test data
    sections = ['A']
    subjects = {
        'A': {
            'MATH': {'hours': 2, 'lab': False, 'last': False},
            'CS_LAB': {'hours': 2, 'lab': True, 'last': False},
        }
    }
    faculties = {
        'MATH': 'Dr. Smith',
        'CS_LAB': 'Dr. Jones',
    }
    
    print("\nCalling store_section_timetables with break_config...")
    
    try:
        # This simulates the server call
        result = store_section_timetables(
            section_list=sections,
            subjects_dict=subjects,
            faculty_dict=faculties,
            break_config=mock_break_config
        )
        
        if result:
            print("[SUCCESS] Timetables generated with dynamic break configuration")
            for section, timetable in result.items():
                print(f"\n  Section {section}:")
                for day in range(1, 3):  # Show first 2 days
                    subjects_in_day = [timetable[day][p] for p in range(1, 8) if timetable[day][p]]
                    print(f"    Day {day}: {subjects_in_day}")
        else:
            print("[ERROR] Failed to generate timetables")
            return False
            
        return True
        
    except Exception as e:
        print(f"[ERROR] Exception during generation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_algorithm_state():
    """Verify algorithm global state is correctly updated"""
    
    import algorithm
    
    print("\n" + "="*70)
    print("ALGORITHM STATE TEST")
    print("="*70)
    
    print("\nInitial state:")
    print(f"  first_break_period: {algorithm.first_break_period}")
    print(f"  lunch_break_period: {algorithm.lunch_break_period}")
    
    # Simulate different break configurations
    configs = [
        {'first_break_period': 1, 'lunch_break_period': 3},
        {'first_break_period': 2, 'lunch_break_period': 4},
        {'first_break_period': 3, 'lunch_break_period': 5},
    ]
    
    print("\nTesting different configurations:")
    for i, config in enumerate(configs, 1):
        # Set up minimal test data
        algorithm.sections = ['A']
        algorithm.subjects_per_section = {'A': {}}
        algorithm.faculties = {}
        
        # Call store_section_timetables which updates globals
        # We won't actually run the full algorithm, just check global updates
        store_section_timetables(
            section_list=['A'],
            subjects_dict={'A': {}},
            faculty_dict={},
            break_config=config
        )
        
        print(f"\n  Config {i}: breaks at P{config['first_break_period']}, P{config['lunch_break_period']}")
        print(f"    Algorithm state updated: first={algorithm.first_break_period}, lunch={algorithm.lunch_break_period}")
        
        if (algorithm.first_break_period == config['first_break_period'] and
            algorithm.lunch_break_period == config['lunch_break_period']):
            print(f"    [PASS] Globals updated correctly")
        else:
            print(f"    [FAIL] Globals not updated correctly")
            return False
    
    return True

if __name__ == '__main__':
    print("\n" + "#"*70)
    print("# SERVER INTEGRATION TESTS")
    print("#"*70)
    
    test1 = test_server_integration()
    test2 = test_algorithm_state()
    
    print("\n" + "="*70)
    if test1 and test2:
        print("[RESULT] ALL INTEGRATION TESTS PASSED")
    else:
        print("[RESULT] SOME INTEGRATION TESTS FAILED")
    print("="*70)
