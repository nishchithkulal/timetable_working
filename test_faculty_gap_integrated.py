#!/usr/bin/env python3
"""Test that faculty consecutive gap constraint is integrated and working"""

import sys
sys.path.insert(0, '/c/Users/91988/timetable_working')

from algorithm import generate_timetable
from app.models.database import load_data

# Load data
data = load_data()

print("=" * 80)
print("TESTING FACULTY CONSECUTIVE GAP CONSTRAINT")
print("=" * 80)

# Generate timetable
result = generate_timetable(data)

if result:
    all_timetables, all_counters, all_data = result
    
    # Check for faculty consecutive violations
    print("\nChecking for faculty consecutive teaching violations...")
    days = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri"}
    
    violations = []
    
    for section, timetable in all_timetables.items():
        # Get faculty assignments for this section
        faculty_assignments = {}  # (faculty, day) -> [periods]
        
        for day in range(1, 6):
            for period in range(1, 8):
                subject = timetable[day][period]
                if subject and subject != "REMEDIAL":
                    # Find which faculty teaches this subject in this section
                    from algorithm import get_faculty_for_subject
                    try:
                        faculty = get_faculty_for_subject(section, subject)
                        key = (faculty, day)
                        if key not in faculty_assignments:
                            faculty_assignments[key] = []
                        faculty_assignments[key].append(period)
                    except:
                        pass
        
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
            print(f"   {v['faculty']} at {v['day']} {v['periods']} (Section {v['section']})")
    else:
        print("\n✅ NO VIOLATIONS FOUND - Faculty gap constraint is working!")
    
    # Print first section's timetable as verification
    first_section = list(all_timetables.keys())[0]
    print(f"\nFirst section ({first_section}) timetable:")
    print("     Mon  Tue  Wed  Thu  Fri")
    for period in range(1, 8):
        row = f"P{period}:  "
        for day in range(1, 6):
            subject = all_timetables[first_section][day][period] or "-"
            row += f"{subject:6} "
        print(row)
else:
    print("❌ Timetable generation failed!")
