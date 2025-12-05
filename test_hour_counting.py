#!/usr/bin/env python
"""Test that subject hours are correctly counted after reorganization"""

import algorithm

# Setup
algorithm.num_periods = 7
algorithm.num_days = 5
algorithm.sections = ["A"]
algorithm.break_config_state = {'first': 2, 'lunch': 4}

# Define subjects with required hours
algorithm.subjects_per_section = {
    "A": {
        "MATH": {"hours": 3, "lab": False},
        "OS": {"hours": 4, "lab": False},
        "JAVA": {"hours": 2, "lab": True},
        "REMEDIAL": {"hours": 0, "lab": False}
    }
}

# Create a messy timetable with scattered/duplicate subjects
timetable = algorithm.create_empty_timetable()

# Day 1: MATH, OS scattered
timetable[1][1] = "MATH"
timetable[1][2] = "OS"
timetable[1][3] = None
timetable[1][4] = None
timetable[1][5] = "OS"  # Duplicate - will be deduplicated
timetable[1][6] = None
timetable[1][7] = None

# Day 2: MATH, JAVA
timetable[2][1] = "JAVA"
timetable[2][2] = "JAVA"  # Lab 2-period
timetable[2][3] = None
timetable[2][4] = None
timetable[2][5] = "MATH"
timetable[2][6] = None
timetable[2][7] = None

# Day 3: OS scattered again
timetable[3][1] = "OS"
timetable[3][2] = "OS"  # Will be deduplicated
timetable[3][3] = None
timetable[3][4] = None
timetable[3][5] = "MATH"
timetable[3][6] = None
timetable[3][7] = None

print("Initial Timetable State:")
print("=" * 70)
for day in range(1, 4):
    print(f"\nDay {day}:")
    for p in range(1, 8):
        subject = timetable[day][p]
        print(f"  P{p}: {subject if subject else '(empty)'}")

print("\n" + "=" * 70)
print("Counting before reorganization:")
print("=" * 70)

# Count before
counters_before = algorithm.recount_subjects("A", timetable)
for subject, count in counters_before.items():
    if subject != "REMEDIAL":
        required = algorithm.subjects_per_section["A"][subject]["hours"]
        status = "✓" if count == required else "✗"
        print(f"  {subject}: {count} (required: {required}) {status}")

# Reorganize
print("\n" + "=" * 70)
print("Reorganizing with fix_remedial_at_end():")
print("=" * 70)

algorithm.fix_remedial_at_end("A", timetable)

print("\nReorganized Timetable:")
print("=" * 70)
for day in range(1, 4):
    print(f"\nDay {day}:")
    for p in range(1, 8):
        subject = timetable[day][p]
        marker = " [REMEDIAL]" if subject == "REMEDIAL" else ""
        print(f"  P{p}: {subject if subject else '(empty)'}{marker}")

print("\n" + "=" * 70)
print("Counting after reorganization:")
print("=" * 70)

# Recount after
counters_after = algorithm.recount_subjects("A", timetable)
for subject, count in counters_after.items():
    if subject != "REMEDIAL":
        required = algorithm.subjects_per_section["A"][subject]["hours"]
        status = "✓" if count == required else "✗"
        print(f"  {subject}: {count} (required: {required}) {status}")

print("\n" + "=" * 70)
print("Analysis:")
print("=" * 70)

total_hours_before = sum(counters_before.values())
total_hours_after = sum(counters_after.values())

print(f"Total hours before: {total_hours_before}")
print(f"Total hours after:  {total_hours_after}")
print(f"Total required:     {sum(info['hours'] for info in algorithm.subjects_per_section['A'].values())}")

all_correct = all(
    counters_after.get(subject, 0) == info["hours"]
    for subject, info in algorithm.subjects_per_section["A"].items()
    if subject != "REMEDIAL"
)

if all_correct:
    print("\n✓ All subjects have correct hour counts after reorganization!")
else:
    print("\n✗ Some subjects have incorrect hour counts!")
    for subject, info in algorithm.subjects_per_section["A"].items():
        if subject != "REMEDIAL":
            actual = counters_after.get(subject, 0)
            required = info["hours"]
            if actual != required:
                print(f"  {subject}: expected {required}, got {actual}")
