#!/usr/bin/env python3
"""
Smart Marks & Grade Predictor with Gemini Subject Categorization
Uses Gemini AI to categorize subjects, then predicts grades based on similar subjects from previous semesters
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import google.generativeai as genai
    from config import GOOGLE_API_KEY, GEMINI_MODEL
except ImportError:
    print("❌ Error: google-generativeai not installed")
    print("   Run: pip install -r requirements.txt")
    sys.exit(1)

from utils.formatters import print_section, print_box


class SmartMarksPredictor:
    """Gemini-powered marks and grade predictor"""
    
    GRADE_POINTS = {'S': 10, 'A': 9, 'B': 8, 'C': 7, 'D': 6, 'E': 5, 'F': 0}
    
    def __init__(self, vtop_data: Dict):
        self.data = vtop_data
        self.current_marks = vtop_data.get('marks', [])
        self.cgpa_trend = vtop_data.get('cgpa_trend', [])
        
        # Initialize Gemini
        if not GOOGLE_API_KEY:
            raise Exception("GOOGLE_API_KEY not configured")
        
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL)
    
    def categorize_subjects_with_gemini(self, current_courses: List[str], 
                                       previous_courses: List[Dict]) -> Dict:
        """
        Use Gemini to categorize current semester subjects and find similar ones from previous semesters
        
        Args:
            current_courses: List of current course names
            previous_courses: List of dicts with course names and grades from previous semesters
            
        Returns:
            Dictionary mapping current courses to similar previous courses
        """
        print("🤖 Using Gemini AI to categorize subjects...")
        
        # Build prompt
        prev_course_list = "\n".join([
            f"- {c['name']} (Grade: {c.get('grade', 'N/A')})" 
            for c in previous_courses
        ])
        
        curr_course_list = "\n".join([f"- {c}" for c in current_courses])
        
        prompt = f"""
You are an academic advisor analyzing course relationships.

CURRENT SEMESTER COURSES:
{curr_course_list}

PREVIOUS SEMESTER COURSES:
{prev_course_list}

For each current semester course, identify the most similar course(s) from previous semesters.
Consider:
1. Subject area (CS, Math, Physics, etc.)
2. Difficulty level
3. Prerequisites/continuity (e.g., Data Structures → Advanced Data Structures)
4. Topic overlap

Respond ONLY in JSON format like this:
{{
  "categorization": {{
    "Current Course Name": {{
      "category": "CS Core/Math/Physics/Elective/etc",
      "similar_previous_courses": ["Previous Course 1", "Previous Course 2"],
      "reason": "Brief explanation"
    }}
  }}
}}

