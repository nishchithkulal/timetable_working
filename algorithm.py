import random
from typing import Dict, List, Tuple, Optional, Set
import copy

# ==================== CONFIG / DATA SETUP (1-based indexing) ====================
# These variables will be set dynamically when generate_timetable is called
sections = ["A", "B", "C"]  # Default fallback
subjects_per_section = {}   # Will be set dynamically
faculties = {}              # Will be set dynamically
strict_subject_placement = {}  # Will be set dynamically
forbidden_subject_placement = {}  # Will be set dynamically

# Break configuration - default values
break_periods = {
    'first': 2,      # First break after P2
    'lunch': 4       # Lunch break after P4
}

days = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri"}
num_days = 5
num_periods = 7  # Teaching periods
# num_display_slots will be set dynamically based on number of breaks
max_subject_per_day = 3

# Map teaching period to display slot
# P1->1, P2->2, BREAK->3, P3->4, P4->5, BREAK->6, P5->7, P6->8, P7->9
def teaching_period_to_display_slot(period: int) -> int:
    """Convert teaching period (1-7) to display slot (1-9)"""
    if period <= 2:
        return period
    elif period <= 4:
        return period + 1
    else:
        return period + 2

subjects_per_section = {
    # Will be populated dynamically from database
}

faculties = {
    # Will be populated dynamically from database
}

assigned_multi_faculty = {}

def get_faculty_for_subject(section: str, subject: str) -> Optional[str]:
    global assigned_multi_faculty
    if subject not in faculties:
        return None
    faculty_data = faculties[subject]
    if isinstance(faculty_data, str):
        return faculty_data
    if isinstance(faculty_data, list):
        key = (section, subject)
        if key in assigned_multi_faculty:
            return assigned_multi_faculty[key]
        # For list, just pick the first one (as per requirement)
        chosen = faculty_data[0] if faculty_data else None
        if chosen:
            assigned_multi_faculty[key] = chosen
        return chosen
    return None


# ==================== STRICT / FORBIDDEN ====================
# These will be populated dynamically from frontend/database
# Format: {section: {subject: [(day_number, period_number), ...], ...}, ...}
# Example:
# strict_subject_placement = {
#     "A": {
#         "MATHS": [(1, 1), (3, 2)],  # Monday period 1, Wednesday period 2
#         "DDCO": [(2, 2), (4, 2), (5, 2)]
#     }
# }
# forbidden_subject_placement = {
#     "A": {
#         "TG": [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1)],  # Cannot be on period 1 any day
#         "REMEDIAL": [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1)]
#     }
# }

def convert_day_to_index(day_input) -> int:
    """Convert day input to index (1-5).
    Can handle:
    - Integer (1-5): returned as-is
    - String day names: "Mon", "Tue", etc. (converted for backward compatibility)
    """
    if isinstance(day_input, int):
        return day_input if 1 <= day_input <= 5 else -1
    
    day_map = {"Mon": 1, "Tue": 2, "Wed": 3, "Thu": 4, "Fri": 5}
    return day_map.get(day_input, -1)

def convert_placements(placement_dict, section):
    converted = {}
    if section not in placement_dict or not placement_dict[section]:
        return converted
    for subject, placements in placement_dict[section].items():
        converted_list = []
        for day_input, period in placements:
            day_idx = convert_day_to_index(day_input)
            if day_idx == -1 or not (1 <= period <= num_periods):
                continue
            converted_list.append((day_idx, period))
        if converted_list:
            converted[subject] = converted_list
    return converted

# ==================== LOCKED CELLS ====================
def is_locked_cell(section: str, day: int, period: int, subject: Optional[str] = None) -> bool:
    """
    Check if a cell is locked (strict placement or forbidden for a subject)
    Returns True if the cell should not be modified
    """
    # Check strict placements
    strict_dict = convert_placements(strict_subject_placement, section)
    for strict_subject, placements in strict_dict.items():
        if (day, period) in placements:
            # This cell is locked to a specific subject
            return True

    # Check forbidden placements for the given subject
    if subject:
        forbidden_dict = convert_placements(forbidden_subject_placement, section)
        if subject in forbidden_dict:
            if (day, period) in forbidden_dict[subject]:
                # This subject is forbidden at this position
                return True

    return False

def get_all_locked_cells(section: str) -> Set[Tuple[int, int]]:
    """Get all cells that are locked due to strict placements"""
    locked = set()
    strict_dict = convert_placements(strict_subject_placement, section)
    for subject, placements in strict_dict.items():
        for (day, period) in placements:
            locked.add((day, period))
    return locked

# ==================== HELPERS ====================
def create_empty_timetable():
    tt = {}
    for day in range(1, num_days + 1):
        tt[day] = {}
        for period in range(1, num_periods + 1):
            tt[day][period] = None
    return tt

def recount_subjects(section: str, timetable: Dict[int, Dict[int, Optional[str]]]) -> Dict[str, int]:
    counters = {subj: 0 for subj in subjects_per_section[section]}
    for day in range(1, num_days + 1):
        for period in range(1, num_periods + 1):
            subj = timetable[day][period]
            if subj and subj in counters:
                counters[subj] += 1
    return counters

def is_section_complete(section: str, counters: Dict[str, int]) -> bool:
    for subject, info in subjects_per_section[section].items():
        if counters.get(subject, 0) != info["hours"]:
            return False
    return True

def get_incomplete_subjects(section: str, counters: Dict[str, int]) -> List[Tuple[str, int]]:
    incomplete = []
    for subject, info in subjects_per_section[section].items():
        have = counters.get(subject, 0)
        if have < info["hours"]:
            incomplete.append((subject, info["hours"] - have))
    return incomplete

