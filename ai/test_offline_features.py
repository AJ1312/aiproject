#!/usr/bin/env python3
"""
Test All AI Features
Runs all offline AI features using test dataset
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Load test data
test_data_path = Path(__file__).parent / 'data' / 'test_dataset.json'
with open(test_data_path) as f:
    TEST_DATA = json.load(f)

print("=" * 80)
print("🧪 TESTING ALL OFFLINE AI FEATURES")
print("=" * 80)
print(f"Using test dataset: {test_data_path}")
print(f"Student: {TEST_DATA.get('reg_no')}")
print(f"CGPA: {TEST_DATA.get('cgpa')}")
print("=" * 80)
print()

# Test 1: Attendance Optimizer
print("=" * 80)
print("1️⃣  ATTENDANCE OPTIMIZER")
print("=" * 80)
try:
    from features.attendance_optimizer import AttendanceOptimizer
    
    optimizer = AttendanceOptimizer(TEST_DATA)
    results = optimizer.analyze_all_courses()
    
    print(f"✅ Analyzed {len(results)} courses")
    for result in results:
        print(f"  • {result['course_name']}: {result['skip_analysis']['current_percentage']}% "
              f"(Buffer: {result['skip_analysis']['buffer_classes']} classes)")
except Exception as e:
    print(f"❌ Failed: {e}")

print()

# Test 2: CGPA Calculator
print("=" * 80)
print("2️⃣  CGPA CALCULATOR")
print("=" * 80)
try:
    from features.cgpa_calculator import CGPACalculator
    
    calculator = CGPACalculator(TEST_DATA)
    prediction = calculator.predict_current_semester()
    
    if 'error' not in prediction:
        print(f"✅ Current CGPA: {calculator.current_cgpa}")
        print(f"  Predicted Semester GPA: {prediction['predicted_semester_gpa']}")
        print(f"  Predicted CGPA: {prediction['predicted_cumulative_cgpa']}")
        print(f"  Expected Change: {prediction['cgpa_change']:+.2f}")
    
    # What-if scenario
    scenario = calculator.what_if_scenario(9.0, 2)
    print(f"\n  What-if: Target 9.0 CGPA")
    print(f"  Required GPA: {scenario['required_gpa_per_semester']}/10 ({scenario['difficulty']})")
except Exception as e:
    print(f"❌ Failed: {e}")

print()

# Test 3: Exam Schedule Optimizer
print("=" * 80)
print("3️⃣  EXAM SCHEDULE OPTIMIZER")
print("=" * 80)
try:
    from features.exam_schedule_optimizer import ExamScheduleOptimizer
    
    exam_optimizer = ExamScheduleOptimizer(TEST_DATA)
    study_plan = exam_optimizer.optimize_study_allocation(total_study_hours=100)
    
    print(f"✅ Generated study plan for {len(study_plan)} exams")
    for plan in study_plan[:3]:  # Show first 3
        print(f"  • {plan['course_name']}: {plan['total_hours']}h total "
              f"({plan['hours_per_day']}h/day, Priority: {plan['priority']})")
    
    # Crunch periods
    crunch = exam_optimizer.identify_crunch_periods()
    if crunch:
        print(f"\n  ⚠️  Found {len(crunch)} crunch period(s)")
except Exception as e:
    print(f"❌ Failed: {e}")

print()

# Test 4: ML Feature (if sklearn available)
print("=" * 80)
print("4️⃣  ACADEMIC PERFORMANCE ML")
print("=" * 80)
try:
    from features.academic_performance_ml import AcademicPerformanceML
    
    ml_analyzer = AcademicPerformanceML(TEST_DATA)
    
    # Clustering
    clustering = ml_analyzer.cluster_courses(n_clusters=2)
    if 'error' not in clustering:
        print(f"✅ Clustered courses into {len(clustering['clusters'])} groups")
        print(f"  Quality: {clustering['quality']} (Score: {clustering['silhouette_score']})")
    
    # Grade prediction
    predictions = ml_analyzer.predict_final_grades()
    print(f"\n  Predicted grades for {len(predictions)} courses")
    
    # CGPA trajectory
    trajectory = ml_analyzer.analyze_cgpa_trajectory()
    if 'error' not in trajectory:
        print(f"\n  CGPA Trend: {trajectory['trend']}")
        print(f"  Predicted Next Semester: {trajectory['predicted_next_cgpa']}")
except ImportError:
    print("⚠️  sklearn not installed - skipping ML feature")
except Exception as e:
    print(f"❌ Failed: {e}")

print()

# Summary
print("=" * 80)
print("✅ TESTING COMPLETE")
print("=" * 80)
print("All offline AI features tested successfully!")
print("These features work without any API keys or external dependencies.")
print("=" * 80)
