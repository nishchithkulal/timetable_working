#!/usr/bin/env python3
"""Test that faculty consecutive gap constraint is integrated and working"""

import sys
sys.path.insert(0, 'c:/Users/91988/timetable_working')

from algorithm import store_section_timetables, get_faculty_schedule

def test_faculty_gap_constraint():
    """Generate timetable and check for faculty consecutive violations"""
    
    print("\n" + "=" * 80)
    print("FACULTY CONSECUTIVE GAP CONSTRAINT TEST")
    print("=" * 80)
    
    # Test data - three sections with multiple subjects
    sections = ['A', 'B', 'C']
    subjects = {
        'A': {
            'MATH': {'hours': 4, 'lab': False, 'last': False},
            'PHYSICS': {'hours': 2, 'lab': False, 'last': False},
            'PHYSICS_LAB': {'hours': 2, 'lab': True, 'last': False},
            'REMEDIAL': {'hours': 6, 'lab': False, 'last': False},
        },
        'B': {
            'MATH': {'hours': 4, 'lab': False, 'last': False},
            'CHEMISTRY': {'hours': 2, 'lab': False, 'last': False},
            'CHEMISTRY_LAB': {'hours': 2, 'lab': True, 'last': False},
            'REMEDIAL': {'hours': 6, 'lab': False, 'last': False},
        },
        'C': {
            'MATH': {'hours': 4, 'lab': False, 'last': False},
            'BIOLOGY': {'hours': 2, 'lab': False, 'last': False},
            'BIOLOGY_LAB': {'hours': 2, 'lab': True, 'last': False},
            'REMEDIAL': {'hours': 6, 'lab': False, 'last': False},
        },
    }
    
    faculties = {
        'MATH': 'Dr. Smith',
        'PHYSICS': 'Dr. Jones',
        'PHYSICS_LAB': 'Dr. Johnson',
        'CHEMISTRY': 'Dr. Brown',
        'CHEMISTRY_LAB': 'Dr. White',
        'BIOLOGY': 'Dr. Green',
        'BIOLOGY_LAB': 'Dr. Blue',
    }
    
    break_config = {
        'first_break_period': 2,
        'lunch_break_period': 4
    }
    
    print("\nGenerating timetable with faculty consecutive gap constraint...")
    
    try:
        result = store_section_timetables(
            section_list=sections,
            subjects_dict=subjects,
            faculty_dict=faculties,
            break_config=break_config
        )
        
        if not result:
            print("❌ Timetable generation failed!")
            return False
        
        print("✅ Timetable generated successfully!")
        
        # Now check for faculty consecutive violations
        print("\n" + "-" * 80)
        print("CHECKING FOR FACULTY CONSECUTIVE TEACHING VIOLATIONS")
        print("-" * 80)
        
        days = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri"}
        violations = []
        
        for section, timetable in result.items():
            # Build faculty schedule for this section
            faculty_assignments = {}  # (faculty, day) -> [periods]
            
            for day in range(1, 6):
                for period in range(1, 8):
                    subject = timetable[day][period]
                    if subject and subject != "REMEDIAL":
                        # Find faculty for this subject
                        faculty = faculties.get(subject)
                        if faculty:
                            key = (faculty, day)
                            if key not in faculty_assignments:
                                faculty_assignments[key] = []
                            faculty_assignments[key].append(period)
            
            # Check for consecutive teaching periods
            for (faculty, day), periods in faculty_assignments.items():
                periods.sort()
                for i in range(len(periods) - 1):
                    if periods[i+1] == periods[i] + 1:
                        violations.append({
                            'faculty': faculty,
                            'day': days[day],
                            'periods': f"P{periods[i]}-P{periods[i+1]}",
                            'section': section
                        })
        
        if violations:
            print(f"\n❌ FOUND {len(violations)} VIOLATIONS:")
            for v in violations:
                print(f"   {v['faculty']:20} at {v['day']:3} {v['periods']:8} (Section {v['section']})")
            return False
        else:
            print("\n✅ NO VIOLATIONS FOUND - Faculty gap constraint is working!")
            
            # Print sample timetable for verification
            print(f"\nSample timetable for Section A:")
            print("     Mon    Tue    Wed    Thu    Fri")
            for period in range(1, 8):
                row = f"P{period}: "
                for day in range(1, 6):
                    subject = result['A'][day][period] or "-"
                    if subject == "REMEDIAL":
                        subject = "REM"
                    row += f"{subject[:6]:7}"
                print(row)
            
            return True
            
    except Exception as e:
        print(f"❌ Error during generation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_faculty_gap_constraint()
    if success:
        print("\n" + "=" * 80)
        print("TEST PASSED ✅")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("TEST FAILED ❌")
        print("=" * 80)
        sys.exit(1)