def get_timetable_state_hash(timetable: Dict[int, Dict[int, Optional[str]]]) -> str:
    state = []
    for d in range(1, num_days+1):
        for p in range(1, num_periods+1):
            state.append(timetable[d][p] or "EMPTY")
    return "|".join(state)

def print_timetable(section: str, timetable: Dict[int, Dict[int, Optional[str]]], counters: Dict[str, int]):
    print(f"\n{'='*130}")
    print(f"SECTION {section} TIMETABLE".center(130))
    print(f"{'='*130}")
    print(f"{'Day':<12}", end="")
    
    # Calculate which display slots are breaks
    first_break_slot = break_periods['first'] + 1  # +1 for the break itself
    lunch_break_slot = break_periods['lunch'] + 2  # +2 for both breaks before lunch
    
    for slot in range(1, num_display_slots + 1):
        if slot == first_break_slot or slot == lunch_break_slot:
            print(f"{'BREAK':<14}", end="")
        else:
            # Map display slot back to teaching period for label
            if slot < first_break_slot:
                p = slot
            elif slot < lunch_break_slot:
                p = slot - 1
            else:
                p = slot - 2
            print(f"P{p:<13}", end="")
    print()
    print("-" * 130)

    for d in range(1, num_days+1):
        day_name = days[d]
        print(f"{day_name:<12}", end="")

        for slot in range(1, num_display_slots + 1):
            if slot == first_break_slot or slot == lunch_break_slot:
                print(f"{'BREAK':<14}", end="")
            else:
                # Map display slot to teaching period
                if slot < first_break_slot:
                    p = slot
                elif slot < lunch_break_slot:
                    p = slot - 1
                else:
                    p = slot - 2

                s = timetable[d][p]
                if s:
                    f = get_faculty_for_subject(section, s)
                    display = f"{s}({f})"
                    print(f"{display:<14}", end="")
                else:
                    print(f"{'---':<14}", end="")
        print()

    print("-"*130)
    print(f"\nSubject Usage for Section {section}:")
    for subject, count in sorted(counters.items()):
        max_hours = subjects_per_section[section][subject]["hours"]
        status = "✓" if count == max_hours else "✗"
        print(f"  {status} {subject}: {count}/{max_hours}", end="  ")
    print("\n")

def get_faculty_schedule(all_timetables: Dict[str, Dict[int, Dict[int, Optional[str]]]]) -> Dict[Tuple[str, int, int], str]:
    schedule = {}
    for section, tt in all_timetables.items():
        for d in range(1, num_days+1):
            for p in range(1, num_periods+1):
                subj = tt[d][p]
                if subj:
                    fac = get_faculty_for_subject(section, subj)
                    if fac:
                        schedule[(section, d, p)] = fac
    return schedule

def verify_lab_integrity(section: str, timetable: Dict[int, Dict[int, Optional[str]]]) -> bool:
    for subject, info in subjects_per_section[section].items():
        if not info["lab"]:
            continue
        positions = []
        for d in range(1, num_days+1):
            for p in range(1, num_periods+1):
                if timetable[d][p] == subject:
                    positions.append((d, p))
        
        expected_hours = info["hours"]
        
        # Labs MUST have even hours only (enforced by UI dropdown)
        if expected_hours % 2 != 0:
            print(f"    ✗ LAB ERROR: {subject} has odd hours ({expected_hours}) - labs must have even hours only")
            return False
        
        # Number of positions must match hours
        if len(positions) != expected_hours:
            print(f"    ✗ LAB ERROR: {subject} has {len(positions)} periods but needs {expected_hours}")
            return False
        
        # All lab periods must be in consecutive pairs
        pairs_needed = expected_hours // 2
        pairs_found = 0
        
        i = 0
        while i < len(positions):
            if i+1 >= len(positions):
                # Odd number of positions means incomplete pairing
                print(f"    ✗ LAB ERROR: {subject} has incomplete pairing (odd count) in section {section}")
                return False
            
            d1, p1 = positions[i]
            d2, p2 = positions[i+1]
            
            if d1 != d2 or p2 != p1 + 1:
                print(f"    ✗ LAB ERROR: {subject} not consecutive at {days[d1]} P{p1}")
                return False
            
            # Check if lab crosses break
            if p1 == 2 or p1 == 4:
                print(f"    ✗ LAB ERROR: {subject} crosses break at {days[d1]} P{p1}-P{p2}")
                return False
            
            pairs_found += 1
            i += 2
        
        if pairs_found != pairs_needed:
            print(f"    ✗ LAB ERROR: {subject} has {pairs_found} pairs but needs {pairs_needed}")
            return False
    
    return True

# ==================== CONSTRAINT CHECKS ====================
def check_last_subject_overlap(section: str, subject: str, day: int, period: int,
                               all_timetables: Dict[str, Dict[int, Dict[int, Optional[str]]]]) -> bool:
    if subject not in subjects_per_section[section]:
        return False
    if not subjects_per_section[section][subject].get("last", False):
        return False

    # Special handling for MC1 and MC2 - they must NEVER overlap regardless of faculty
    if subject in ["MC1", "MC2"]:
        for other_section in sections:
            if other_section not in all_timetables:
                continue
            # Check P6 and P7 on the same day
            for chk_p in [6, 7]:
                other_subj = all_timetables[other_section][day][chk_p]
                if other_subj in ["MC1", "MC2"]:
                    print(f"      ✗ MC OVERLAP: {subject} in {section} cannot be placed - {other_subj} already in {other_section} on {days[day]} P{chk_p}")
                    return True
        return False

    # For other last=True subjects, check faculty conflicts
    faculty = get_faculty_for_subject(section, subject)
    if not faculty:
        return False
    for other_section in sections:
        if other_section not in all_timetables:
            continue
        for chk_p in [6,7]:
            other_subj = all_timetables[other_section][day][chk_p]
            if other_subj and other_subj in subjects_per_section[other_section] and subjects_per_section[other_section][other_subj].get("last", False):
                other_fac = get_faculty_for_subject(other_section, other_subj)
                if other_fac == faculty:
                    return True
    return False

