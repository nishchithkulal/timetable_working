#!/usr/bin/env python3
"""Test that faculty consecutive gap constraint is integrated and working"""

import sys
sys.path.insert(0, '/c/Users/91988/timetable_working')

# Run the algorithm main
if __name__ == '__main__':
    from algorithm import main
    
    print("\n" + "=" * 80)
    print("RUNNING TIMETABLE GENERATION WITH FACULTY GAP CONSTRAINT")
    print("=" * 80)
    
    main()
    
    print("\n" + "=" * 80)
    print("CHECKING RESULTS FOR VIOLATIONS")
    print("=" * 80)
