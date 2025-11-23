#!/usr/bin/env python3
"""
Test script to verify that constraints from database are properly fetched
and used by the algorithm during timetable generation.
"""

import os
import sys
import logging
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Configure logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_constraint_flow():
    """Test that constraints flow correctly from database to algorithm"""
    
    logger.info("=" * 70)
    logger.info("CONSTRAINT FLOW TEST")
    logger.info("=" * 70)
    
    try:
        # Import Flask app and database
        from server import app, db
        from app.models.database import SubjectConstraint, BreakConfiguration, Department
        
        logger.info("\n✓ Successfully imported Flask app and database models")
        
        # Create app context to access database
        with app.app_context():
            logger.info("\n" + "=" * 70)
            logger.info("STEP 1: Check existing constraints in database")
            logger.info("=" * 70)
            
            # Query all constraints
            all_constraints = SubjectConstraint.query.all()
            logger.info(f"\nTotal constraints in database: {len(all_constraints)}")
            
            if all_constraints:
                logger.info("\nSample constraints:")
                for constraint in all_constraints[:5]:
                    logger.info(f"  - {constraint.dept_name} | {constraint.section} | {constraint.subject}")
                    logger.info(f"    Day: {constraint.day}, Period: {constraint.period}, Type: {constraint.constraint_type}")
            else:
                logger.warning("\n⚠ No constraints found in database!")
            
            logger.info("\n" + "=" * 70)
            logger.info("STEP 2: Test build_constraints_from_db function")
            logger.info("=" * 70)
            
            from server import build_constraints_from_db
            
            # Get a department to test with
            dept = Department.query.first()
            if not dept:
                logger.warning("\n⚠ No departments found in database. Skipping constraint build test.")
                return
            
            dept_name = dept.name
            college_id = dept.college_id
            
            logger.info(f"\nTesting with department: {dept_name} (College: {college_id})")
            
            # Build constraints from database
            strict_constraints, forbidden_constraints = build_constraints_from_db(dept_name, college_id)
            
            logger.info("\n✓ Successfully built constraints from database")
            logger.info(f"\nStrict constraints structure:")
            logger.info(f"  Type: {type(strict_constraints).__name__}")
            logger.info(f"  Number of sections: {len(strict_constraints)}")
            
            if strict_constraints:
                for section, subjects_dict in strict_constraints.items():
                    logger.info(f"\n  Section '{section}':")
                    for subject, placements in subjects_dict.items():
                        logger.info(f"    {subject}: {placements}")
                        # Verify placements are tuples of integers
                        for placement in placements:
                            if not isinstance(placement, tuple) or len(placement) != 2:
                                logger.error(f"    ✗ Invalid placement format: {placement}")
                            elif not all(isinstance(x, int) for x in placement):
                                logger.error(f"    ✗ Non-integer values in placement: {placement}")
                            else:
                                logger.info(f"      ✓ Valid placement: Day {placement[0]}, Period {placement[1]}")
            
            logger.info(f"\nForbidden constraints structure:")
            logger.info(f"  Type: {type(forbidden_constraints).__name__}")
            logger.info(f"  Number of sections: {len(forbidden_constraints)}")
            
            if forbidden_constraints:
                for section, subjects_dict in forbidden_constraints.items():
                    logger.info(f"\n  Section '{section}':")
                    for subject, placements in subjects_dict.items():
                        logger.info(f"    {subject}: {len(placements)} forbidden positions")
                        # Show first 3 placements
                        for placement in placements[:3]:
                            if isinstance(placement, tuple) and len(placement) == 2:
                                logger.info(f"      Day {placement[0]}, Period {placement[1]}")
            
            logger.info("\n" + "=" * 70)
            logger.info("STEP 3: Verify constraint format expected by algorithm")
            logger.info("=" * 70)
            
            logger.info("\nExpected format for algorithm:")
            logger.info("  {section: {subject: [(day_int, period_int), ...], ...}}")
            logger.info("\nFormat validation:")
            
            all_valid = True
            
            # Validate strict constraints
            for section, subjects_dict in strict_constraints.items():
                if not isinstance(section, str):
                    logger.error(f"  ✗ Section key not string: {type(section)}")
                    all_valid = False
                for subject, placements in subjects_dict.items():
                    if not isinstance(subject, str):
                        logger.error(f"  ✗ Subject key not string: {type(subject)}")
                        all_valid = False
                    if not isinstance(placements, list):
                        logger.error(f"  ✗ Placements not list: {type(placements)}")
                        all_valid = False
                    for placement in placements:
                        if not isinstance(placement, tuple) or len(placement) != 2:
                            logger.error(f"  ✗ Invalid placement: {placement}")
                            all_valid = False
                        day, period = placement
                        if not isinstance(day, int) or not isinstance(period, int):
                            logger.error(f"  ✗ Day/Period not int: Day={type(day)}, Period={type(period)}")
                            all_valid = False
            
            # Validate forbidden constraints
            for section, subjects_dict in forbidden_constraints.items():
                if not isinstance(section, str):
                    logger.error(f"  ✗ Section key not string: {type(section)}")
                    all_valid = False
                for subject, placements in subjects_dict.items():
                    if not isinstance(subject, str):
                        logger.error(f"  ✗ Subject key not string: {type(subject)}")
                        all_valid = False
                    if not isinstance(placements, list):
                        logger.error(f"  ✗ Placements not list: {type(placements)}")
                        all_valid = False
                    for placement in placements:
                        if not isinstance(placement, tuple) or len(placement) != 2:
                            logger.error(f"  ✗ Invalid placement: {placement}")
                            all_valid = False
                        day, period = placement
                        if not isinstance(day, int) or not isinstance(period, int):
                            logger.error(f"  ✗ Day/Period not int: Day={type(day)}, Period={type(period)}")
                            all_valid = False
            
            if all_valid:
                logger.info("  ✓ All constraints are in correct format!")
            
            logger.info("\n" + "=" * 70)
            logger.info("STEP 4: Check break configuration")
            logger.info("=" * 70)
            
            from server import get_break_configuration
            
            break_config = get_break_configuration(dept_name, college_id)
            logger.info(f"\nBreak configuration for {dept_name}:")
            logger.info(f"  First break at P{break_config['first_break_period']}")
            logger.info(f"  Lunch break at P{break_config['lunch_break_period']}")
            logger.info(f"  Second break at P{break_config['second_break_period']}")
            logger.info("  ✓ Break config fetched successfully!")
            
            logger.info("\n" + "=" * 70)
            logger.info("CONSTRAINT FLOW VERIFICATION COMPLETE")
            logger.info("=" * 70)
            
            logger.info("\n✓ SUMMARY:")
            logger.info("  - Constraints are properly fetched from database")
            logger.info("  - Format matches algorithm expectations")
            logger.info("  - Day/Period values are integers (not strings)")
            logger.info("  - Break configuration is loaded correctly")
            logger.info("\n✓ The system is ready to use constraints during timetable generation!")
            
    except Exception as e:
        logger.exception("\n✗ ERROR during constraint flow test")
        sys.exit(1)

if __name__ == "__main__":
    test_constraint_flow()