def check_faculty_conflict(faculty: str, section: str, day: int, period: int,
                          faculty_schedule: Dict[Tuple[str, int, int], str]) -> bool:
    # Check all sections (including same section) for faculty conflicts
    for other_section in sections:
        if (other_section, day, period) in faculty_schedule and faculty_schedule[(other_section, day, period)] == faculty:
            return True
        if period < num_periods and (other_section, day, period + 1) in faculty_schedule and faculty_schedule[(other_section, day, period + 1)] == faculty:
            return True
        if period > 1 and (other_section, day, period - 1) in faculty_schedule and faculty_schedule[(other_section, day, period - 1)] == faculty:
            return True
    return False

def check_consecutive_constraint(timetable: Dict[int, Dict[int, Optional[str]]], subject: str,
                                 day: int, period: int, is_lab: bool) -> bool:
    """
    STRICT: Non-lab subjects can ONLY be consecutive at P2-P3 and P4-P5 (across breaks).
    All other consecutive periods are BLOCKED for non-lab subjects.
    Labs are always allowed to be consecutive (they are 2-period blocks).
    """
    if is_lab:
        return True

    # Allowed consecutive period pairs for non-lab subjects (across breaks only)
    allowed_consecutive_pairs = [(2, 3), (4, 5)]

    # Check previous period
    if period > 1 and timetable[day][period-1] == subject:
        if (period-1, period) not in allowed_consecutive_pairs:
            return False  # BLOCKED: consecutive not allowed here

    # Check next period
    if period < num_periods and timetable[day][period+1] == subject:
        if (period, period+1) not in allowed_consecutive_pairs:
            return False  # BLOCKED: consecutive not allowed here

    return True

def can_place_lab(timetable: Dict[int, Dict[int, Optional[str]]], subject: str, section: str,
                  day: int, period: int, slots_needed: int) -> bool:
    """
    Lab placement rules with break awareness:
    - Valid positions: P1-P2, P3-P4, P5-P6, P6-P7
    - Invalid positions: P2-P3 (crosses first break), P4-P5 (crosses second break)
    - For last=True labs (MC1, MC2, MP), must be at P6-P7
    - MC1 and MC2 are enforced to P6-P7 only
    - Labs cannot be placed at P7 (only 1 slot available)
    """
    if subject not in subjects_per_section[section]:
        return False
    
    # Labs cannot be placed at P7 (need 2 consecutive periods)
    if period == 7:
        return False
    
    info = subjects_per_section[section][subject]

    # MC1 and MC2 MUST be at P6-P7 (strictly enforced)
    if subject in ["MC1", "MC2"]:
        if period != 6:
            return False

    # Other last=True labs must be at P6-P7
    if info.get("last", False):
        if period != 6:
            return False

    # Labs cannot start at P2 or P4 (would cross breaks)
    if period == 2 or period == 4:
        return False

    # Valid lab starting periods: 1, 3, 5, 6
    valid_lab_starts = [1, 3, 5, 6]
    if period not in valid_lab_starts:
        return False

    # Check if there's enough space
    if period + slots_needed - 1 > num_periods:
        return False

    # Check if cells are empty
    for i in range(slots_needed):
        cell = timetable[day][period + i]
        if cell is not None:
            return False

    return True

def get_preferred_lab_periods() -> List[int]:
    """Return lab starting periods in priority order: preferred first, fallback last"""
    # P3, P5, P6 are preferred (don't include first slot)
    # P1 is fallback
    return [3, 5, 6, 1]