Be specific and practical. If no similar course exists, say "None - New topic area".
"""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            categorization = json.loads(response_text)
            print("✅ Subject categorization complete!")
            
            return categorization.get('categorization', {})
            
        except Exception as e:
            print(f"⚠️  Gemini categorization failed: {e}")
            # Fallback to simple matching
            return self._fallback_categorization(current_courses, previous_courses)
    
    def _fallback_categorization(self, current: List[str], previous: List[Dict]) -> Dict:
        """Simple keyword-based fallback categorization"""
        categorization = {}
        
        for curr_course in current:
            curr_lower = curr_course.lower()
            similar = []
            
            for prev in previous:
                prev_name = prev['name'].lower()
                # Simple keyword matching
                curr_words = set(curr_lower.split())
                prev_words = set(prev_name.split())
                overlap = curr_words & prev_words
                
                if len(overlap) >= 2:  # At least 2 words in common
                    similar.append(prev['name'])
            
            categorization[curr_course] = {
                'category': 'General',
                'similar_previous_courses': similar if similar else ['None - New topic area'],
                'reason': 'Keyword matching'
            }
        
        return categorization
    
    def predict_marks_and_grades(self) -> Dict:
        """
        Predict final marks and grades for current semester
        
        Returns:
            Dictionary with predictions for each course
        """
        print("\n📊 Analyzing performance patterns...")
        
        # Step 1: Extract previous semester data
        previous_courses = []
        for sem in self.cgpa_trend:
            # Extract grade counts
            for grade in ['S', 'A', 'B', 'C', 'D', 'E', 'F']:
                count = sem.get(f'{grade.lower()}_grades', 0)
                for _ in range(count):
                    previous_courses.append({
                        'semester': sem.get('semester', 'Unknown'),
                        'name': f"{grade}-level course",
                        'grade': grade
                    })
        
        # Step 2: Get current course names
        current_course_names = [c.get('course_title', 'Unknown') for c in self.current_marks]
        
        # Step 3: Categorize with Gemini
        if current_course_names and previous_courses:
            categorization = self.categorize_subjects_with_gemini(
                current_course_names, 
                previous_courses
            )
        else:
            categorization = {}
        
        # Step 4: Predict for each current course
        predictions = []
        
        for course in self.current_marks:
            course_title = course.get('course_title', 'Unknown')
            course_code = course.get('course_code', 'N/A')
            total_scored = course.get('total_scored', 0)
            total_weight = course.get('total_weight', 40)
            components = course.get('components', [])
            
            # Current internal percentage
            internal_pct = (total_scored / total_weight * 100) if total_weight > 0 else 0
            
            # Get categorization info
            cat_info = categorization.get(course_title, {})
            category = cat_info.get('category', 'General')
            similar_courses = cat_info.get('similar_previous_courses', [])
            
            # Calculate average grade from similar courses
            similar_grades = []
            for sim in similar_courses:
                if sim != 'None - New topic area':
                    for prev in previous_courses:
                        if prev['name'] == sim:
                            similar_grades.append(prev['grade'])
            
            # Predict based on similar courses or current performance
            if similar_grades:
                avg_grade_points = sum(self.GRADE_POINTS.get(g, 0) for g in similar_grades) / len(similar_grades)
                predicted_marks = avg_grade_points * 10  # Convert to marks (0-100)
                prediction_basis = f"Based on {len(similar_grades)} similar courses"
            else:
                # Use current internal performance with slight optimization
                predicted_marks = internal_pct * 0.4 + (internal_pct * 1.1) * 0.6  # Assume slight improvement in FAT
                prediction_basis = "Based on current internal performance"
            
            # Ensure within bounds
            predicted_marks = max(0, min(100, predicted_marks))
            
            # Map to grade
            if predicted_marks >= 90:
                predicted_grade = 'S'
            elif predicted_marks >= 80:
                predicted_grade = 'A'
            elif predicted_marks >= 70:
                predicted_grade = 'B'
            elif predicted_marks >= 60:
                predicted_grade = 'C'
            elif predicted_marks >= 50:
                predicted_grade = 'D'
            elif predicted_marks >= 40:
                predicted_grade = 'E'
            else:
                predicted_grade = 'F'
            
            # Component-wise breakdown
            completed_components = [c for c in components if c.get('status') == 'Completed']
            avg_component_pct = sum(
                (c.get('scored_marks', 0) / c.get('max_marks', 1) * 100) 
                for c in completed_components
            ) / len(completed_components) if completed_components else internal_pct
            
            predictions.append({
                'course_code': course_code,
                'course_title': course_title,
                'category': category,
                'similar_courses': similar_courses,
                'current_internal': round(total_scored, 2),
                'internal_percentage': round(internal_pct, 2),
                'avg_component_performance': round(avg_component_pct, 2),
                'predicted_final_marks': round(predicted_marks, 2),
                'predicted_grade': predicted_grade,
                'prediction_basis': prediction_basis,
                'confidence': 'High' if similar_grades else 'Medium'
            })
        
        return {
            'predictions': predictions,
            'total_courses': len(predictions),
            'categorization_method': 'Gemini AI' if categorization else 'Fallback'
        }


def main():
    """Run smart marks predictor"""
    from vtop_data_manager import get_vtop_data
    
    print("=" * 80)
    print("🎯 SMART MARKS & GRADE PREDICTOR")
    print("Powered by Gemini AI for Subject Categorization")
    print("=" * 80)
    print()
    
    # Get data
    data = get_vtop_data(use_cache=True)
    
    try:
        predictor = SmartMarksPredictor(data)
        
        # Run predictions
        print("🔄 Step 1: Collecting course data...")
        print(f"   Current courses: {len(predictor.current_marks)}")
        print(f"   Previous semesters: {len(predictor.cgpa_trend)}")
        print()
        
        print("🔄 Step 2: Categorizing subjects with Gemini AI...")
        result = predictor.predict_marks_and_grades()
        print()
        
        print("=" * 80)
        print_section(f"PREDICTIONS ({result['total_courses']} courses)")
        print(f"Method: {result['categorization_method']}")
        print("=" * 80)
        print()
        
        for pred in result['predictions']:
            print(f"\n📚 {pred['course_title']} ({pred['course_code']})")
            print(f"   Category: {pred['category']}")
            print(f"   Similar to: {', '.join(pred['similar_courses'][:2])}")
            print(f"   ")
            print(f"   Current Internal: {pred['current_internal']}/{40} ({pred['internal_percentage']}%)")
            print(f"   Avg Component Performance: {pred['avg_component_performance']}%")
            print(f"   ")
            print(f"   🎯 PREDICTED FINAL: {pred['predicted_final_marks']}/100")
            print(f"   🏆 PREDICTED GRADE: {pred['predicted_grade']}")
            print(f"   ")
            print(f"   Basis: {pred['prediction_basis']}")
            print(f"   Confidence: {pred['confidence']}")
        
        print("\n" + "=" * 80)
        print("💡 These predictions use Gemini AI to find similar courses")
        print("   from your previous semesters and predict based on patterns!")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
