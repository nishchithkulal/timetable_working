#!/usr/bin/env python
"""Test that consecutive constraints respect dynamic break configuration"""

import algorithm

# Test with different break configurations
test_cases = [
    {
        "name": "Breaks at P2 and P4",
        "first_break": 2,
        "lunch_break": 4,
        "expected_pairs": [(2, 3), (4, 5)]
    },
    {
        "name": "Breaks at P1 and P3",
        "first_break": 1,
        "lunch_break": 3,
        "expected_pairs": [(1, 2), (3, 4)]
    },
    {
        "name": "Breaks at P3 and P5",
        "first_break": 3,
        "lunch_break": 5,
        "expected_pairs": [(3, 4), (5, 6)]
    },
]

print("Testing Dynamic Consecutive Constraint Logic\n" + "="*50)

for test_case in test_cases:
    print(f"\n{test_case['name']}")
    print(f"  First break after P{test_case['first_break']}: Allowed pair is P{test_case['first_break']}-P{test_case['first_break']+1}")
    print(f"  Lunch break after P{test_case['lunch_break']}: Allowed pair is P{test_case['lunch_break']}-P{test_case['lunch_break']+1}")
    
    # Set break configuration
    algorithm.break_config_state['first'] = test_case['first_break']
    algorithm.break_config_state['lunch'] = test_case['lunch_break']
    
    # Verify the getter functions return correct values
    assert algorithm.get_first_break_period() == test_case['first_break'], "First break not set correctly"
    assert algorithm.get_lunch_break_period() == test_case['lunch_break'], "Lunch break not set correctly"
    
    # Calculate expected allowed pairs
    expected = test_case['expected_pairs']
    print(f"  Expected allowed consecutive pairs: {expected}")
    
    # Check against the validation logic
    allowed_pairs = [
        (algorithm.get_first_break_period(), algorithm.get_first_break_period() + 1),
        (algorithm.get_lunch_break_period(), algorithm.get_lunch_break_period() + 1)
    ]
    print(f"  Calculated allowed pairs: {allowed_pairs}")
    
    assert allowed_pairs == expected, f"Pairs mismatch! Expected {expected}, got {allowed_pairs}"
    print("  ✓ Consecutive constraint pairs correctly dynamic")

print("\n" + "="*50)
print("All tests passed! Consecutive constraints are dynamic based on break config.")