# ==================== INSERTION ALGORITHM ====================
def insertion_algorithm(section: str, all_timetables: Dict[str, Dict[int, Dict[int, Optional[str]]]]) -> Tuple[Dict[int, Dict[int, Optional[str]]], Dict[str, int]]:
    print(f"\n  → INSERTION for Section {section}")
    timetable = create_empty_timetable()
    counters = {subj: 0 for subj in subjects_per_section[section]}
    faculty_schedule = get_faculty_schedule(all_timetables)

    # Handle strict placements first
    strict_dict = convert_placements(strict_subject_placement, section)
    for subject, placements in strict_dict.items():
        if subject not in subjects_per_section[section]:
            continue
        info = subjects_per_section[section][subject]
        is_lab = info["lab"]
        faculty = get_faculty_for_subject(section, subject)
        for (day, period) in placements:
            slots_needed = 2 if is_lab else 1
            
            # Check faculty conflict BEFORE placing any subject (strict or not)
            has_conflict = False
            for slot_offset in range(slots_needed):
                if check_faculty_conflict(faculty, section, day, period + slot_offset, faculty_schedule):
                    has_conflict = True
                    break
            
            if has_conflict:
                print(f"    ✗ Could not place strict {subject} at {days[day]} P{period} - faculty conflict")
                continue
            
            if is_lab and not can_place_lab(timetable, subject, section, day, period, slots_needed):
                print(f"    ✗ Could not place strict lab {subject} at {days[day]} P{period}")
                continue
            if info.get("last", False) and check_last_subject_overlap(section, subject, day, period, all_timetables):
                print(f"    ✗ Cannot place strict {subject} - last=True overlap")
                continue

            # For non-lab strict placements, check consecutive constraint BEFORE placing
            if not is_lab:
                # Check if cell is already occupied
                if timetable[day][period] is not None:
                    print(f"    ✗ Could not place strict {subject} at {days[day]} P{period} - cell occupied")
                    continue

                # Temporarily place to check constraint
                timetable[day][period] = subject
                
                if not check_consecutive_constraint(timetable, subject, day, period, is_lab):
                    print(f"    ✗ Could not place strict {subject} at {days[day]} P{period} - violates consecutive constraint")
                    # Rollback
                    timetable[day][period] = None
                    continue

                # If valid, update counters and faculty schedule
                counters[subject] += 1
                faculty_schedule[(section, day, period)] = faculty
                print(f"    ✓ Placed strict {subject} at {days[day]} P{period}")
            else:
                # Labs - check MC1/MC2 overlap if applicable
                if subject in ["MC1", "MC2"]:
                    if check_last_subject_overlap(section, subject, day, period, all_timetables):
                        print(f"    ✗ Could not place strict {subject} at {days[day]} P{period} - MC overlap")
                        continue

                # Place the lab
                for i in range(slots_needed):
                    timetable[day][period + i] = subject
                    counters[subject] += 1
                    faculty_schedule[(section, day, period + i)] = faculty
                print(f"    ✓ Placed strict lab {subject} at {days[day]} P{period}-P{period+1}")

    subjects_to_place = [s for s, info in subjects_per_section[section].items() if s != "REMEDIAL"]

    # Use priority order for periods: preferred lab periods first, then others
    lab_priority_periods = get_preferred_lab_periods()
    regular_periods = [p for p in range(1, num_periods+1)]

    # Try to place subjects
    for day in range(1, num_days+1):
        for period in regular_periods:
            if timetable[day][period] is not None:
                continue

            # Check if this cell is locked to a strict placement
            if is_locked_cell(section, day, period):
                continue

            random.shuffle(subjects_to_place)
            for subject in subjects_to_place:
                info = subjects_per_section[section][subject]
                if counters[subject] >= info["hours"]:
                    continue

                # Check forbidden constraint for this subject
                if is_locked_cell(section, day, period, subject):
                    continue

                is_lab = info["lab"]
                faculty = get_faculty_for_subject(section, subject)

                if is_lab:
                    # For labs, check if next period would exceed bounds
                    if period + 1 > num_periods:  # Can't place 2-period lab if no next period
                        # Labs must have even hours, so we only place in 2-period blocks
                        # If we can't place 2 periods, skip this slot
                        continue
                    
                    remaining = info["hours"] - counters[subject]
                    if remaining >= 2:
                        if can_place_lab(timetable, subject, section, day, period, 2):
                            # Check last subject overlap (includes MC1/MC2 overlap check)
                            if info.get("last", False) or subject in ["MC1", "MC2"]:
                                if check_last_subject_overlap(section, subject, day, period, all_timetables):
                                    continue
                            if not any(check_faculty_conflict(faculty, section, day, period+i, faculty_schedule) for i in range(2)):
                                for i in range(2):
                                    timetable[day][period+i] = subject
                                    counters[subject] += 1
                                    faculty_schedule[(section, day, period+i)] = faculty
                                break
                else:
                    # For non-lab subjects, check consecutive constraint
                    old_val = timetable[day][period]
                    timetable[day][period] = subject

                    if check_consecutive_constraint(timetable, subject, day, period, False):
                        if not check_faculty_conflict(faculty, section, day, period, faculty_schedule):
                            # Valid placement - keep it
                            counters[subject] += 1
                            faculty_schedule[(section, day, period)] = faculty
                            break
                        else:
                            # Faculty conflict - rollback
                            timetable[day][period] = old_val
                    else:
                        # Consecutive constraint violated - rollback
                        timetable[day][period] = old_val

    # Fill remaining slots with REMEDIAL
    for day in range(1, num_days+1):
        for period in range(1, num_periods+1):
            if timetable[day][period] is None and counters["REMEDIAL"] < subjects_per_section[section]["REMEDIAL"]["hours"]:
                if not is_locked_cell(section, day, period):
                    timetable[day][period] = "REMEDIAL"
                    counters["REMEDIAL"] += 1

    return timetable, counters

