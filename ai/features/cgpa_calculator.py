#!/usr/bin/env python3
"""
CGPA Calculator with What-If Scenarios - Offline AI Feature
VIT-specific grade calculations with scenario planning
Uses VIT grading system and credit calculations
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.formatters import print_section, print_box


class CGPACalculator:
    """VIT CGPA calculator with what-if scenarios"""
    
    # VIT Grading System
    GRADE_POINTS = {
        'S': 10, 'A': 9, 'B': 8, 'C': 7, 'D': 6,
        'E': 5, 'F': 0, 'N': 0, 'W': 0
    }
    
    # Mark to grade conversion (VIT system)
    MARK_TO_GRADE = [
        (90, 'S'), (80, 'A'), (70, 'B'), (60, 'C'),
        (50, 'D'), (40, 'E'), (0, 'F')
    ]
    
    def __init__(self, vtop_data: Dict):
        self.data = vtop_data
        self.current_cgpa = vtop_data.get('cgpa', 0)
        self.cgpa_trend = vtop_data.get('cgpa_trend', [])
        self.marks = vtop_data.get('marks', [])
    
    def marks_to_grade(self, marks: float) -> str:
        """Convert marks to VIT grade"""
        for threshold, grade in self.MARK_TO_GRADE:
            if marks >= threshold:
                return grade
        return 'F'
    
    def calculate_semester_gpa(self, grades: List[Tuple[str, int]]) -> float:
        """
        Calculate GPA for a semester
        
        Args:
            grades: List of (grade, credits) tuples
            
        Returns:
            GPA for the semester
        """
        total_points = 0
        total_credits = 0
        
        for grade, credits in grades:
            points = self.GRADE_POINTS.get(grade, 0)
            total_points += points * credits
            total_credits += credits
        
        return total_points / total_credits if total_credits > 0 else 0
    
    def calculate_cumulative_cgpa(self, semester_gpas: List[Tuple[float, int]]) -> float:
        """
        Calculate cumulative CGPA
        
        Args:
            semester_gpas: List of (gpa, credits) tuples for each semester
            
        Returns:
            Cumulative CGPA
        """
        total_points = 0
        total_credits = 0
        
        for gpa, credits in semester_gpas:
            total_points += gpa * credits
            total_credits += credits
        
        return total_points / total_credits if total_credits > 0 else 0
    
    def what_if_scenario(self, target_cgpa: float, remaining_semesters: int, 
                        credits_per_sem: int = 24) -> Dict:
        """
        Calculate required GPA for target CGPA
        
        Args:
            target_cgpa: Desired CGPA
            remaining_semesters: Number of semesters left
            credits_per_sem: Credits per semester (default: 24 for VIT)
            
        Returns:
            What-if analysis with required GPA
        """
        # Calculate current total credits and points
        total_credits = 0
        total_points = 0
        
        for sem in self.cgpa_trend:
            gpa = sem.get('cgpa', 0)
            credits = sem.get('credits_registered', 24)
            total_points += gpa * credits
            total_credits += credits
        
        # Calculate required points for target CGPA
        future_credits = remaining_semesters * credits_per_sem
        total_future_credits = total_credits + future_credits
        required_total_points = target_cgpa * total_future_credits
        required_future_points = required_total_points - total_points
        required_gpa = required_future_points / future_credits if future_credits > 0 else 0
        
        # Determine feasibility
        feasible = required_gpa <= 10.0
        difficulty = (
            'EASY' if required_gpa <= 8.0 else
            'MODERATE' if required_gpa <= 9.0 else
            'CHALLENGING' if required_gpa <= 9.5 else
            'VERY DIFFICULT' if required_gpa <= 10.0 else
            'IMPOSSIBLE'
        )
        
        return {
            'target_cgpa': target_cgpa,
            'current_cgpa': self.current_cgpa,
            'remaining_semesters': remaining_semesters,
            'required_gpa_per_semester': round(required_gpa, 2),
            'feasible': feasible,
            'difficulty': difficulty,
            'credits_needed': future_credits,
            'recommendation': self._get_scenario_recommendation(required_gpa, feasible)
        }
    
    def _get_scenario_recommendation(self, required_gpa: float, feasible: bool) -> str:
        """Get recommendation for scenario"""
        if not feasible:
            return "This target is not achievable. Consider a more realistic goal."
        elif required_gpa <= 8.0:
            return "Very achievable! Maintain consistent performance."
        elif required_gpa <= 9.0:
            return "Achievable with good effort. Focus on understanding concepts."
        elif required_gpa <= 9.5:
            return "Challenging but possible. Need excellent performance."
        else:
            return "Very difficult! Requires near-perfect grades in all courses."
    
    def predict_current_semester(self) -> Dict:
        """Predict current semester GPA based on marks"""
        if not self.marks:
            return {'error': 'No marks data available'}
        
        semester_grades = []
        course_predictions = []
        
        for course in self.marks:
            code = course.get('course_code')
            title = course.get('course_title')
            total_scored = course.get('total_scored', 0)
            total_weight = course.get('total_weight', 40)
            
            # Project to 100 (assuming total_weight is out of 40 for internals)
            # Final marks = internals (40%) + FAT (60%)
            # Assume student gets proportional marks in FAT
            internal_pct = (total_scored / total_weight * 100) if total_weight > 0 else 0
            projected_marks = (internal_pct * 0.4) + (internal_pct * 0.6)  # Conservative estimate
            
            predicted_grade = self.marks_to_grade(projected_marks)
            
            # Assume 3 credits for theory, 1 for lab
            credits = 1 if 'L' in code or 'Lab' in title else 3
            
            semester_grades.append((predicted_grade, credits))
            course_predictions.append({
                'course_code': code,
                'course_title': title,
                'current_internal': round(total_scored, 2),
                'projected_total': round(projected_marks, 2),
                'predicted_grade': predicted_grade,
                'credits': credits
            })
        
        # Calculate predicted GPA
        predicted_gpa = self.calculate_semester_gpa(semester_grades)
        
        # Calculate predicted CGPA
        semester_gpas = [(sem.get('cgpa', 0), sem.get('credits_registered', 24)) 
                        for sem in self.cgpa_trend]
        semester_gpas.append((predicted_gpa, sum(c for _, c in semester_grades)))
        
        predicted_cgpa = self.calculate_cumulative_cgpa(semester_gpas)
        
        return {
            'predicted_semester_gpa': round(predicted_gpa, 2),
            'predicted_cumulative_cgpa': round(predicted_cgpa, 2),
            'current_cgpa': self.current_cgpa,
            'cgpa_change': round(predicted_cgpa - self.current_cgpa, 2),
            'course_predictions': course_predictions
        }
    
    def grade_distribution_analysis(self) -> Dict:
        """Analyze grade distribution across semesters"""
        total_grades = {grade: 0 for grade in self.GRADE_POINTS.keys()}
        
        for sem in self.cgpa_trend:
            for grade in total_grades.keys():
                count = sem.get(f'{grade.lower()}_grades', 0)
                total_grades[grade] += count
        
        total_courses = sum(total_grades.values())
        
        distribution = {}
        for grade, count in total_grades.items():
            if count > 0:
                percentage = (count / total_courses * 100) if total_courses > 0 else 0
                distribution[grade] = {
                    'count': count,
                    'percentage': round(percentage, 1)
                }
        
        return {
            'total_courses': total_courses,
            'distribution': distribution,
            'most_common_grade': max(total_grades.items(), key=lambda x: x[1])[0],
            'excellence_rate': round(
                (total_grades.get('S', 0) + total_grades.get('A', 0)) / total_courses * 100, 1
            ) if total_courses > 0 else 0
        }


def main():
    """Run CGPA calculator"""
    from vtop_data_manager import get_vtop_data
    
    print("=" * 70)
    print("🎯 CGPA CALCULATOR - VIT Grading System")
    print("=" * 70)
    print()
    
    data = get_vtop_data(use_cache=True)
    calculator = CGPACalculator(data)
    
    # Current status
    print(f"📊 Current CGPA: {calculator.current_cgpa}")
    print()
    
    # Predict current semester
    print_section("CURRENT SEMESTER PREDICTION")
    prediction = calculator.predict_current_semester()
    
    if 'error' not in prediction:
        print(f"Predicted Semester GPA: {prediction['predicted_semester_gpa']}")
        print(f"Predicted Cumulative CGPA: {prediction['predicted_cumulative_cgpa']}")
        print(f"Expected Change: {prediction['cgpa_change']:+.2f}")
        print()
        
        print("Course-wise Predictions:")
        for course in prediction['course_predictions']:
            print(f"  {course['course_code']}: {course['predicted_grade']} "
                  f"(Projected: {course['projected_total']:.1f}/100)")
    
    print()
    
    # What-if scenarios
    print_section("WHAT-IF SCENARIOS")
    
    scenarios = [
        (9.0, 2, "Reach 9.0 CGPA"),
        (9.5, 2, "Reach 9.5 CGPA"),
        (8.5, 1, "Maintain 8.5 CGPA")
    ]
    
    for target, semesters, description in scenarios:
        analysis = calculator.what_if_scenario(target, semesters)
        
        print(f"\n{description} in {semesters} semester(s):")
        print(f"  Required GPA: {analysis['required_gpa_per_semester']}/10")
        print(f"  Difficulty: {analysis['difficulty']}")
        print(f"  Feasible: {'Yes ✅' if analysis['feasible'] else 'No ❌'}")
        print(f"  💡 {analysis['recommendation']}")
    
    print()
    
    # Grade distribution
    print_section("GRADE DISTRIBUTION ANALYSIS")
    distribution = calculator.grade_distribution_analysis()
    
    print(f"Total Courses: {distribution['total_courses']}")
    print(f"Most Common Grade: {distribution['most_common_grade']}")
    print(f"Excellence Rate (S+A): {distribution['excellence_rate']}%")
    print()
    print("Distribution:")
    for grade, data in sorted(distribution['distribution'].items(), 
                             key=lambda x: calculator.GRADE_POINTS[x[0]], reverse=True):
        bars = '█' * int(data['percentage'] / 5)
        print(f"  {grade}: {bars} {data['count']} ({data['percentage']}%)")
    
    print("\n" + "=" * 70)
    print("Use these scenarios to plan your academic goals!")
    print("=" * 70)


if __name__ == '__main__':
    main()
