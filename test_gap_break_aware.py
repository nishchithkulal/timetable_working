#!/usr/bin/env python3
"""Test that faculty consecutive gap constraint is integrated - with break-aware checking"""

import sys
sys.path.insert(0, 'c:/Users/91988/timetable_working')

from algorithm import store_section_timetables, get_faculty_for_subject

def test_faculty_gap_constraint_break_aware():
    """Generate timetable and check for violations WITHIN each section, accounting for breaks"""
    
    print("\n" + "=" * 80)
    print("FACULTY CONSECUTIVE GAP CONSTRAINT TEST (Break-Aware)")
    print("=" * 80)
    
    # Test data - simpler
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
    
    # Break periods (periods after which a break occurs)
    break_periods = {2, 4}
    
    def has_break_between(p1, p2):
        """Check if there's a break between period p1 and p2"""
        if p2 != p1 + 1:
            return False  # Not consecutive periods, so definitely has break/gap
        # Check if period p1 is a break period (i.e., a break comes after p1)
        return p1 in break_periods
    
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
        
        print("✅ Timetable generated successfully!")
        
        # Now check for faculty consecutive violations
        print("\n" + "-" * 80)
        print("CHECKING FOR FACULTY CONSECUTIVE TEACHING VIOLATIONS")
        print("Breaks are at: after P2 and after P4 (so P2-P3 and P4-P5 have breaks)")
        print("-" * 80)
        
        days = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri"}
        violations = []
        
        for section, timetable in result.items():
            print(f"\nSection {section}:")
            
            # Build faculty schedule ONLY for subjects in THIS section
            faculty_assignments = {}  # (faculty, day) -> [periods]
            
            for day in range(1, 6):
                for period in range(1, 8):
                    subject = timetable[day][period]
                    if subject and subject != "REMEDIAL":
                        # Check if this subject is in this section's subject list
                        if subject in subjects[section]:
                            faculty = faculties.get(subject)
                            if faculty:
                                key = (faculty, day)
                                if key not in faculty_assignments:
                                    faculty_assignments[key] = []
                                faculty_assignments[key].append(period)
            
            # Check for consecutive teaching periods
            for (faculty, day), periods in faculty_assignments.items():
                periods.sort()
                periods_str = ",".join(str(p) for p in periods)
                print(f"  {faculty:20} on {days[day]:3}: P{periods_str}")
                
                # Check consecutive pairs
                for i in range(len(periods) - 1):
                    p1, p2 = periods[i], periods[i+1]
                    if p2 == p1 + 1:  # Consecutive periods
                        if not has_break_between(p1, p2):
                            # VIOLATION: Consecutive without a break
                            violations.append({
                                'faculty': faculty,
                                'day': days[day],
                                'periods': f"P{p1}-P{p2}",
                                'section': section,
                                'reason': 'no break between them'
                            })
                        else:
                            # OK: There's a break
                            print(f"    -> P{p1}-P{p2} OK (break between them)")
        
        if violations:
            print(f"\n❌ FOUND {len(violations)} VIOLATIONS:")
            for v in violations:
                print(f"   {v['faculty']:20} at {v['day']:3} {v['periods']:8} (Section {v['section']}) - {v['reason']}")
            return False
        else:
            print("\n✅ NO VIOLATIONS FOUND - Faculty gap constraint is working correctly!")
            
            # Print full timetables
            for section in sections:
                print(f"\nTimetable for Section {section}:")
                print("     Mon    Tue    Wed    Thu    Fri")
                for period in range(1, 8):
                    row = f"P{period}: "
                    for day in range(1, 6):
                        subject = result[section][day][period] or "-"
                        if subject == "REMEDIAL":
                            subject = "REM"
                        row += f"{subject[:6]:7}"
                    print(row)
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_faculty_gap_constraint_break_aware()
    print("\n" + "=" * 80)
    if success:
        print("TEST PASSED ✅")
    else:
        print("TEST FAILED ❌")
    print("=" * 80)
    sys.exit(0 if success else 1)