# ==================== SWAP & SAFE SWAP ====================
def attempt_random_swap(section: str, timetable: Dict[int, Dict[int, Optional[str]]],
                        counters: Dict[str, int],
                        all_timetables: Dict[str, Dict[int, Dict[int, Optional[str]]]]) -> bool:
    positions = [(d,p) for d in range(1, num_days+1) for p in range(1, num_periods+1)]
    locked_cells = get_all_locked_cells(section)

    # Remove locked cells from positions
    positions = [(d,p) for (d,p) in positions if (d,p) not in locked_cells]

    random.shuffle(positions)
    attempts = 0
    max_attempts = 200

    while attempts < max_attempts and len(positions) >= 2:
        attempts += 1
        (d1,p1) = positions[random.randrange(len(positions))]
        (d2,p2) = positions[random.randrange(len(positions))]
        if (d1,p1) == (d2,p2):
            continue

        new_timetable = copy.deepcopy(timetable)

        def expand_unit(tt, d, p):
            subj = tt[d][p]
            if not subj:
                return [(d,p)]
            if p < num_periods and tt[d][p+1] == subj:
                return [(d,p),(d,p+1)]
            if p > 1 and tt[d][p-1] == subj:
                return [(d,p-1),(d,p)]
            return [(d,p)]

        unit1 = expand_unit(new_timetable, d1, p1)
        unit2 = expand_unit(new_timetable, d2, p2)

        # Check if any cell in units is locked
        if any((d,p) in locked_cells for (d,p) in unit1) or any((d,p) in locked_cells for (d,p) in unit2):
            continue

        if set(unit1) & set(unit2):
            continue

        vals1 = [new_timetable[d][p] for (d,p) in unit1]
        vals2 = [new_timetable[d][p] for (d,p) in unit2]

        if len(vals1) != len(vals2):
            continue

        # Check forbidden constraints before swapping
        subj1 = vals1[0] if vals1[0] else None
        subj2 = vals2[0] if vals2[0] else None

        forbidden_swap = False
        for (d,p) in unit2:
            if subj1 and is_locked_cell(section, d, p, subj1):
                forbidden_swap = True
                break
        for (d,p) in unit1:
            if subj2 and is_locked_cell(section, d, p, subj2):
                forbidden_swap = True
                break

        if forbidden_swap:
            continue

        for idx, (d,p) in enumerate(unit1):
            new_timetable[d][p] = vals2[idx]
        for idx, (d,p) in enumerate(unit2):
            new_timetable[d][p] = vals1[idx]

        temp_all = {}
        for s in all_timetables:
            if s == section:
                temp_all[s] = new_timetable
            else:
                temp_all[s] = all_timetables[s]

        if not verify_lab_integrity(section, new_timetable):
            continue

        valid_nonconsec = True
        for d in range(1, num_days+1):
            for p in range(1, num_periods+1):
                subj = new_timetable[d][p]
                if not subj:
                    continue
                info = subjects_per_section[section].get(subj)
                if info and not info["lab"]:
                    if not check_consecutive_constraint(new_timetable, subj, d, p, False):
                        valid_nonconsec = False
                        break
            if not valid_nonconsec:
                break
        if not valid_nonconsec:
            continue

        faculty_sched_temp = get_faculty_schedule(temp_all)
        conflict_found = False
        for d in range(1, num_days+1):
            for p in range(1, num_periods+1):
                subj = new_timetable[d][p]
                if subj:
                    fac = get_faculty_for_subject(section, subj)
                    if check_faculty_conflict(fac, section, d, p, faculty_sched_temp):
                        conflict_found = True
                        break
            if conflict_found:
                break
        if conflict_found:
            continue

        for d in range(1, num_days+1):
            for p in range(1, num_periods+1):
                timetable[d][p] = new_timetable[d][p]
        new_counters = recount_subjects(section, timetable)
        counters.clear()
        counters.update(new_counters)
        return True

    return False

# ==================== PLACEMENT AVOIDING STUCK CELLS ====================
def place_avoiding_stuck_cells(section: str, timetable: Dict[int, Dict[int, Optional[str]]],
                               counters: Dict[str, int], subject: str,
                               stuck_cells: Set[Tuple[int, int]],
                               all_timetables: Dict[str, Dict[int, Dict[int, Optional[str]]]]) -> bool:
    faculty = get_faculty_for_subject(section, subject)
    faculty_schedule = get_faculty_schedule(all_timetables)
    info = subjects_per_section[section][subject]
    is_lab = info["lab"]
    locked_cells = get_all_locked_cells(section)

    if is_lab:
        # Try preferred periods first, then fallback
        lab_periods = get_preferred_lab_periods()
        for d in range(1, num_days+1):
            for p in lab_periods:
                if (d,p) in stuck_cells or (d,p) in locked_cells:
                    continue
                if info["hours"] - counters[subject] < 2:
                    continue
                if can_place_lab(timetable, subject, section, d, p, 2):
                    # Check if second cell is also not locked
                    if (d, p+1) in locked_cells:
                        continue
                    # Check MC1/MC2 overlap for these subjects
                    if subject in ["MC1", "MC2"]:
                        if check_last_subject_overlap(section, subject, d, p, all_timetables):
                            continue
                    # Check faculty conflicts
                    if not any(check_faculty_conflict(faculty, section, d, p+i, faculty_schedule) for i in range(2)):
                        for i in range(2):
                            timetable[d][p+i] = subject
                            counters[subject] += 1
                        return True
    else:
        for d in range(1, num_days+1):
            for p in range(1, num_periods+1):
                if (d,p) in stuck_cells or (d,p) in locked_cells:
                    continue
                if is_locked_cell(section, d, p, subject):
                    continue
                if timetable[d][p] is None:
                    # Temporarily place to check consecutive constraint
                    timetable[d][p] = subject

                    if check_consecutive_constraint(timetable, subject, d, p, False):
                        if not check_faculty_conflict(faculty, section, d, p, faculty_schedule):
                            # Valid placement - keep it
                            counters[subject] += 1
                            return True
                        else:
                            # Faculty conflict - rollback
                            timetable[d][p] = None
                    else:
                        # Consecutive constraint violated - rollback
                        timetable[d][p] = None
    return False

