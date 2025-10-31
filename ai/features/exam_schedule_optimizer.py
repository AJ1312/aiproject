#!/usr/bin/env python3
"""
Exam Schedule Optimizer - Offline AI Feature
Intelligent exam preparation planning for VIT students
Optimizes study time based on exam gaps and difficulty
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.formatters import print_section, print_box


class ExamScheduleOptimizer:
    """Smart exam schedule and study plan optimizer"""
    
    def __init__(self, vtop_data: Dict):
        self.data = vtop_data
        self.exams = vtop_data.get('exams', [])
        self.marks = vtop_data.get('marks', [])
        self.attendance = vtop_data.get('attendance', [])
    
    def parse_exam_date(self, date_str: str) -> datetime:
        """Parse exam date string to datetime"""
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except:
            return datetime.now()
    
    def calculate_exam_gaps(self) -> List[Dict]:
        """Calculate gaps between consecutive exams"""
        if not self.exams:
            return []
        
        # Sort exams by date
        sorted_exams = sorted(self.exams, key=lambda x: self.parse_exam_date(x.get('date', '')))
        
        gaps = []
        for i in range(len(sorted_exams) - 1):
            current = sorted_exams[i]
            next_exam = sorted_exams[i + 1]
            
            current_date = self.parse_exam_date(current.get('date', ''))
            next_date = self.parse_exam_date(next_exam.get('date', ''))
            
            gap_days = (next_date - current_date).days
            
            gaps.append({
                'exam_1': current.get('course_name'),
                'exam_2': next_exam.get('course_name'),
                'gap_days': gap_days,
                'intensity': 'HIGH' if gap_days <= 1 else 'MEDIUM' if gap_days <= 3 else 'LOW'
            })
        
        return gaps
    
    def calculate_course_difficulty(self, course_code: str) -> Dict:
        """
        Calculate course difficulty based on multiple factors
        
        Factors:
        - Current performance (low marks = high difficulty)
        - Attendance (low attendance = needs more prep)
        - Number of topics (assumed from syllabus if available)
        """
        difficulty_score = 0
        factors = []
        
        # Check marks
        for course in self.marks:
            if course.get('course_code') == course_code:
                total_scored = course.get('total_scored', 0)
                total_weight = course.get('total_weight', 40)
                percentage = (total_scored / total_weight * 100) if total_weight > 0 else 0
                
                if percentage < 60:
                    difficulty_score += 3
                    factors.append("Low internal marks")
                elif percentage < 75:
                    difficulty_score += 2
                    factors.append("Moderate internal marks")
                else:
                    difficulty_score += 1
                break
        
        # Check attendance
        for att in self.attendance:
            if att.get('course_code') == course_code:
                pct = att.get('percentage', 100)
                if pct < 75:
                    difficulty_score += 3
                    factors.append("Low attendance - more catchup needed")
                elif pct < 85:
                    difficulty_score += 1
                    factors.append("Moderate attendance")
                break
        
        # Classify difficulty
        if difficulty_score >= 5:
            level = 'HARD'
        elif difficulty_score >= 3:
            level = 'MEDIUM'
        else:
            level = 'EASY'
        
        return {
            'difficulty_score': difficulty_score,
            'level': level,
            'factors': factors
        }
    
    def optimize_study_allocation(self, total_study_hours: int = 100) -> List[Dict]:
        """
        Allocate study hours based on exam schedule and difficulty
        
        Args:
            total_study_hours: Total hours available for study
            
        Returns:
            Optimized study plan
        """
        if not self.exams:
            return []
        
        # Calculate difficulty for each exam
        exam_analysis = []
        total_difficulty = 0
        
        for exam in self.exams:
            code = exam.get('course_code')
            name = exam.get('course_name')
            date = exam.get('date')
            
            difficulty = self.calculate_course_difficulty(code)
            days_until = (self.parse_exam_date(date) - datetime.now()).days
            
            # Weight by difficulty and urgency
            urgency_weight = max(1, 10 - days_until) if days_until >= 0 else 1
            combined_score = difficulty['difficulty_score'] * urgency_weight
            total_difficulty += combined_score
            
            exam_analysis.append({
                'course_code': code,
                'course_name': name,
                'date': date,
                'days_until': days_until,
                'difficulty': difficulty,
                'urgency_weight': urgency_weight,
                'combined_score': combined_score
            })
        
        # Allocate hours proportionally
        study_plan = []
        for exam in sorted(exam_analysis, key=lambda x: x['date']):
            proportion = exam['combined_score'] / total_difficulty if total_difficulty > 0 else 0
            allocated_hours = round(proportion * total_study_hours, 1)
            
            # Daily recommendation
            days_available = max(1, exam['days_until'])
            hours_per_day = round(allocated_hours / days_available, 1) if days_available > 0 else allocated_hours
            
            study_plan.append({
                'course_code': exam['course_code'],
                'course_name': exam['course_name'],
                'date': exam['date'],
                'days_until': exam['days_until'],
                'difficulty': exam['difficulty']['level'],
                'total_hours': allocated_hours,
                'hours_per_day': hours_per_day,
                'priority': 'HIGH' if exam['difficulty']['level'] == 'HARD' else
                           'MEDIUM' if exam['difficulty']['level'] == 'MEDIUM' else 'LOW',
                'recommendation': self._get_study_recommendation(exam['difficulty']['level'], 
                                                                 days_available)
            })
        
        return study_plan
    
    def _get_study_recommendation(self, difficulty: str, days: int) -> str:
        """Get study recommendation"""
        if difficulty == 'HARD':
            if days <= 3:
                return "⚠️ URGENT! Intensive study needed. Focus on key topics."
            elif days <= 7:
                return "High priority. Cover all topics systematically."
            else:
                return "Start early. Build strong fundamentals."
        elif difficulty == 'MEDIUM':
            if days <= 3:
                return "Important. Quick revision of all topics."
            else:
                return "Moderate effort needed. Practice problems."
        else:
            if days <= 3:
                return "Quick revision should be sufficient."
            else:
                return "Low pressure. Light revision recommended."
    
    def identify_crunch_periods(self) -> List[Dict]:
        """Identify periods with multiple exams close together"""
        if len(self.exams) < 2:
            return []
        
        sorted_exams = sorted(self.exams, key=lambda x: self.parse_exam_date(x.get('date', '')))
        crunch_periods = []
        
        i = 0
        while i < len(sorted_exams):
            current_date = self.parse_exam_date(sorted_exams[i].get('date', ''))
            cluster = [sorted_exams[i]]
            
            # Find exams within 3 days
            j = i + 1
            while j < len(sorted_exams):
                next_date = self.parse_exam_date(sorted_exams[j].get('date', ''))
                if (next_date - current_date).days <= 3:
                    cluster.append(sorted_exams[j])
                    j += 1
                else:
                    break
            
            if len(cluster) >= 2:
                crunch_periods.append({
                    'start_date': sorted_exams[i].get('date'),
                    'end_date': cluster[-1].get('date'),
                    'num_exams': len(cluster),
                    'exams': [{'code': e.get('course_code'), 'name': e.get('course_name')} 
                             for e in cluster],
                    'stress_level': 'HIGH' if len(cluster) >= 3 else 'MEDIUM'
                })
            
            i = j if j > i + 1 else i + 1
        
        return crunch_periods


def main():
    """Run exam schedule optimizer"""
    from vtop_data_manager import get_vtop_data
    
    print("=" * 70)
    print("📅 EXAM SCHEDULE OPTIMIZER - VIT Smart Study Planning")
    print("=" * 70)
    print()
    
    data = get_vtop_data(use_cache=True)
    optimizer = ExamScheduleOptimizer(data)
    
    if not optimizer.exams:
        print("⚠️  No exam data available")
        return
    
    # Exam gaps analysis
    print_section("EXAM SCHEDULE ANALYSIS")
    gaps = optimizer.calculate_exam_gaps()
    
    print(f"Total Exams: {len(optimizer.exams)}")
    print()
    
    if gaps:
        print("Exam Gaps:")
        for gap in gaps:
            emoji = '🔴' if gap['intensity'] == 'HIGH' else '🟡' if gap['intensity'] == 'MEDIUM' else '🟢'
            print(f"  {emoji} {gap['exam_1']} → {gap['exam_2']}: {gap['gap_days']} days ({gap['intensity']})")
    
    print()
    
    # Crunch periods
    crunch = optimizer.identify_crunch_periods()
    if crunch:
        print_section("⚠️ CRUNCH PERIODS (Multiple Exams Close Together)")
        for period in crunch:
            print(f"\n{period['start_date']} to {period['end_date']}")
            print(f"  Stress Level: {period['stress_level']}")
            print(f"  Exams ({period['num_exams']}):")
            for exam in period['exams']:
                print(f"    • {exam['name']} ({exam['code']})")
    
    print()
    
    # Optimized study plan
    print_section("OPTIMIZED STUDY PLAN (100 hours total)")
    study_plan = optimizer.optimize_study_allocation(total_study_hours=100)
    
    for plan in study_plan:
        priority_emoji = '🔴' if plan['priority'] == 'HIGH' else '🟡' if plan['priority'] == 'MEDIUM' else '🟢'
        
        print(f"\n{priority_emoji} {plan['course_name']} ({plan['course_code']})")
        print(f"  Date: {plan['date']} (in {plan['days_until']} days)")
        print(f"  Difficulty: {plan['difficulty']}")
        print(f"  Allocated Time: {plan['total_hours']} hours total")
        print(f"  Daily: {plan['hours_per_day']} hours/day")
        print(f"  💡 {plan['recommendation']}")
    
    print("\n" + "=" * 70)
    print("Pro Tip: Adjust hours based on your understanding of each subject!")
    print("=" * 70)


if __name__ == '__main__':
    main()
