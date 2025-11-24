# Lab Constraints Enforcement - Complete Justification

## Overview
This document explains the lab scheduling constraints and why they are enforced to prevent violations.

---

## Lab Constraint Rules

### 1. **Labs MUST Have Even Hours Only**
- **Rule**: Laboratory subjects can only have 2, 4, 6, 8, or 10 hours per week
- **UI Enforcement**: The "Number of Hours" field in `add_subjects.html` shows a dropdown with ONLY even numbers (2, 4, 6, 8, 10) when "Is Lab Subject" is checked
- **Backend Enforcement**: The `/add-subject` and `/update-subject` endpoints convert hours to `int` to ensure integer storage
- **Algorithm Enforcement**: `verify_lab_integrity()` rejects any lab with odd hours

**Justification**: 
- Labs are inherently 2-hour blocks (consecutive periods)
- With 7 teaching periods and 2 breaks, the effective slots are: P1-P2, P3-P4, P5-P6, P6-P7, P1-P3, P3-P5, P5-P7
- Only even-hour labs fit cleanly into 2-hour blocks without leaving incomplete periods
- Odd hours would either waste time or violate the consecutive period requirement

### 2. **Labs Must Always Be in Consecutive Pairs**
- **Rule**: Each 2-hour lab block must occupy exactly 2 consecutive periods on the same day
- **Validation**: `verify_lab_integrity()` checks that:
  - Every lab subject appears in complete pairs
  - Pairs are consecutive (period `p` followed by period `p+1`)
  - No single periods exist for labs (except as complete 2-period blocks)

**Examples**:
- ✅ Valid: Lab with 4 hours = 2 pairs (e.g., P1-P2 and P3-P4)
- ✅ Valid: Lab with 6 hours = 3 pairs (e.g., P1-P2, P3-P4, P5-P6)
- ❌ Invalid: Lab with 3 hours (odd) = cannot form complete pairs
- ❌ Invalid: Lab appearing as P1, P2, P3 (not paired correctly)

**Justification**:
- Labs require continuous block time for hands-on activities
- Splitting labs across non-consecutive periods disrupts practical work
- Two consecutive periods per lab ensures focused lab sessions

### 3. **Labs Cannot Cross Break Periods**
- **Rule**: Lab blocks cannot start at P2 or P4 (the periods before breaks)
- **Validation**: `can_place_lab()` prevents placement at:
  - Period 2 (would cross break into period 3)
  - Period 4 (would cross break into period 5)
- **Valid Lab Start Periods**: 1, 3, 5, 6

**Examples**:
- ✅ Valid: P1-P2 (both before break)
- ✅ Valid: P3-P4 (starts after first break)
- ✅ Valid: P5-P6 (starts after second break)
- ❌ Invalid: P2-P3 (crosses first break)
- ❌ Invalid: P4-P5 (crosses second break)

**Justification**:
- Breaks are designated for rest/refreshment
- Placing lab across a break disrupts the continuity needed for lab work
- Ensures labs happen in uninterrupted blocks during focused lab time

### 4. **Labs Cannot Start at P7**
- **Rule**: Labs need 2 consecutive periods; P7 is the last period, so no second period available
- **Validation**: `can_place_lab()` rejects period 7 for lab placement

**Justification**:
- No room for the required 2-period block
- P7 can only be used for single-period subjects

### 5. **Mandatory (last=true) Labs Must Be at P6-P7**
- **Rule**: Subjects with `last=true` flag (MC1, MC2, MP labs) must be scheduled at P6-P7 only
- **Validation**: `can_place_lab()` enforces:
  ```python
  if info.get("last", False):
      if period != 6:
          return False
  ```

**Justification**:
- Last classes should be at the end of the day for administrative reasons
- Ensures consistency in timetable structure
- MC1 and MC2 have special overlap rules that apply only at P6-P7

---

## Constraint Violations Fixed

### Issue 1: Labs with Odd Hours
**Previous Problem**: Algorithm allowed labs with 3, 5, 7, 9 hours
- Caused incomplete pairs (e.g., 3 hours = 1 pair + 1 single period)
- Led to verification errors

**Fix Applied**:
1. **UI Level**: Dropdown only shows even numbers for labs
2. **Backend Level**: `int()` conversion ensures proper type
3. **Algorithm Level**: `verify_lab_integrity()` rejects odd hours

### Issue 2: Labs in Single Periods
**Previous Problem**: Code allowed placing a single period for odd-hour labs
- Example: 3-hour lab → 2-period block + 1-period placement

**Fix Applied**:
- Removed single-period placement logic from `insertion_algorithm()`
- Removed fallback logic from `verify_lab_integrity()`
- Now ONLY places labs in complete 2-period blocks

### Issue 3: Labs Crossing Breaks
**Previous Problem**: Labs could be placed at P2-P3 or P4-P5
- Interrupted continuity across break periods

**Fix Applied**:
- `can_place_lab()` explicitly prevents P2 and P4 as starting positions
- Tests verify no lab crosses break positions

---

## Verification Process

When timetable is generated:

1. **Input Validation**: 
   - Check that all labs have even hours (enforced by UI dropdown)

2. **Placement Phase**:
   - Insertion algorithm places labs only in valid 2-period blocks
   - Respects all placement constraints

3. **Output Verification**:
   - `verify_lab_integrity()` confirms:
     - All labs have even hours
     - All labs appear in complete pairs
     - No labs cross breaks
     - Lab count matches hours

4. **Result**:
   - ✅ If all checks pass → Timetable is valid
   - ❌ If any check fails → Timetable is rejected with detailed error message

---

## Testing the Constraints

### Test Case 1: Even Hours Lab
```
Subject: "Physics Lab"
Hours: 4
Lab: Yes
Expected: 2 pairs placed in valid positions (P1-P2, P3-P4, P5-P6, or P6-P7)
```

### Test Case 2: Odd Hours Lab (Should Fail)
```
Subject: "Chemistry Lab"
Hours: 3
Lab: Yes
Expected: Rejected at UI (dropdown won't show 3)
```

### Test Case 3: Lab with Last Flag
```
Subject: "MC1"
Hours: 2
Lab: Yes
Last: Yes
Expected: ONLY placed at P6-P7
```

---

## Implementation Files

**Modified Files**:
1. `app/templates/add_subjects.html` - UI dropdown for even hours only
2. `server.py` - Backend int() conversion
3. `algorithm.py` - Removed odd-hour support, enforced pairs-only

**Key Functions**:
- `verify_lab_integrity()` - Final validation (lines 250-297)
- `can_place_lab()` - Placement rules (lines 363-408)
- `insertion_algorithm()` - Lab placement logic (lines 451-570)

---

## Conclusion

All lab constraints are now:
- ✅ Enforced at UI level (dropdown selection)
- ✅ Validated at backend level (type conversion)
- ✅ Checked at algorithm level (placement rules)
- ✅ Verified at output level (integrity checks)

This multi-layer approach ensures no lab constraint violations can occur.