# ==================== SMART OPTIMIZATION ====================
def smart_optimize(section: str, timetable: Dict[int, Dict[int, Optional[str]]],
                   counters: Dict[str, int], all_timetables: Dict[str, Dict[int, Dict[int, Optional[str]]]],
                   max_iterations: int = 1000) -> Tuple[Dict[int, Dict[int, Optional[str]]], Dict[str, int], bool]:
    print(f"\n  → SMART OPTIMIZATION for Section {section}")

    seen_states: Set[str] = set()
    stuck_cells: Set[Tuple[int,int]] = set()
    consecutive_same_state = 0
    last_state_hash = ""

    for iteration in range(1, max_iterations+1):
        if iteration % 100 == 0:
            print(f"    → Iteration {iteration}/{max_iterations}")

        counters = recount_subjects(section, timetable)
        if is_section_complete(section, counters):
            print(f"    ✓ Section {section} is 100% COMPLETE!")
            return timetable, counters, True

        current_state = get_timetable_state_hash(timetable)
        if current_state == last_state_hash:
            consecutive_same_state += 1
        else:
            consecutive_same_state = 0
            last_state_hash = current_state

        if consecutive_same_state >= 10:
            print(f"    ⚠ Loop detected! Trying recovery strategies...")
            incomplete = get_incomplete_subjects(section, counters)
            if incomplete:
                subj, deficit = incomplete[0]
                if place_avoiding_stuck_cells(section, timetable, counters, subj, stuck_cells, all_timetables):
                    consecutive_same_state = 0
                    continue

            if attempt_random_swap(section, timetable, counters, all_timetables):
                consecutive_same_state = 0
                continue

            for d in range(1, num_days+1):
                for p in range(1, num_periods+1):
                    if (d,p) not in stuck_cells:
                        stuck_cells.add((d,p))
                        print(f"    → Marking stuck cell {days[d]} P{p}")
                        break
                if stuck_cells:
                    break
            consecutive_same_state = 0
            continue

        incomplete = get_incomplete_subjects(section, counters)
        if incomplete:
            for subject, deficit in incomplete:
                for _ in range(min(deficit, 3)):
                    if place_avoiding_stuck_cells(section, timetable, counters, subject, stuck_cells, all_timetables):
                        break

        fix_remedial_at_end(section, timetable)

    print(f"    ✗ Could not fully optimize after {max_iterations} iterations")
    return timetable, counters, False

def fix_remedial_at_end(section: str, timetable: Dict[int, Dict[int, Optional[str]]]):
    locked_cells = get_all_locked_cells(section)

    for d in range(1, num_days+1):
        row = [timetable[d][p] for p in range(1, num_periods+1)]
        non_remedial = []
        remedial_count = 0
        lab_blocks = []  # Store lab blocks to preserve continuity

        # Collect subjects and identify lab blocks
        i = 1
        while i <= num_periods:
            s = timetable[d][i]
            if (d, i) in locked_cells:
                # Keep locked cells in place
                i += 1
                continue
            
            # Check if this is part of a lab block
            is_part_of_lab = False
            if s and s != "REMEDIAL":
                info = subjects_per_section[section].get(s, {})
                if info.get("lab", False):
                    # This is a lab - check if it's a complete pair or incomplete
                    if i < num_periods and timetable[d][i+1] == s:
                        # It's a 2-period lab block
                        lab_blocks.append((i, i+1, s))
                        i += 2
                        is_part_of_lab = True
                    else:
                        # Single period (incomplete lab - should not happen but handle it)
                        non_remedial.append(s)
                        i += 1
                        is_part_of_lab = True
                else:
                    # Non-lab subject
                    non_remedial.append(s)
                    i += 1
            elif s == "REMEDIAL":
                remedial_count += 1
                i += 1
            else:
                i += 1

        # Clear only non-locked cells
        for p in range(1, num_periods+1):
            if (d, p) not in locked_cells:
                timetable[d][p] = None

        # Refill non-locked cells - preserve lab blocks, prioritize placing them
        idx = 1
        non_remedial_idx = 0
        lab_block_idx = 0
        placed_subjects = set()  # Track which subjects have been placed
        
        while idx <= num_periods:
            if (d, idx) in locked_cells:
                # Skip locked cells
                idx += 1
                continue

            # Try to place a lab block if available and we have space for 2 periods
            if lab_block_idx < len(lab_blocks) and idx + 1 <= num_periods and (d, idx+1) not in locked_cells:
                start, end, subject = lab_blocks[lab_block_idx]
                # Place the 2-period lab block
                timetable[d][idx] = subject
                timetable[d][idx+1] = subject
                placed_subjects.add(subject)
                lab_block_idx += 1
                idx += 2
                continue
            
            # Place non-lab subjects
            if non_remedial_idx < len(non_remedial):
                subj = non_remedial[non_remedial_idx]
                # Don't place if this is a lab (shouldn't happen)
                info = subjects_per_section[section].get(subj, {})
                if not info.get("lab", False):
                    timetable[d][idx] = subj
                    non_remedial_idx += 1
                else:
                    # Skip labs in the non_remedial list (shouldn't happen)
                    non_remedial_idx += 1
                    continue
            elif remedial_count > 0:
                timetable[d][idx] = "REMEDIAL"
                remedial_count -= 1
            
            idx += 1
        
        # If there are unplaced lab blocks, that's a problem
        if lab_block_idx < len(lab_blocks):
            print(f"    ⚠ WARNING: Could not place all lab blocks on day {d} in section {section}")

# ==================== FACULTY TIMETABLE GENERATION ====================
def generate_faculty_timetables(all_timetables: Dict[str, Dict[int, Dict[int, Optional[str]]]]) -> Dict[str, Dict[int, Dict[int, str]]]:
    faculty_timetables = {}
    all_faculties = set()
    for v in faculties.values():
        if isinstance(v, str):
            all_faculties.add(v)
        else:
            for name in v:
                all_faculties.add(name)
    for faculty_name in all_faculties:
        faculty_tt = {d: {p: "---" for p in range(1, num_periods+1)} for d in range(1, num_days+1)}
        for section, tt in all_timetables.items():
            for d in range(1, num_days+1):
                for p in range(1, num_periods+1):
                    subj = tt[d][p]
                    if subj:
                        fac = get_faculty_for_subject(section, subj)
                        if fac == faculty_name:
                            faculty_tt[d][p] = f"{subj}({section})"
        faculty_timetables[faculty_name] = faculty_tt
    return faculty_timetables

