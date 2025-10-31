"""
Grade Predictor - Historical Pattern Based
Uses YOUR actual previous semester performance to predict future grades.
"""

import json
import os
from typing import Dict, List, Tuple


def load_current_semester_data():
    """Load current semester data."""
    data_file = os.path.join(os.path.dirname(__file__), '../current_semester_data.json')
    with open(data_file, 'r') as f:
        return json.load(f)


def load_historical_patterns():
    """Load historical grade patterns from previous semesters."""
    pattern_file = os.path.join(os.path.dirname(__file__), '../data/historical_grade_patterns.json')
    try:
        with open(pattern_file, 'r') as f:
            return json.load(f)
    except:
        return None


def get_grade_from_marks(total_marks: float) -> str:
    """Convert total marks to grade."""
    if total_marks >= 90:
        return 'S'
    elif total_marks >= 80:
        return 'A'
    elif total_marks >= 70:
        return 'B'
    elif total_marks >= 60:
        return 'C'
    elif total_marks >= 50:
        return 'D'
    else:
        return 'F'


def predict_from_historical_patterns(internal_percentage: float, subject_type: str, course_name: str) -> Tuple[Dict, List]:
    """
    Predict grade based on historical patterns from similar courses.
    Uses YOUR actual performance history to make realistic predictions.
    
    Args:
        internal_percentage: Current internal marks percentage (0-100)
        subject_type: Type of subject (CORE_CSE, MATH, CORE_ENGG, etc.)
        course_name: Name of the course
    
    Returns:
        (scenarios dict, list of closest historical matches)
    """
    historical_data = load_historical_patterns()
    
    if not historical_data or 'patterns_by_type' not in historical_data:
        # Fallback to simple calculation if no historical data
        return predict_three_scenarios_simple(internal_percentage)
    
    # Get courses of the same type from history
    similar_courses = historical_data['patterns_by_type'].get(subject_type, [])
    
    if not similar_courses:
        # Fallback if no similar courses found
        return predict_three_scenarios_simple(internal_percentage), []
    
    # Find the 3 closest matches by internal percentage
    sorted_courses = sorted(similar_courses, 
                           key=lambda x: abs(x['internal_percentage'] - internal_percentage))
    
    closest_matches = sorted_courses[:min(3, len(sorted_courses))]  # Top 3 similar courses
    
    # Calculate scenarios based on historical patterns
    scenarios = {}
    
    # OPTIMISTIC: Best case from similar internal marks
    best_match = max(closest_matches, key=lambda x: x['total_marks'])
    internal_current = (internal_percentage / 100) * 60
    fat_opt = best_match['total_marks'] - internal_current
    fat_opt = max(20, min(40, fat_opt))  # Clamp between 20-40
    
    scenarios['optimistic'] = {
        'fat_marks': round(fat_opt, 1),
        'fat_percentage': round((fat_opt / 40) * 100, 1),
        'total': round(internal_current + fat_opt, 1),
        'grade': best_match['grade'],
        'reference': f"{best_match['course_name'][:30]} ({best_match.get('semester', 'N/A')[:17]})",
        'historical_internal': best_match['internal_percentage']
    }
    
    # REALISTIC: Average of closest matches
    avg_fat = sum(c['fat_marks'] for c in closest_matches) / len(closest_matches)
    avg_total = sum(c['total_marks'] for c in closest_matches) / len(closest_matches)
    avg_grade_points = sum({'S': 10, 'A': 9, 'B': 8, 'C': 7, 'D': 6, 'E': 5, 'F': 0}.get(c['grade'], 0) 
                           for c in closest_matches) / len(closest_matches)
    
    # Map average grade points back to letter grade
    if avg_grade_points >= 9.5:
        avg_grade = 'S'
    elif avg_grade_points >= 8.5:
        avg_grade = 'A'
    elif avg_grade_points >= 7.5:
        avg_grade = 'B'
    elif avg_grade_points >= 6.5:
        avg_grade = 'C'
    elif avg_grade_points >= 5.5:
        avg_grade = 'D'
    else:
        avg_grade = 'F'
    
    scenarios['realistic'] = {
        'fat_marks': round(avg_fat, 1),
        'fat_percentage': round((avg_fat / 40) * 100, 1),
        'total': round(avg_total, 1),
        'grade': avg_grade,
        'reference': f"Avg of {len(closest_matches)} similar {subject_type} courses",
        'historical_internal': round(sum(c['internal_percentage'] for c in closest_matches) / len(closest_matches), 1)
    }
    
    # PESSIMISTIC: Worst case from similar internal marks
    worst_match = min(closest_matches, key=lambda x: x['total_marks'])
    fat_pess = worst_match['total_marks'] - internal_current
    fat_pess = max(20, min(40, fat_pess))
    
    scenarios['pessimistic'] = {
        'fat_marks': round(fat_pess, 1),
        'fat_percentage': round((fat_pess / 40) * 100, 1),
        'total': round(internal_current + fat_pess, 1),
        'grade': worst_match['grade'],
        'reference': f"{worst_match['course_name'][:30]} ({worst_match.get('semester', 'N/A')[:17]})",
        'historical_internal': worst_match['internal_percentage']
    }
    
    return scenarios, closest_matches


