# Dynamic Break Configuration Implementation

## Summary

The algorithm has been updated to fetch break configuration from the database (`BreakConfiguration` table) instead of using hard-coded values. Labs now respect the dynamic break periods when determining valid placement positions.

## Changes Made

### 1. **algorithm.py** - Global Variables Added
- Added `first_break_period = 2` (default)
- Added `lunch_break_period = 4` (default)
- These globals are set dynamically by `store_section_timetables()` from the `break_config` parameter

### 2. **store_section_timetables()** Function
- Now accepts `break_config` parameter from the database
- Sets global `first_break_period` and `lunch_break_period` dynamically
- Updates legacy `break_periods` dict for backward compatibility

```python
if break_config is not None:
    first_break_period = break_config.get('first_break_period', 2)
    lunch_break_period = break_config.get('lunch_break_period', 4)
```

### 3. **can_place_lab()** Function
- Updated to check against dynamic `first_break_period` and `lunch_break_period`
- Labs cannot start at period numbers that represent break positions
- Calculates valid lab starting periods dynamically based on break configuration

**Logic**: If break occurs after period X, labs cannot start at period X (would be interrupted)

### 4. **verify_lab_integrity()** Function
- Updated to detect lab placements that cross breaks using dynamic values
- Rejects labs that span periods where breaks occur in between

### 5. **check_consecutive_constraint()** Function
- Updated to calculate allowed consecutive pairs dynamically
- Non-lab subjects can only be consecutive at periods that cross breaks
- For example, with breaks at P2 and P4: allowed pairs are (2,3) and (4,5)

### 6. **get_preferred_lab_periods()** Function
- Updated to dynamically calculate valid lab starting periods
- Returns periods in priority order (preferred first, fallback last)
- Excludes break periods and invalid starting positions

## How It Works

### Example 1: Standard Configuration (breaks at P2, P4)
```
Display: P1 | P2 | [BREAK] | P3 | P4 | [BREAK] | P5 | P6 | P7

Valid lab placements:
  - P1-P2: VALID (break comes after)
  - P2-P3: INVALID (break interrupts)
  - P3-P4: VALID (break comes after)
  - P4-P5: INVALID (break interrupts)
  - P5-P6: VALID
  - P6-P7: VALID
```

### Example 2: Custom Configuration (breaks at P1, P3)
```
Display: P1 | [BREAK] | P2 | P3 | [BREAK] | P4 | P5 | P6 | P7

Valid lab placements:
  - P1-P2: INVALID (break interrupts)
  - P2-P3: VALID (break comes after)
  - P3-P4: INVALID (break interrupts)
  - P4-P5: VALID
  - P5-P6: VALID
  - P6-P7: VALID
```

## Database Integration

The `get_break_configuration()` function in `server.py` fetches break data:

```python
break_config = get_break_configuration(dept_name, college_id)
# Returns: {'first_break_period': 2, 'lunch_break_period': 4}
```

This is then passed to `store_section_timetables()`:

```python
section_timetables = store_section_timetables(
    section_list=sections,
    subjects_dict=subjects_per_section,
    faculty_dict=faculties,
    strict_constraints=strict_constraints,
    forbidden_constraints=forbidden_constraints,
    break_config=break_config  # From database
)
```

## Testing

Comprehensive tests verify the implementation:
- `test_dynamic_breaks.py`: Tests custom break configuration
- `test_break_comprehensive.py`: Tests multiple break scenarios

All scenarios correctly enforce lab placement constraints based on break positions.

## Backward Compatibility

- Default values maintained: `first_break_period = 2`, `lunch_break_period = 4`
- Legacy `break_periods` dict updated for any code that still uses it
- Algorithm works seamlessly with or without `break_config` parameter