def print_faculty_timetable(faculty_name: str, faculty_tt: Dict[int, Dict[int, str]]):
    print(f"\n{'='*130}")
    print(f"FACULTY: {faculty_name}".center(130))
    print(f"{'='*130}")
    print(f"{'Day':<12}", end="")
    
    # Calculate which display slots are breaks
    first_break_slot = break_periods['first'] + 1  # +1 for the break itself
    lunch_break_slot = break_periods['lunch'] + 2  # +2 for both breaks before lunch
    
    for slot in range(1, num_display_slots + 1):
        if slot == first_break_slot or slot == lunch_break_slot:
            print(f"{'BREAK':<14}", end="")
        else:
            # Map display slot back to teaching period for label
            if slot < first_break_slot:
                p = slot
            elif slot < lunch_break_slot:
                p = slot - 1
            else:
                p = slot - 2
            print(f"P{p:<13}", end="")
    print()
    print("-" * 130)

    for d in range(1, num_days+1):
        day_name = days[d]
        print(f"{day_name:<12}", end="")

        for slot in range(1, num_display_slots + 1):
            if slot == first_break_slot or slot == lunch_break_slot:
                print(f"{'BREAK':<14}", end="")
            else:
                # Map display slot to teaching period
                if slot < first_break_slot:
                    p = slot
                elif slot < lunch_break_slot:
                    p = slot - 1
                else:
                    p = slot - 2

                entry = faculty_tt[d][p]
                print(f"{entry:<14}", end="")
        print()
    print("-" * 130)

# ==================== MAIN ====================
def main():
    print("=" * 130)
    print("SMART TIMETABLE GENERATION - FIXED VERSION".center(130))
    print("=" * 130)
    print("\n🔧 TIMETABLE STRUCTURE:")
    print("  ✓ 7 Teaching Periods (P1-P7)")
    print("  ✓ 2 Break Periods (After P2 and After P4)")
    print("  ✓ 9 Total Slots: P1, P2, BREAK, P3, P4, BREAK, P5, P6, P7")
    print("\n🔧 CONSTRAINT RULES:")
    print("  ✓ Strict placements are LOCKED (cannot be swapped)")
    print("  ✓ Forbidden placements are ENFORCED (subjects blocked from specific slots)")
    print("  ✓ MC1 and MC2 MUST be at P6-P7 and NEVER overlap across sections")
    print("  ✓ Labs prioritized at: P3-P4, P5-P6, P6-P7 (preferred)")
    print("  ✓ Labs allowed at: P1-P2 (fallback, lower priority)")
    print("  ✗ Labs FORBIDDEN at: P2-P3, P4-P5 (crosses breaks)")
    print("  ✓ Non-lab subjects CAN be consecutive ONLY at P2-P3 and P4-P5")
    print("  ✗ Non-lab subjects BLOCKED from consecutive at P1-P2, P3-P4, P5-P6, P6-P7")
    print("=" * 130)

    max_global_attempts = 50
    global_attempt = 0
    best_all_timetables = None
    best_all_counters = None

    while global_attempt < max_global_attempts:
        global_attempt += 1
        print(f"\n{'='*130}")
        print(f"GLOBAL ATTEMPT {global_attempt}/{max_global_attempts}".center(130))
        print(f"{'='*130}")

        all_timetables = {}
        all_counters = {}

        for section in sections:
            print(f"\n{'-'*80}")
            print(f"Processing Section {section}")
            print(f"{'-'*80}")
            timetable, counters = insertion_algorithm(section, all_timetables)
            timetable, counters, success = smart_optimize(section, timetable, counters, all_timetables)
            all_timetables[section] = timetable
            all_counters[section] = counters

            if section != sections[0]:
                for prev in sections[:sections.index(section)]:
                    prev_counters = recount_subjects(prev, all_timetables[prev])
                    if not is_section_complete(prev, prev_counters):
                        print(f"  ⚠ Section {prev} affected -> re-optimizing")
                        all_timetables[prev], all_counters[prev], _ = smart_optimize(prev, all_timetables[prev], prev_counters, all_timetables)

        print(f"\n{'='*130}")
        print("VALIDATION".center(130))
        print(f"{'='*130}")
        all_complete = True
        has_empty_slots = False
        for section in sections:
            counters = recount_subjects(section, all_timetables[section])
            all_counters[section] = counters
            if not is_section_complete(section, counters):
                all_complete = False
                incom = get_incomplete_subjects(section, counters)
                print(f"  ✗ Section {section} incomplete: {incom}")
            for d in range(1, num_days+1):
                for p in range(1, num_periods+1):
                    if all_timetables[section][d][p] is None:
                        has_empty_slots = True
                        print(f"  ✗ Section {section}: Empty slot at {days[d]} P{p}")

            if not verify_lab_integrity(section, all_timetables[section]):
                all_complete = False

        if all_complete and not has_empty_slots:
            print(f"\n{'='*130}")
            print("✓ ALL SECTIONS COMPLETE WITH NO EMPTY SLOTS ✓".center(130))
            print(f"{'='*130}")

            # Print section timetables
            for section in sections:
                print_timetable(section, all_timetables[section], all_counters[section])

            # Print faculty timetables
            print(f"\n{'='*130}")
            print("FACULTY TIMETABLES".center(130))
            print(f"{'='*130}")
            faculty_timetables = generate_faculty_timetables(all_timetables)
            for faculty_name in sorted(faculty_timetables.keys()):
                print_faculty_timetable(faculty_name, faculty_timetables[faculty_name])

            return

        best_all_timetables = all_timetables
        best_all_counters = all_counters
       

    print("\n" + "="*130)
    print("WARNING: exhausted global attempts; printing best-effort result".center(130))
    print("="*130)
    for section in sections:
        print_timetable(section, best_all_timetables[section], best_all_counters[section])

    # Print faculty timetables even for best-effort
    print(f"\n{'='*130}")
    print("FACULTY TIMETABLES (BEST EFFORT)".center(130))
    print(f"{'='*130}")
    faculty_timetables = generate_faculty_timetables(best_all_timetables)
    for faculty_name in sorted(faculty_timetables.keys()):
        print_faculty_timetable(faculty_name, faculty_timetables[faculty_name])
 