def predict_three_scenarios_simple(internal_percentage: float) -> Tuple[Dict, List]:
    """Fallback simple prediction when no historical data available."""
    internal_marks = (internal_percentage / 100) * 60
    
    scenarios = {}
    
    # OPTIMISTIC
    if internal_percentage >= 80:
        opt_fat_marks = 38
    elif internal_percentage >= 70:
        opt_fat_marks = 34
    else:
        opt_fat_marks = 32
    
    scenarios['optimistic'] = {
        'fat_marks': opt_fat_marks,
        'fat_percentage': (opt_fat_marks / 40) * 100,
        'total': internal_marks + opt_fat_marks,
        'grade': get_grade_from_marks(internal_marks + opt_fat_marks),
        'reference': 'Calculated estimate (no history)',
        'historical_internal': internal_percentage
    }
    
    # REALISTIC
    real_fat_marks = (internal_percentage / 100) * 40
    scenarios['realistic'] = {
        'fat_marks': real_fat_marks,
        'fat_percentage': internal_percentage,
        'total': internal_marks + real_fat_marks,
        'grade': get_grade_from_marks(internal_marks + real_fat_marks),
        'reference': 'Proportional to internal marks',
        'historical_internal': internal_percentage
    }
    
    # PESSIMISTIC
    pess_fat_marks = max(20, real_fat_marks * 0.85)
    scenarios['pessimistic'] = {
        'fat_marks': pess_fat_marks,
        'fat_percentage': (pess_fat_marks / 40) * 100,
        'total': internal_marks + pess_fat_marks,
        'grade': get_grade_from_marks(internal_marks + pess_fat_marks),
        'reference': '15% performance drop',
        'historical_internal': internal_percentage
    }
    
    return scenarios, []


def calculate_internal_marks(marks_entry: Dict) -> Dict:
    """Calculate internal marks breakdown from components with intelligent prediction."""
    # Extract from components
    components = marks_entry.get('components', [])
    cat1 = 0
    cat2 = 0
    cat2_actual = False  # Track if CAT2 is actual data
    da = 0
    quiz1 = 0
    quiz2 = 0
    
    for comp in components:
        title = comp.get('title', '').lower()
        weightage_mark = comp.get('weightage_mark', 0)
        
        if 'continuous assessment test' in title or ('cat' in title and 'assessment' in title):
            # Check for CAT-II first (more specific pattern)
            if '- ii' in title or 'test ii' in title or title.endswith(' ii'):
                cat2 = weightage_mark
                cat2_actual = True
            elif '- i' in title or 'test i' in title or title.endswith(' i'):
                cat1 = weightage_mark
        elif 'quiz' in title:
            # Check for Quiz II first (more specific pattern)
            if '- ii' in title or 'quiz ii' in title or title.endswith(' ii'):
                quiz2 = weightage_mark
            elif '- i' in title or 'quiz i' in title or (quiz1 == 0):
                quiz1 = weightage_mark
        elif 'digital assignment' in title or 'assignment' in title:
            da = weightage_mark
    
    # Smart prediction of missing components based on CAT1 performance
    cat1_percentage = (cat1 / 15) * 100 if cat1 > 0 else 0
    
    # Predict CAT2 (typically similar to CAT1, maybe slight drop)
    if cat2 == 0 and cat1 > 0:
        cat2 = cat1 * 0.96  # Assume 4% drop
    
    # Predict DA based on CAT1 level
    if da == 0 and cat1 > 0:
        if cat1_percentage >= 85:
            da = 9.0  # 90% of 10
        elif cat1_percentage >= 75:
            da = 8.5  # 85% of 10
        elif cat1_percentage >= 65:
            da = 8.0  # 80% of 10
        else:
            da = 7.0  # 70% of 10
    
    # Predict Quiz1 if missing
    if quiz1 == 0 and cat1 > 0:
        if cat1_percentage >= 85:
            quiz1 = 9.0
        elif cat1_percentage >= 75:
            quiz1 = 8.0
        else:
            quiz1 = 7.5
    
    # Predict Quiz2 (usually improves from Quiz1)
    if quiz2 == 0:
        if quiz1 > 0:
            quiz2 = min(10, quiz1 * 1.1)  # 10% improvement
        elif cat1 > 0:
            if cat1_percentage >= 85:
                quiz2 = 9.5
            elif cat1_percentage >= 75:
                quiz2 = 8.5
            else:
                quiz2 = 8.0
    
    total_internal = cat1 + cat2 + da + quiz1 + quiz2
    internal_percentage = (total_internal / 60) * 100
    
    return {
        'CAT1': cat1,
        'CAT2': cat2,
        'CAT2_actual': cat2_actual,
        'DA': da,
        'Quiz1': quiz1,
        'Quiz2': quiz2,
        'total_internal': total_internal,
        'internal_percentage': internal_percentage
    }


