"""
Smart Grade Predictor with Live Data & Gemini AI
- Fetches fresh VTOP data on every run (no caching)
- Uses Gemini to intelligently categorize subjects across semesters
- Shows live progress to user
- Predicts grades using historical patterns + AI insights
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re

try:
    import google.generativeai as genai
    from config import GOOGLE_API_KEY, GEMINI_MODEL
    GEMINI_AVAILABLE = bool(GOOGLE_API_KEY)
except:
    GEMINI_AVAILABLE = False
    print("⚠️  Gemini AI not available - using fallback categorization")


class SmartGradePredictor:
    """Smart grade predictor with live data and AI-powered categorization"""
    
    def __init__(self, show_progress=True):
        self.show_progress = show_progress
        self.cli_top_path = Path(__file__).parent.parent.parent / 'cli-top'
        self.gemini_model = None
        
        if GEMINI_AVAILABLE:
            genai.configure(api_key=GOOGLE_API_KEY)
            self.gemini_model = genai.GenerativeModel(GEMINI_MODEL)
    
    def log(self, message: str, step: Optional[int] = None):
        """Log progress to user"""
        if self.show_progress:
            if step:
                print(f"[{step}/5] {message}")
            else:
                print(f"    {message}")
    
    def fetch_live_vtop_data(self) -> Dict:
        """Fetch fresh VTOP data directly from CLI-TOP (no caching)"""
        self.log("🔄 Fetching live data from VTOP...", 1)
        
        # Export all data to temp file
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        temp_file.close()
        
        try:
            # Run CLI-TOP export
            cmd = [str(self.cli_top_path), 'ai', 'export', '-o', temp_file.name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                raise Exception(f"Failed to export VTOP data: {result.stderr}")
            
            self.log(f"✅ Exported {Path(temp_file.name).stat().st_size} bytes of data")
            
            # Parse the exported data
            return self.parse_all_data(temp_file.name)
            
        finally:
            # Cleanup
            Path(temp_file.name).unlink(missing_ok=True)
    
    def parse_all_data(self, file_path: str) -> Dict:
        """Parse all_data.txt to extract marks from ALL semesters"""
        self.log("📊 Parsing data from all semesters...", 2)
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        data = {
            'current_semester': {},
            'historical_semesters': [],
            'all_courses': []
        }
        
        # Find all semester marks sections
        semester_pattern = r'=== MARKS SEMESTER (\d+) ==='
        sections = re.split(semester_pattern, content)
        
        current_sem_num = 0
        all_semesters = []
        
        for i in range(1, len(sections), 2):
            if i+1 < len(sections):
                sem_num = int(sections[i])
                sem_content = sections[i+1]
                
                # Parse marks for this semester
                courses = self.parse_semester_marks(sem_content, sem_num)
                
                if courses:
                    semester_data = {
                        'semester_number': sem_num,
                        'courses': courses
                    }
                    all_semesters.append(semester_data)
                    
                    if sem_num > current_sem_num:
                        current_sem_num = sem_num
        
        # Identify current and historical
        if all_semesters:
            # Latest semester is current
            data['current_semester'] = all_semesters[-1]
            # All previous semesters are historical
            data['historical_semesters'] = all_semesters[:-1]
            data['all_courses'] = [c for sem in all_semesters for c in sem['courses']]
        
        self.log(f"✅ Found {len(all_semesters)} semesters with {len(data['all_courses'])} total courses")
        self.log(f"   Current: Semester {current_sem_num} ({len(data['current_semester'].get('courses', []))} courses)")
        self.log(f"   Historical: {len(data['historical_semesters'])} semesters")
        
        return data
    
    def parse_semester_marks(self, content: str, semester_num: int) -> List[Dict]:
        """Parse marks from a semester section"""
        courses = []
        lines = content.split('\n')
        
        current_course = None
        
        for line in lines:
            # Look for course names (lines with color codes)
            if '[1;34m' in line:
                # Save previous course
                if current_course and current_course.get('components'):
                    courses.append(current_course)
                
                # Start new course
                course_name = re.sub(r'\x1b\[[\d;]*m|\[[\d;]*m', '', line).strip()
                current_course = {
                    'course_name': course_name,
                    'semester': semester_num,
                    'components': [],
                    'total_scored': 0,
                    'total_max': 100
                }
                continue
            
            # Parse component rows
            if current_course and '│' in line and 'TITLE' not in line:
                parts = [p.strip() for p in line.split('│')]
                if len(parts) >= 6:
                    try:
                        # Check if numeric values exist
                        if parts[4] and parts[5]:
                            component = {
                                'title': parts[0],
                                'max_marks': float(parts[1]) if parts[1] else 0,
                                'weightage': float(parts[2]) if parts[2] else 0,
                                'scored': float(parts[4]) if parts[4] else 0,
                                'weightage_mark': float(parts[5]) if parts[5] else 0
                            }
                            current_course['components'].append(component)
                    except:
                        pass
            
            # Parse total line
            if current_course and '[32m' in line and '/[32m' in line:
                match = re.search(r'\[32m([\d.]+)\[0m/\[32m([\d.]+)\[0m', line)
                if match:
                    current_course['total_scored'] = float(match.group(1))
                    current_course['total_max'] = float(match.group(2))
                
                # Save course
                if current_course.get('components'):
                    courses.append(current_course)
                current_course = None
        
        # Don't forget last course
        if current_course and current_course.get('components'):
            courses.append(current_course)
        
        return courses
    
    def categorize_subjects_with_gemini(self, all_courses: List[Dict]) -> Dict[str, List[Dict]]:
        """Use Gemini AI to intelligently categorize subjects across semesters"""
        self.log("🤖 Using Gemini AI to categorize subjects...", 3)
        
        if not GEMINI_AVAILABLE or not self.gemini_model:
            self.log("⚠️  Gemini unavailable - using rule-based categorization")
            return self.categorize_subjects_fallback(all_courses)
        
        # Prepare course list for Gemini
        course_names = [c['course_name'] for c in all_courses]
        
        prompt = f"""
