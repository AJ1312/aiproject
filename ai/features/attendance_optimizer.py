#!/usr/bin/env python3
"""
Attendance Optimizer - Offline AI Feature
Intelligent attendance planning for VIT 75% requirement
Uses algorithms to calculate optimal skip patterns and recovery plans
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.formatters import print_section, print_box


class AttendanceOptimizer:
    """Smart attendance optimization for VIT students"""
    
    def __init__(self, vtop_data: Dict):
        self.data = vtop_data
        self.attendance = vtop_data.get('attendance', [])
        self.min_attendance = 75.0  # VIT requirement
        
    def calculate_skip_buffer(self, attended: int, total: int) -> Dict:
        """
        Calculate how many classes can be skipped while staying above 75%
        
        Args:
            attended: Classes attended
            total: Total classes conducted
            
        Returns:
            Dictionary with skip analysis
        """
        current_pct = (attended / total * 100) if total > 0 else 0
        
        # Calculate buffer - classes that can be missed
        buffer = 0
        temp_attended = attended
        temp_total = total
        
        while True:
            temp_total += 1
            projected_pct = (temp_attended / temp_total * 100)
            if projected_pct < self.min_attendance:
                break
            buffer += 1
        
        # Calculate classes needed to recover if below 75%
        recovery_classes = 0
        if current_pct < self.min_attendance:
            temp_attended = attended
            temp_total = total
            while (temp_attended / temp_total * 100) < self.min_attendance:
                temp_total += 1
                temp_attended += 1
                recovery_classes += 1
        
        return {
            'current_percentage': round(current_pct, 2),
            'buffer_classes': buffer,
            'status': 'SAFE' if current_pct >= 85 else 'WARNING' if current_pct >= 75 else 'CRITICAL',
            'recovery_needed': recovery_classes,
            'can_skip': buffer > 0,
            'recommendation': self._get_recommendation(current_pct, buffer)
        }
    
    def _get_recommendation(self, pct: float, buffer: int) -> str:
        """Get smart recommendation based on attendance"""
        if pct >= 85:
            return f"You're doing great! You can safely skip up to {buffer} classes."
        elif pct >= 80:
            return f"Good attendance. You have {buffer} buffer classes."
        elif pct >= 75:
            return "You're at the minimum. Attend all future classes!"
        else:
            return "CRITICAL! Attend continuously to recover."
    
    def optimize_skip_pattern(self, attended: int, total: int, future_classes: int = 20) -> Dict:
        """
        Calculate optimal skip pattern for future classes
        
        Args:
            attended: Current attendance
            total: Total classes so far
            future_classes: Number of future classes to plan
            
        Returns:
            Skip pattern with dates
        """
        current_pct = (attended / total * 100) if total > 0 else 0
        
        # Calculate how many classes can be skipped in next N classes
        skip_opportunities = []
        
        for i in range(1, future_classes + 1):
            # If we skip this class
            temp_attended = attended
            temp_total = total + i
            projected_pct = (temp_attended / temp_total * 100)
            
            if projected_pct >= self.min_attendance:
                skip_opportunities.append({
                    'class_number': total + i,
                    'can_skip': True,
                    'projected_percentage': round(projected_pct, 2)
                })
            else:
                skip_opportunities.append({
                    'class_number': total + i,
                    'can_skip': False,
                    'projected_percentage': round(projected_pct, 2)
                })
            
            # If we attended
            if not skip_opportunities[-1]['can_skip']:
                attended += 1
        
        # Calculate optimal pattern
        max_skips = sum(1 for x in skip_opportunities if x['can_skip'])
        
        return {
            'future_classes': future_classes,
            'max_safe_skips': max_skips,
            'must_attend': future_classes - max_skips,
            'skip_pattern': skip_opportunities,
            'advice': f"Out of next {future_classes} classes, you can skip max {max_skips} classes"
        }
    
    def recovery_plan(self, attended: int, total: int, target_pct: float = 75.0) -> Dict:
        """
        Create recovery plan to reach target attendance
        
        Args:
            attended: Current attendance
            total: Total classes
            target_pct: Target percentage to achieve
            
        Returns:
            Recovery plan with timeline
        """
        current_pct = (attended / total * 100) if total > 0 else 0
        
        if current_pct >= target_pct:
            return {
                'needs_recovery': False,
                'current': round(current_pct, 2),
                'message': f"Already above {target_pct}%"
            }
        
        # Calculate classes needed
        classes_needed = 0
        temp_attended = attended
        temp_total = total
        
        while (temp_attended / temp_total * 100) < target_pct:
            temp_total += 1
            temp_attended += 1
            classes_needed += 1
        
        # Weekly plan (assuming 5 classes per week per course)
        weeks_needed = (classes_needed + 4) // 5
        
        return {
            'needs_recovery': True,
            'current': round(current_pct, 2),
            'target': target_pct,
            'classes_to_attend': classes_needed,
            'consecutive_weeks': weeks_needed,
            'final_percentage': round((temp_attended / temp_total * 100), 2),
            'plan': f"Attend {classes_needed} consecutive classes ({weeks_needed} weeks)",
            'motivation': "You got this! Consistency is key! 💪"
        }
    
    def analyze_all_courses(self) -> List[Dict]:
        """Analyze all courses and provide optimization"""
        results = []
        
        for course in self.attendance:
            code = course.get('course_code')
            name = course.get('course_name')
            attended = course.get('attended', 0)
            total = course.get('total', 0)
            
            if total == 0:
                continue
            
            # Calculate skip buffer
            skip_analysis = self.calculate_skip_buffer(attended, total)
            
            # Calculate optimal pattern for next 15 classes
            skip_pattern = self.optimize_skip_pattern(attended, total, future_classes=15)
            
            # Recovery plan if needed
            recovery = self.recovery_plan(attended, total)
            
            results.append({
                'course_code': code,
                'course_name': name,
                'attended': attended,
                'total': total,
                'skip_analysis': skip_analysis,
                'skip_pattern': skip_pattern,
                'recovery': recovery
            })
        
        # Sort by status (CRITICAL first)
        results.sort(key=lambda x: (
            0 if x['skip_analysis']['status'] == 'CRITICAL' else
            1 if x['skip_analysis']['status'] == 'WARNING' else 2
        ))
        
        return results


def main():
    """Run attendance optimizer"""
    from vtop_data_manager import get_vtop_data
    
    print("=" * 70)
    print("📊 ATTENDANCE OPTIMIZER - VIT 75% Requirement")
    print("=" * 70)
    print()
    
    data = get_vtop_data(use_cache=True)
    optimizer = AttendanceOptimizer(data)
    
    results = optimizer.analyze_all_courses()
    
    if not results:
        print("⚠️  No attendance data available")
        return
    
    # Summary statistics
    critical = sum(1 for r in results if r['skip_analysis']['status'] == 'CRITICAL')
    warning = sum(1 for r in results if r['skip_analysis']['status'] == 'WARNING')
    safe = sum(1 for r in results if r['skip_analysis']['status'] == 'SAFE')
    
    print(f"📈 Overall Status:")
    print(f"   🔴 Critical: {critical} courses")
    print(f"   🟡 Warning: {warning} courses")
    print(f"   🟢 Safe: {safe} courses")
    print()
    
    # Detailed analysis
    for result in results:
        course = result['course_name']
        code = result['course_code']
        analysis = result['skip_analysis']
        pattern = result['skip_pattern']
        recovery = result['recovery']
        
        status_emoji = '🔴' if analysis['status'] == 'CRITICAL' else '🟡' if analysis['status'] == 'WARNING' else '🟢'
        
        print(f"\n{status_emoji} {course} ({code})")
        print(f"   Current: {analysis['current_percentage']}% ({result['attended']}/{result['total']})")
        print(f"   Status: {analysis['status']}")
        
        if recovery['needs_recovery']:
            print(f"   ⚠️  Recovery: {recovery['plan']}")
            print(f"   🎯 {recovery['motivation']}")
        else:
            print(f"   ✅ Buffer: Can skip {analysis['buffer_classes']} classes")
            print(f"   📅 Next 15 classes: Can skip {pattern['max_safe_skips']}, must attend {pattern['must_attend']}")
        
        print(f"   💡 {analysis['recommendation']}")
    
    print("\n" + "=" * 70)
    print("Tip: Use this to plan your semester strategically!")
    print("=" * 70)


if __name__ == '__main__':
    main()