def section_timetable(section: str, all_timetables: Dict[str, Dict[int, Dict[int, Optional[str]]]] = None,
                      attempts: int = 10) -> Tuple[Dict[int, Dict[int, Optional[str]]], Dict[str, int], bool]:
    """Generate and return a timetable for a single section.

    Parameters:
    - section: the section name (must be in `sections`).
    - all_timetables: optional dict of other sections' timetables to consider for cross-section constraints.
    - attempts: number of attempts to try optimization before returning best-effort.

    Returns a tuple (timetable, counters, success) where `timetable` is the generated
    timetable dict, `counters` maps subjects to placed hours, and `success` indicates
    whether a fully valid timetable (per constraints) was produced.
    """
    if section not in sections:
        raise ValueError(f"Unknown section: {section}")

    if all_timetables is None:
        all_timetables = {}

    best_tt = None
    best_counters = None

    for _ in range(attempts):
        tt, counters = insertion_algorithm(section, all_timetables)
        tt, counters, success = smart_optimize(section, tt, counters, all_timetables)
        if success:
            return tt, counters, True
        best_tt, best_counters = tt, counters

    # return best effort if no success
    return best_tt, best_counters, False

def store_section_timetables(section_list=None, subjects_dict=None, faculty_dict=None, strict_constraints=None, forbidden_constraints=None, break_config=None):
    """Generate and return timetables for all sections.
    
    Args:
        section_list: List of section names (e.g., ["A", "B", "C"])
        subjects_dict: Dictionary with structure {section: {subject_name: {hours, lab, last}, ...}, ...}
        faculty_dict: Dictionary mapping subject_name to faculty_name
        strict_constraints: Dictionary {section: {subject: [(day, period), ...], ...}, ...} for fixed placements
        forbidden_constraints: Dictionary {section: {subject: [(day, period), ...], ...}, ...} for forbidden placements
        break_config: Dictionary {first_break_period, lunch_break_period, second_break_period} for break timings
    
    Returns a dictionary mapping section names to their timetables.
    Each timetable is a dictionary mapping day numbers (1-5) to dictionaries mapping period numbers (1-7) to subject names."""
    
    global sections, subjects_per_section, faculties, assigned_multi_faculty, strict_subject_placement, forbidden_subject_placement, break_periods
    
    # Set the global variables from parameters
    if section_list is not None:
        sections = section_list
    if subjects_dict is not None:
        subjects_per_section = subjects_dict
    if faculty_dict is not None:
        faculties = faculty_dict
    if strict_constraints is not None:
        strict_subject_placement = strict_constraints
    if forbidden_constraints is not None:
        forbidden_subject_placement = forbidden_constraints
    if break_config is not None:
        break_periods = {
            'first': break_config.get('first_break_period', 2),
            'lunch': break_config.get('lunch_break_period', 4)
        }
    
    # Calculate display slots dynamically: 7 periods + 2 breaks = 9 slots
    global num_display_slots
    num_display_slots = num_periods + 2
    
    # Reset assigned faculties for this generation
    assigned_multi_faculty = {}
    
    max_global_attempts = 5  # Reduced from 50 for faster generation
    global_attempt = 0
    best_all_timetables = None
    best_all_counters = None

    while global_attempt < max_global_attempts:
        global_attempt += 1
        all_timetables = {}
        all_counters = {}

        for section in sections:
            timetable, counters = insertion_algorithm(section, all_timetables)
            timetable, counters, success = smart_optimize(section, timetable, counters, all_timetables)
            all_timetables[section] = timetable
            all_counters[section] = counters

            if section != sections[0]:
                for prev in sections[:sections.index(section)]:
                    prev_counters = recount_subjects(prev, all_timetables[prev])
                    if not is_section_complete(prev, prev_counters):
                        all_timetables[prev], all_counters[prev], _ = smart_optimize(prev, all_timetables[prev], prev_counters, all_timetables)

        all_complete = True
        has_empty_slots = False
        for section in sections:
            counters = recount_subjects(section, all_timetables[section])
            all_counters[section] = counters
            if not is_section_complete(section, counters):
                all_complete = False
            for d in range(1, num_days+1):
                for p in range(1, num_periods+1):
                    if all_timetables[section][d][p] is None:
                        has_empty_slots = True
                        break

            if not verify_lab_integrity(section, all_timetables[section]):
                all_complete = False

        if all_complete and not has_empty_slots:
            return all_timetables

        best_all_timetables = all_timetables
        best_all_counters = all_counters

    # Fill any remaining None values with REMEDIAL
    if best_all_timetables:
        for section in best_all_timetables:
            for day in range(1, num_days + 1):
                for period in range(1, num_periods + 1):
                    if best_all_timetables[section][day][period] is None:
                        best_all_timetables[section][day][period] = "REMEDIAL"
    
    return best_all_timetables  # Return best attempt if we couldn't get a perfect solution

if __name__ == "__main__":
    main()