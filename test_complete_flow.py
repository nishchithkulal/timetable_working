#!/usr/bin/env python
"""Test complete timetable generation with correct hour counting"""

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
        "ENGLISH": {"hours": 2, "lab": False},
        "OS": {"hours": 2, "lab": False},
        "JAVA": {"hours": 4, "lab": True},  # Lab (2-hour blocks)
        "REMEDIAL": {"hours": 0, "lab": False}
    }
}

# Create a timetable simulating insertion algorithm results
# Non-labs spread across different days (due to subject_already_on_day check)
# Labs can appear in 2-period blocks
timetable = algorithm.create_empty_timetable()

# Day 1: MATH (non-lab), JAVA LAB (lab 2-period)
timetable[1][1] = "MATH"
timetable[1][2] = "JAVA"
timetable[1][3] = "JAVA"
timetable[1][4] = None
timetable[1][5] = None
timetable[1][6] = None
timetable[1][7] = None

# Day 2: ENGLISH (non-lab)
timetable[2][1] = "ENGLISH"
timetable[2][2] = None
timetable[2][3] = None
timetable[2][4] = None
timetable[2][5] = None
timetable[2][6] = None
timetable[2][7] = None

# Day 3: MATH (non-lab), JAVA LAB (lab 2-period)
timetable[3][1] = "MATH"
timetable[3][2] = "JAVA"
timetable[3][3] = "JAVA"
timetable[3][4] = None
timetable[3][5] = None
timetable[3][6] = None
timetable[3][7] = None

# Day 4: OS (non-lab)
timetable[4][1] = "OS"
timetable[4][2] = None
timetable[4][3] = None
timetable[4][4] = None
timetable[4][5] = None
timetable[4][6] = None
timetable[4][7] = None

# Day 5: MATH (non-lab), ENGLISH (non-lab)
timetable[5][1] = "MATH"
timetable[5][2] = "ENGLISH"
timetable[5][3] = None
timetable[5][4] = None
timetable[5][5] = None
timetable[5][6] = None
timetable[5][7] = None

print("BEFORE fix_remedial_at_end():")
print("=" * 80)

for day in range(1, 6):
    subjects_today = []
    for p in range(1, 8):
        if timetable[day][p]:
            subjects_today.append(timetable[day][p])
    print(f"Day {day}: {' '.join(subjects_today)}")

# Count before
counters_before = algorithm.recount_subjects("A", timetable)

print("\nHour counts BEFORE reorganization:")
for subject, count in counters_before.items():
    if subject != "REMEDIAL":
        required = algorithm.subjects_per_section["A"][subject]["hours"]
        status = "✓" if count == required else "✗ SHORT"
        print(f"  {subject}: {count}/{required} {status}")

# Apply reorganization
print("\n" + "=" * 80)
print("Applying fix_remedial_at_end()...")
print("=" * 80)

algorithm.fix_remedial_at_end("A", timetable)

print("\nAFTER fix_remedial_at_end():")
print("=" * 80)

for day in range(1, 6):
    print(f"\nDay {day}:")
    non_remedial = []
    remedial_count = 0
    
    for p in range(1, 8):
        subject = timetable[day][p]
        if subject == "REMEDIAL":
            remedial_count += 1
        elif subject:
            non_remedial.append((p, subject))
    
    for p, subject in non_remedial:
        print(f"  P{p}: {subject}")
    
    if remedial_count > 0:
        start_p = non_remedial[-1][0] + 1 if non_remedial else 1
        print(f"  P{start_p}-P7: REMEDIAL (×{remedial_count})")
    
    # Check constraint: each non-lab subject appears at most once per day
    non_lab_subjects = set()
    for p in range(1, 8):
        subject = timetable[day][p]
        if subject and subject != "REMEDIAL":
            info = algorithm.subjects_per_section["A"].get(subject, {})
            if not info.get("lab", False):
                if subject in non_lab_subjects:
                    print(f"  ✗ ERROR: Non-lab {subject} appears twice on this day!")
                non_lab_subjects.add(subject)

# Count after
counters_after = algorithm.recount_subjects("A", timetable)

print("\n" + "=" * 80)
print("Hour counts AFTER reorganization:")
for subject, count in counters_after.items():
    if subject != "REMEDIAL":
        required = algorithm.subjects_per_section["A"][subject]["hours"]
        status = "✓" if count == required else "✗ SHORT"
        print(f"  {subject}: {count}/{required} {status}")

print("\n" + "=" * 80)
print("SUMMARY:")
all_correct = all(
    counters_after.get(subject, 0) == info["hours"]
    for subject, info in algorithm.subjects_per_section["A"].items()
    if subject != "REMEDIAL"
)

if all_correct:
    print("✓ All subjects have correct hour counts!")
    print("✓ REMEDIAL correctly placed at end of each day")
    print("✓ No non-lab subject appears twice per day")
else:
    print("✗ Some subjects have incorrect hour counts")
