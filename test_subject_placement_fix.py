#!/usr/bin/env python3
"""Final test to verify subjects are placed correctly and not replaced with remedials"""

import sys
sys.path.insert(0, 'c:/Users/91988/timetable_working')

from algorithm import store_section_timetables

def test_subject_placement():
    """Test that subjects are placed correctly without excessive remedial replacement"""
    
    print("\n" + "=" * 80)
    print("SUBJECT PLACEMENT TEST - Verify No Excessive Remedial Replacement")
    print("=" * 80)
    
    # Test 1: Simple case
    print("\n[TEST 1] Simple case: 2 subjects + remedial")
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
    
    result = store_section_timetables(
        section_list=sections,
        subjects_dict=subjects,
        faculty_dict=faculties,
        break_config={'first_break_period': 2, 'lunch_break_period': 4}
    )
    
    if result:
        math_count = sum(1 for d in range(1, 6) for p in range(1, 8) if result['A'][d][p] == "MATH")
        english_count = sum(1 for d in range(1, 6) for p in range(1, 8) if result['A'][d][p] == "ENGLISH")
        remedial_count = sum(1 for d in range(1, 6) for p in range(1, 8) if result['A'][d][p] == "REMEDIAL")
        
        print(f"  MATH: {math_count}/4", "✅" if math_count == 4 else "❌")
        print(f"  ENGLISH: {english_count}/4", "✅" if english_count == 4 else "❌")
        print(f"  REMEDIAL: {remedial_count}/8", "✅" if remedial_count == 8 else "❌")
        
        if math_count == 4 and english_count == 4 and remedial_count == 8:
            print("  ✅ TEST 1 PASSED")
            test1_pass = True
        else:
            print("  ❌ TEST 1 FAILED")
            test1_pass = False
    else:
        print("  ❌ TEST 1 FAILED - No result")
        test1_pass = False
    
    # Test 2: Complex case with 3 sections
    print("\n[TEST 2] Complex case: 3 sections with multiple subjects")
    sections = ['A', 'B', 'C']
    subjects = {
        'A': {
            'MATH': {'hours': 3, 'lab': False, 'last': False},
            'SCIENCE': {'hours': 2, 'lab': False, 'last': False},
            'ENGLISH': {'hours': 2, 'lab': False, 'last': False},
            'REMEDIAL': {'hours': 5, 'lab': False, 'last': False},
        },
        'B': {
            'MATH': {'hours': 3, 'lab': False, 'last': False},
            'HISTORY': {'hours': 2, 'lab': False, 'last': False},
            'ENGLISH': {'hours': 2, 'lab': False, 'last': False},
            'REMEDIAL': {'hours': 5, 'lab': False, 'last': False},
        },
        'C': {
            'MATH': {'hours': 3, 'lab': False, 'last': False},
            'PE': {'hours': 2, 'lab': False, 'last': False},
            'ART': {'hours': 2, 'lab': False, 'last': False},
            'REMEDIAL': {'hours': 5, 'lab': False, 'last': False},
        },
    }
    
    faculties = {
        'MATH': 'Dr. Smith',
        'SCIENCE': 'Dr. Johnson',
        'HISTORY': 'Dr. Brown',
        'ENGLISH': 'Dr. Jones',
        'PE': 'Dr. Wilson',
        'ART': 'Dr. White',
    }
    
    result = store_section_timetables(
        section_list=sections,
        subjects_dict=subjects,
        faculty_dict=faculties,
        break_config={'first_break_period': 2, 'lunch_break_period': 4}
    )
    
    test2_pass = True
    for section in sections:
        total_hours = 0
        for subj in ['MATH', 'SCIENCE', 'HISTORY', 'ENGLISH', 'PE', 'ART']:
            if subj in subjects[section]:
                hours = sum(1 for d in range(1, 6) for p in range(1, 8) if result[section][d][p] == subj)
                expected = subjects[section][subj]['hours']
                status = "✅" if hours == expected else "❌"
                print(f"  {section} {subj}: {hours}/{expected} {status}")
                if hours != expected:
                    test2_pass = False
        
        remedial_hours = sum(1 for d in range(1, 6) for p in range(1, 8) if result[section][d][p] == "REMEDIAL")
        expected_remedial = subjects[section]['REMEDIAL']['hours']
        status = "✅" if remedial_hours == expected_remedial else "❌"
        print(f"  {section} REMEDIAL: {remedial_hours}/{expected_remedial} {status}")
        if remedial_hours != expected_remedial:
            test2_pass = False
    
    if test2_pass:
        print("  ✅ TEST 2 PASSED")
    else:
        print("  ❌ TEST 2 FAILED")
    
    # Summary
    print("\n" + "=" * 80)
    if test1_pass and test2_pass:
        print("✅ ALL TESTS PASSED - Subjects are correctly placed without excessive remedials")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        return False

if __name__ == '__main__':
    success = test_subject_placement()
    sys.exit(0 if success else 1)
