#!/usr/bin/env python3
"""
Comprehensive test demonstrating faculty consecutive gap constraint is working.

The constraint ensures:
- Faculty members have at least a break-period gap between teaching periods
- With breaks after P2 and P4, valid lab placements are P2-P3 and P4-P5 only
- Theory subjects are placed with proper gaps (checking adjacent faculty classes)
"""

import sys
sys.path.insert(0, 'c:/Users/91988/timetable_working')

from algorithm import store_section_timetables

def test_faculty_gap_constraint():
    """Test faculty consecutive gap constraint with break-aware logic"""
    
    print("\n" + "=" * 80)
    print("FACULTY CONSECUTIVE GAP CONSTRAINT - COMPREHENSIVE TEST")
    print("=" * 80)
    print("\nRequirement: Faculty must have at least 1 gap between teaching periods")
    print("Break Configuration: After P2 and After P4")
    print("Valid lab placements: P2-P3 and P4-P5 (only periods with breaks between them)")
    print("Invalid lab placements: P1-P2, P3-P4, P5-P6, P6-P7 (no breaks between them)")
    
    # Test data
    sections = ['A']
    subjects = {
        'A': {
            'MATH': {'hours': 4, 'lab': False, 'last': False},
            'ENGLISH': {'hours': 2, 'lab': False, 'last': False},
            'SCIENCE_LAB': {'hours': 2, 'lab': True, 'last': False},
            'REMEDIAL': {'hours': 6, 'lab': False, 'last': False},
        },
    }
    
    faculties = {
        'MATH': 'Dr. Smith',
        'ENGLISH': 'Dr. Jones',
        'SCIENCE_LAB': 'Dr. Johnson',
    }
    
    break_config = {
        'first_break_period': 2,
        'lunch_break_period': 4
    }
    
    print("\nTest Data:")
    print(f"  Section A has: MATH (4h), ENGLISH (2h), SCIENCE_LAB (2h lab)")
    print(f"  Faculties: Dr. Smith (MATH), Dr. Jones (ENGLISH), Dr. Johnson (SCIENCE_LAB)")
    
    print("\nGenerating timetable...")
    
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
        
        print("✅ Timetable generated!")
        
        # Analyze the result
        timetable = result['A']
        days = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri"}
        
        print("\nGenerated Timetable for Section A:")
        print("     Mon    Tue    Wed    Thu    Fri")
        for period in range(1, 8):
            row = f"P{period}: "
            for day in range(1, 6):
                subject = timetable[day][period] or "-"
                if subject == "REMEDIAL":
                    subject = "REM"
                row += f"{subject[:6]:7}"
            print(row)
        
        # Check for violations
        print("\n" + "-" * 80)
        print("CONSTRAINT VERIFICATION")
        print("-" * 80)
        
        # Build faculty schedule
        faculty_assignments = {}  # (faculty, day) -> [periods]
        for day in range(1, 6):
            for period in range(1, 8):
                subject = timetable[day][period]
                if subject and subject != "REMEDIAL":
                    faculty = faculties.get(subject)
                    if faculty:
                        key = (faculty, day)
                        if key not in faculty_assignments:
                            faculty_assignments[key] = []
                        faculty_assignments[key].append(period)
        
        violations = []
        break_periods = {2, 4}  # Periods after which breaks occur
        
        print("\nFaculty Teaching Schedule:")
        for (faculty, day), periods in sorted(faculty_assignments.items()):
            periods.sort()
            periods_str = ",".join(str(p) for p in periods)
            print(f"  {faculty:20} on {days[day]:3}: P{periods_str}", end="")
            
            # Check for violations
            for i in range(len(periods) - 1):
                p1, p2 = periods[i], periods[i+1]
                if p2 == p1 + 1:  # Consecutive periods
                    if p1 not in break_periods:
                        # Violation: consecutive without a break
                        violations.append({
                            'faculty': faculty,
                            'day': days[day],
                            'periods': f"P{p1}-P{p2}",
                            'reason': 'no break between them'
                        })
                        print(" ❌ VIOLATION at P{}-P{}".format(p1, p2), end="")
            print()
        
        if violations:
            print(f"\n❌ FOUND {len(violations)} VIOLATIONS:")
            for v in violations:
                print(f"   {v['faculty']:20} {v['day']} {v['periods']} - {v['reason']}")
            return False
        else:
            print("\n✅ NO VIOLATIONS - Constraint is working correctly!")
            
            # Summary
            print("\n" + "=" * 80)
            print("SUMMARY")
            print("=" * 80)
            print("✅ Faculty consecutive gap constraint is WORKING")
            print("✅ All faculty teaching schedules respect the 1-period gap requirement")
            print("✅ Breaks are properly recognized as gaps between teaching periods")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_faculty_gap_constraint()
    sys.exit(0 if success else 1)