Analyze these {len(course_names)} course names from a BTech Computer Science program and categorize them into these categories:

Categories:
1. CORE_CS_THEORY - Core CS theory subjects (DS, Algorithms, AI, ML, Networks, OS, DBMS, Compiler, etc.)
2. CORE_CS_LAB - Lab components of core CS subjects
3. MATHEMATICS - Math subjects (Calculus, Linear Algebra, Probability, Discrete Math, etc.)
4. PROGRAMMING - Programming and coding focused (Java, Python, Competitive Coding, etc.)
5. HARDWARE_ENGG - Hardware/Engineering (VLSI, Embedded, Computer Architecture, etc.)
6. SOFT_SKILLS - Soft skills and communication (English, Ethics, Professional Writing, etc.)
7. SCIENCE - Basic sciences (Physics, Chemistry, Biology, Environmental Science, etc.)
8. ELECTIVE - Domain electives (Cloud, Security, Blockchain, IoT, etc.)
9. PROJECT - Projects and thesis
10. OTHERS - Anything else

Courses:
{json.dumps(course_names, indent=2)}

Return ONLY a JSON object mapping each course name to its category. Format:
{{
  "Course Name 1": "CATEGORY",
  "Course Name 2": "CATEGORY",
  ...
}}
"""
        
        try:
            self.log("   Calling Gemini API...")
            response = self.gemini_model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                categorization = json.loads(json_match.group(0))
                self.log(f"✅ Categorized {len(categorization)} courses using Gemini AI")
                
                # Group courses by category
                categories = {}
                for course in all_courses:
                    category = categorization.get(course['course_name'], 'OTHERS')
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(course)
                
                # Show category distribution
                for cat, courses in sorted(categories.items()):
                    self.log(f"   - {cat}: {len(courses)} courses")
                
                return categories
            
        except Exception as e:
            self.log(f"⚠️  Gemini error: {str(e)[:100]} - using fallback")
        
        return self.categorize_subjects_fallback(all_courses)
    
    def categorize_subjects_fallback(self, all_courses: List[Dict]) -> Dict[str, List[Dict]]:
        """Rule-based categorization when Gemini is unavailable"""
        categories = {}
        
        for course in all_courses:
            name = course['course_name'].lower()
            
            # Categorize by keywords
            if any(kw in name for kw in ['lab', 'practical', 'project work']):
                category = 'CORE_CS_LAB' if 'comput' in name or 'program' in name else 'OTHERS'
            elif any(kw in name for kw in ['calculus', 'algebra', 'probability', 'statistics', 'discrete', 'math']):
                category = 'MATHEMATICS'
            elif any(kw in name for kw in ['algorithm', 'data structure', 'artificial intelligence', 'machine learning',
                                            'network', 'database', 'operating system', 'compiler', 'software']):
                category = 'CORE_CS_THEORY'
            elif any(kw in name for kw in ['java', 'python', 'coding', 'programming']):
                category = 'PROGRAMMING'
            elif any(kw in name for kw in ['cloud', 'security', 'blockchain', 'iot', 'cyber', 'malware']):
                category = 'ELECTIVE'
            elif any(kw in name for kw in ['english', 'communication', 'ethics', 'professional']):
                category = 'SOFT_SKILLS'
            elif any(kw in name for kw in ['physics', 'chemistry', 'biology', 'environmental']):
                category = 'SCIENCE'
            elif 'project' in name or 'thesis' in name:
                category = 'PROJECT'
            else:
                category = 'OTHERS'
            
            if category not in categories:
                categories[category] = []
            categories[category].append(course)
        
        return categories
    
    def predict_grades(self, current_courses: List[Dict], categorized_history: Dict[str, List[Dict]]) -> List[Dict]:
        """Predict grades for current semester using historical patterns"""
        self.log("🎯 Predicting grades using historical patterns...", 4)
        
        predictions = []
        
        for course in current_courses:
            course_name = course['course_name']
            
            # Find category
            category = None
            for cat, courses in categorized_history.items():
                if course in courses:
                    category = cat
                    break
            
            if not category:
                category = 'OTHERS'
            
            # Calculate internal marks
            internal = self.calculate_internal_marks(course)
            
            # Find similar historical courses
            historical = [c for c in categorized_history.get(category, []) 
                         if c.get('semester', 0) < course.get('semester', 999)]
            
            # Predict three scenarios
            scenarios = self.calculate_scenarios(internal, historical, category)
            
            prediction = {
                'course_name': course_name,
                'category': category,
                'internal': internal,
                'scenarios': scenarios,
                'historical_matches': len(historical)
            }
            
            predictions.append(prediction)
            
            # Show progress
            self.log(f"   ✓ {course_name[:50]:<50} | {internal['percentage']:.1f}% → {scenarios['realistic']['grade']}")
        
        self.log(f"✅ Predicted grades for {len(predictions)} courses")
        
        return predictions
    
    def calculate_internal_marks(self, course: Dict) -> Dict:
        """Calculate internal marks from components"""
        components = course.get('components', [])
        
        total = sum(c.get('weightage_mark', 0) for c in components)
        max_internal = 60  # Standard internal max
        percentage = (total / max_internal) * 100 if max_internal > 0 else 0
        
        return {
            'total': total,
            'max': max_internal,
            'percentage': percentage,
            'components': components
        }
    
    def calculate_scenarios(self, internal: Dict, historical: List[Dict], category: str) -> Dict:
        """Calculate optimistic, realistic, and pessimistic grade scenarios"""
        internal_pct = internal['percentage']
        internal_marks = internal['total']
        
        scenarios = {}
        
        if historical:
            # Use historical patterns
            avg_total = sum(c.get('total_scored', 0) for c in historical) / len(historical)
            avg_internal_pct = (avg_total / 100) * 60  # Rough estimate
            
            # Optimistic: Best historical performance
            best = max(c.get('total_scored', 0) for c in historical)
            opt_fat = max(20, best - internal_marks)
            opt_fat = min(40, opt_fat)  # Clamp
            
            # Realistic: Based on historical average
            real_fat = avg_total - internal_marks if avg_total > internal_marks else internal_pct * 0.4
            real_fat = max(20, min(40, real_fat))
            
            # Pessimistic: Conservative estimate
            pess_fat = real_fat * 0.85
            pess_fat = max(20, min(40, pess_fat))
            
        else:
            # No history - use proportional estimates
            opt_fat = min(40, (internal_pct / 100) * 40 * 1.1)  # 10% better
            real_fat = (internal_pct / 100) * 40  # Proportional
            pess_fat = real_fat * 0.85  # 15% worse
        
        # Calculate scenarios
        for scenario_name, fat_marks in [('optimistic', opt_fat), ('realistic', real_fat), ('pessimistic', pess_fat)]:
            total = internal_marks + fat_marks
            grade = self.marks_to_grade(total)
            
            scenarios[scenario_name] = {
                'fat_marks': round(fat_marks, 1),
                'fat_percentage': round((fat_marks / 40) * 100, 1),
                'total': round(total, 1),
                'grade': grade
            }
        
        return scenarios
    
    def marks_to_grade(self, marks: float) -> str:
        """Convert marks to grade"""
        if marks >= 90: return 'S'
        elif marks >= 80: return 'A'
        elif marks >= 70: return 'B'
        elif marks >= 60: return 'C'
        elif marks >= 50: return 'D'
        else: return 'F'
    
    def display_predictions(self, predictions: List[Dict]):
        """Display predictions in beautiful format"""
        self.log("", None)
        print("=" * 120)
        print("📊 SMART GRADE PREDICTIONS - LIVE DATA + AI CATEGORIZATION")
        print("=" * 120)
        print()
        
        for pred in predictions:
            name = pred['course_name']
            cat = pred['category']
            internal = pred['internal']
            scenarios = pred['scenarios']
            
            print(f"📚 {name}")
            print(f"   Category: {cat} | Internal: {internal['total']:.1f}/60 ({internal['percentage']:.1f}%)")
            print()
            print(f"   {'Scenario':<15} {'FAT Needed':<20} {'Total':<15} {'Grade':<10}")
            print(f"   {'─'*15} {'─'*20} {'─'*15} {'─'*10}")
            
            for scenario_name in ['optimistic', 'realistic', 'pessimistic']:
                s = scenarios[scenario_name]
                icon = '🌟' if scenario_name == 'optimistic' else '📈' if scenario_name == 'realistic' else '📉'
                print(f"   {icon} {scenario_name.capitalize():<12} {s['fat_marks']}/40 ({s['fat_percentage']:.1f}%){'':8} {s['total']}/100{'':7} {s['grade']}")
            
            print()
            print("─" * 120)
            print()
        
        # Summary
        realistic_grades = [p['scenarios']['realistic']['grade'] for p in predictions]
        grade_counts = {}
        for g in realistic_grades:
            grade_counts[g] = grade_counts.get(g, 0) + 1
        
        print(f"📊 SUMMARY (Realistic Scenario):")
        for grade in ['S', 'A', 'B', 'C', 'D', 'F']:
            if grade in grade_counts:
                print(f"   Grade {grade}: {grade_counts[grade]} course(s)")
        print()
        print("=" * 120)
    
    def run(self):
        """Main execution flow"""
        print()
        print("🚀 SMART GRADE PREDICTOR - LIVE DATA + AI")
        print("=" * 120)
        print()
        
        try:
            # Step 1: Fetch live data
            vtop_data = self.fetch_live_vtop_data()
            
            # Step 2: Already done in parsing
            
            # Step 3: Categorize with Gemini
            all_courses = vtop_data['all_courses']
            categorized = self.categorize_subjects_with_gemini(all_courses)
            
            # Step 4: Predict grades
            current_courses = vtop_data['current_semester'].get('courses', [])
            predictions = self.predict_grades(current_courses, categorized)
            
            # Step 5: Display results
            self.log("📊 Preparing final report...", 5)
            print()
            self.display_predictions(predictions)
            
            return predictions
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


def main():
    predictor = SmartGradePredictor(show_progress=True)
    predictor.run()


if __name__ == '__main__':
    main()