def get_subject_type(course_code: str, course_name: str) -> str:
    """Determine subject type from course code."""
    code_upper = course_code.upper()
    name_lower = course_name.lower()
    
    # CSE Core subjects
    if code_upper.startswith('BCSE') and code_upper.endswith('L'):
        return 'CORE_CSE'
    elif code_upper.startswith('BCSE') and (code_upper.endswith('E') or code_upper.endswith('P')):
        return 'CORE_CSE'
    
    # Math subjects
    elif code_upper.startswith('BMAT'):
        return 'MATH'
    
    # Engineering core
    elif code_upper.startswith(('BPHY', 'BCHY', 'BEEE', 'BECE', 'BMEE')):
        return 'CORE_ENGG'
    
    # Labs
    elif code_upper.endswith('P'):
        return 'LAB'
    
    # Soft skills
    elif code_upper.startswith('BENG') or code_upper.startswith('BSTS') or 'competitive coding' in name_lower:
        return 'SOFT_SKILL'
    
    # Electives
    elif code_upper.startswith('BCLE') or 'elective' in name_lower:
        return 'ELECTIVE'
    
    return 'UNKNOWN'


def run_grade_predictor(vtop_data=None):
    """
    Main grade predictor using historical pattern analysis.
    Predicts grades based on YOUR actual previous semester performance.
    """
    if vtop_data is None:
        vtop_data = load_current_semester_data()
    
    marks_data = vtop_data.get('marks', [])
    
    if not marks_data:
        print("❌ No marks data available for prediction.")
        return []
    
    print("=" * 100)
    print("GRADE PREDICTION - HISTORICAL PATTERN ANALYSIS")
    print("Based on YOUR actual performance in previous semesters")
    print("=" * 100)
    
    results = []
    
    for marks_entry in marks_data:
        course_code = marks_entry.get('course_code', 'N/A')
        course_name = marks_entry.get('course_name', course_code)
        subject_type = get_subject_type(course_code, course_name)
        
        # Calculate internal marks
        marks = calculate_internal_marks(marks_entry)
        
        # Get three scenarios based on historical patterns
        result = predict_from_historical_patterns(
            marks['internal_percentage'], 
            subject_type, 
            course_name
        )
        if isinstance(result, tuple):
            scenarios, historical_matches = result
        else:
            scenarios = result
            historical_matches = []
        
        # Display results for this course
        print(f"\n📚 {course_name} ({course_code})")
        print(f"   Category: {subject_type}")
        print(f"\n   📊 Current Internal Performance:")
        print(f"      CAT1: {marks['CAT1']:.1f}/15 ({(marks['CAT1']/15)*100:.1f}%)", end="")
        if marks.get('CAT2_actual', False):
            # CAT2 is actual data
            print(f" | CAT2: {marks['CAT2']:.1f}/15 ({(marks['CAT2']/15)*100:.1f}%)")
        elif marks['CAT2'] != marks['CAT1']:
            # CAT2 is predicted
            print(f" | CAT2: {marks['CAT2']:.1f}/15 (predicted)")
        else:
            print()
        print(f"      DA: {marks['DA']:.1f}/10 | Quizzes: {marks['Quiz1']:.1f} + {marks['Quiz2']:.1f} = {marks['Quiz1'] + marks['Quiz2']:.1f}/20")
        print(f"      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"      Total Internal: {marks['total_internal']:.1f}/60 ({marks['internal_percentage']:.1f}%)")
        
        if historical_matches:
            print(f"\n   🔍 Similar Courses from Your History ({subject_type}):")
            for i, match in enumerate(historical_matches[:3], 1):
                print(f"      {i}. {match['course_name'][:40]:<40} | Internal: {match['internal_percentage']:.0f}% | Grade: {match['grade']} | {match.get('semester', 'N/A')[:20]}")
        
        print(f"\n   🎯 Grade Predictions (3 Scenarios):")
        print(f"   ┌{'─'*96}┐")
        print(f"   │ {'Scenario':<18} │ {'FAT Needed':<18} │ {'Total':<12} │ {'Grade':<8} │ {'Based On':<32} │")
        print(f"   ├{'─'*96}┤")
        
        opt = scenarios['optimistic']
        print(f"   │ 🌟 Optimistic     │ {opt['fat_marks']:>4.1f}/40 ({opt['fat_percentage']:>5.1f}%) │ {opt['total']:>5.1f}/100   │ {opt['grade']:<8} │ {opt['reference']:<32} │")
        
        real = scenarios['realistic']
        print(f"   │ 📈 Realistic      │ {real['fat_marks']:>4.1f}/40 ({real['fat_percentage']:>5.1f}%) │ {real['total']:>5.1f}/100   │ {real['grade']:<8} │ {real['reference']:<32} │")
        
        pess = scenarios['pessimistic']
        print(f"   │ 📉 Pessimistic    │ {pess['fat_marks']:>4.1f}/40 ({pess['fat_percentage']:>5.1f}%) │ {pess['total']:>5.1f}/100   │ {pess['grade']:<8} │ {pess['reference']:<32} │")
        print(f"   └{'─'*96}┘")
        
        # Contextual advice based on internal percentage
        internal_pct = marks['internal_percentage']
        if historical_matches:
            avg_historical = sum(m['internal_percentage'] for m in historical_matches) / len(historical_matches)
            if internal_pct > avg_historical + 5:
                advice = f"✅ Performing {internal_pct - avg_historical:.1f}% BETTER than your historical avg for {subject_type}!"
            elif internal_pct < avg_historical - 5:
                advice = f"⚠️  Performing {avg_historical - internal_pct:.1f}% BELOW your historical avg for {subject_type}"
            else:
                advice = f"📊 Consistent with your historical {subject_type} performance"
        else:
            if internal_pct >= 85:
                advice = "✅ Excellent internal performance! Maintain in FAT for S grade"
            elif internal_pct >= 75:
                advice = "📚 Good internal performance! Push for A/S grade in FAT"
            elif internal_pct >= 65:
                advice = "⚠️  Average performance. Significant FAT effort needed for better grade"
            else:
                advice = "🚨 Weak internal marks. Must excel in FAT to improve grade"
        
        print(f"   💡 {advice}")
        print(f"   {'─'*98}")
        
        results.append({
            'course_code': course_code,
            'course_name': course_name,
            'subject_type': subject_type,
            'marks': marks,
            'scenarios': scenarios,
            'historical_matches': historical_matches,
            'predicted_grade': scenarios['realistic']['grade']
        })
    
    # Summary
    print(f"\n{'='*100}")
    print("📊 SUMMARY - REALISTIC SCENARIO")
    print(f"{'='*100}")
    print(f"\nTotal Courses Analyzed: {len(results)}")
    
    # Grade distribution by category
    category_grades = {}
    for r in results:
        cat = r['subject_type']
        grade = r['predicted_grade']
        if cat not in category_grades:
            category_grades[cat] = []
        category_grades[cat].append(grade)
    
    print(f"\nPredicted Grades by Category:")
    for cat, grades in sorted(category_grades.items()):
        grade_str = ', '.join(grades)
        print(f"   {cat:15s}: {grade_str}")
    
    # Overall grade distribution
    grade_dist = {}
    for r in results:
        grade = r['predicted_grade']
        grade_dist[grade] = grade_dist.get(grade, 0) + 1
    
    print(f"\nOverall Grade Distribution (Realistic):")
    for grade in ['S', 'A', 'B', 'C', 'D', 'F']:
        if grade in grade_dist:
            print(f"   Grade {grade}: {grade_dist[grade]} course(s)")
    
    print(f"\n{'='*100}\n")
    
    return results


if __name__ == "__main__":
    run_grade_predictor()
