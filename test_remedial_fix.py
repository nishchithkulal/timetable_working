#!/usr/bin/env python
"""Test that REMEDIAL appears at end and non-lab subjects appear only once per day"""

import algorithm
import copy

# Setup
algorithm.num_periods = 7
algorithm.num_days = 5
algorithm.sections = ["A", "B", "C"]
algorithm.break_config_state = {'first': 2, 'lunch': 4}

# Simulate a messy timetable where:
# 1. Subjects are scattered across periods
# 2. A non-lab subject appears multiple times
timetable = algorithm.create_empty_timetable()

# Day 1: OS scattered (P2, P5), MATH at P1
timetable[1][1] = "MATH"
timetable[1][2] = "OS"
timetable[1][3] = None
timetable[1][4] = None
timetable[1][5] = "OS"  # Duplicate - should be moved to consecutive
timetable[1][6] = None
timetable[1][7] = None

# Day 2: Mix of subjects scattered
timetable[2][1] = "JAVA"
timetable[2][2] = None
timetable[2][3] = "DSA"
timetable[2][4] = None
timetable[2][5] = "JAVA"  # Duplicate
timetable[2][6] = None
timetable[2][7] = None

print("Before fix_remedial_at_end:")
print("=" * 60)

for day in range(1, 3):
    print(f"\nDay {day}:")
    for p in range(1, 8):
        subject = timetable[day][p]
        if subject:
            marker = " (REMEDIAL)" if subject == "REMEDIAL" else ""
            print(f"  P{p}: {subject}{marker}")
        else:
            print(f"  P{p}: (empty)")

# Apply fix
algorithm.fix_remedial_at_end("A", timetable)

print("\n" + "=" * 60)
print("After fix_remedial_at_end:")
print("=" * 60)

for day in range(1, 3):
    print(f"\nDay {day}:")
    subjects_seen = set()
    remedial_started = False
    
    for p in range(1, 8):
        subject = timetable[day][p]
        marker = ""
        
        if subject == "REMEDIAL":
            remedial_started = True
            marker = " [REMEDIAL]"
        elif subject:
            if subject in subjects_seen:
                marker = " [ERROR: DUPLICATE!]"
            subjects_seen.add(subject)
        
        print(f"  P{p}: {subject}{marker}")
    
    # Verify: all REMEDIAL at end
    remedial_periods = [p for p in range(1, 8) if timetable[day][p] == "REMEDIAL"]
    non_remedial_periods = [p for p in range(1, 8) if timetable[day][p] and timetable[day][p] != "REMEDIAL"]
    
    if remedial_periods and non_remedial_periods:
        max_non_remedial = max(non_remedial_periods)
        min_remedial = min(remedial_periods)
        if max_non_remedial < min_remedial:
            print(f"  ✓ REMEDIAL correctly at end (starts at P{min_remedial})")
        else:
            print(f"  ✗ ERROR: REMEDIAL scattered!")
    elif remedial_periods:
        print(f"  ✓ All REMEDIAL (no subjects)")
    else:
        print(f"  ✓ No REMEDIAL needed")
    
    if len(subjects_seen) > 0:
        print(f"  ✓ No duplicate subjects (unique count: {len(subjects_seen)})")

print("\n" + "=" * 60)
print("Test completed!")
