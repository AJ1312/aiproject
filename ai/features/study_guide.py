#!/usr/bin/env python3
"""
Feature B: Personalized Study Guide Generator (Subject-wise)
Interactive subject selection with VIT syllabus integration
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import google.generativeai as genai
from config import GOOGLE_API_KEY, GEMINI_MODEL, OUTPUT_DIR
from utils.formatters import clean_gemini_output


def load_vtop_data(file_path=None):
    """Load VTOP data from current_semester_data.json"""
    if file_path is None:
        file_path = Path(__file__).parent.parent / 'current_semester_data.json'
    
    if not Path(file_path).exists():
        print(f"❌ Error: Data file not found: {file_path}")
        sys.exit(1)
    
    with open(file_path, 'r') as f:
        return json.load(f)


def extract_subjects(vtop_data):
    """Extract all subjects with their marks from current semester data"""
    subjects = []
    marks = vtop_data.get('marks', [])
    
    for course in marks:
        course_name = course.get('course_name', 'Unknown')
        course_code = course.get('course_code', 'N/A')
        
        # Extract CAT1 marks from components
        cat1_score = 0
        cat1_max = 15
        components = course.get('components', [])
        
        for comp in components:
            title = comp.get('title', '').lower()
            if 'cat' in title or 'continuous assessment test' in title:
                cat1_score = comp.get('weightage_mark', 0)
                cat1_max = comp.get('weightage', 15)
                break
        
        subjects.append({
            'name': course_name,
            'code': course_code,
            'cat1_score': cat1_score,
            'cat1_max': cat1_max,
            'cat1_pct': (cat1_score / cat1_max * 100) if cat1_max > 0 else 0,
            'components': components
        })
    
    return subjects


def show_subject_menu(subjects):
    """Display subject selection menu"""
    print("\n" + "="*80)
    print("📚 SELECT SUBJECT FOR STUDY GUIDE")
    print("="*80)
    print()
    
    for idx, subject in enumerate(subjects, 1):
        cat1_pct = subject['cat1_pct']
        status = "🟢" if cat1_pct >= 80 else "🟡" if cat1_pct >= 60 else "🔴"
        
        print(f"  {idx}. {status} {subject['name']}")
        print(f"      Code: {subject['code']} | CAT1: {subject['cat1_score']}/{subject['cat1_max']} ({cat1_pct:.1f}%)")
    
    print()
    print("="*80)
    
    while True:
        try:
            choice = input("\nEnter subject number (or 'q' to quit): ").strip()
            
            if choice.lower() == 'q':
                print("\n👋 Goodbye!")
                sys.exit(0)
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(subjects):
                return subjects[choice_num - 1]
            else:
                print(f"❌ Please enter a number between 1 and {len(subjects)}")
        
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            sys.exit(0)


def get_vit_syllabus_context(subject_code, subject_name):
    """
    Get VIT syllabus context for the subject.
    This uses general knowledge about VIT course structure.
    """
    
    # Check if we have syllabus data stored
    syllabus_dir = Path(__file__).parent.parent / 'data' / 'syllabi'
    syllabus_file = syllabus_dir / f'{subject_code}.json'
    
    if syllabus_file.exists():
        try:
            with open(syllabus_file, 'r') as f:
                return json.load(f).get('content', '')
        except:
            pass
    
    # Generic VIT course structure
    return f"""
VIT Course Structure for {subject_name} ({subject_code}):

TYPICAL VIT COURSE BREAKDOWN:
- Total Marks: 100
  * Internal Assessment (60 marks):
    - CAT 1: 15 marks (Units 1-2, Week 5-6)
    - CAT 2: 15 marks (Units 3-4, Week 11-12)
    - Digital Assignment (DA): 10 marks
    - Quiz 1: 10 marks (Units 1-2)
    - Quiz 2: 10 marks (Units 3-4)
  * Final Assessment Test (FAT): 40 marks (All 5 units, comprehensive)

COURSE STRUCTURE (5 Units):
- Unit 1: Fundamentals & Introduction
- Unit 2: Core Concepts & Theory  
- Unit 3: Advanced Topics & Techniques
- Unit 4: Applications & Implementation
- Unit 5: Integration & Best Practices

ASSESSMENT TIMELINE:
- Weeks 1-6: Focus on Units 1-2 (CAT1 prep)
- Weeks 7-12: Focus on Units 3-4 (CAT2 prep)
- Weeks 13-18: Comprehensive review (FAT prep)

VIT GRADING (Based on absolute grading):
- S Grade: 90-100%
- A Grade: 80-89%
- B Grade: 70-79%
- C Grade: 60-69%
- D Grade: 50-59%
- F Grade: <50%
"""


def generate_study_guide(subject, vtop_data, syllabus_context):
    """Generate personalized study guide using Advanced AI"""
    
    if not GOOGLE_API_KEY:
        return "❌ Error: GOOGLE_API_KEY not configured"
    
    # Configure Advanced AI
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
    
    # Build comprehensive prompt
    student_name = vtop_data.get('reg_no', 'Student')
    cgpa = vtop_data.get('cgpa', 'N/A')
    
    # Get component details
    components_text = ""
    for comp in subject['components']:
        title = comp.get('title', 'Unknown')
        score = comp.get('weightage_mark', 0)
        max_score = comp.get('weightage', 0)
        components_text += f"  - {title}: {score}/{max_score}\n"
    
    prompt = f"""
You are a personalized academic study guide creator for VIT (Vellore Institute of Technology) students.

STUDENT PROFILE:
- Registration: {student_name}
- Current CGPA: {cgpa}/10
- Subject: {subject['name']} ({subject['code']})

CURRENT PERFORMANCE:
{components_text}
CAT1 Score: {subject['cat1_score']}/{subject['cat1_max']} ({subject['cat1_pct']:.1f}%)

VIT COURSE INFORMATION:
{syllabus_context}

TASK:
Create a comprehensive, personalized study guide for this student. The guide should:

1. **Performance Analysis**: Analyze their CAT1 performance and what it indicates
2. **Strengths & Weaknesses**: Identify areas based on their score
3. **Units to Focus On**: 
   - Which units need more attention for CAT2
   - Which topics from Units 1-2 need revision for FAT
4. **Study Plan**: Create a week-by-week study schedule leading to CAT2
5. **FAT Preparation**: Strategy for comprehensive FAT preparation
6. **Recommended Resources**: 
   - VIT library resources
   - Online materials (NPTEL, GeeksforGeeks, etc.)
   - Practice problems and previous year questions
7. **Target Grade**: Based on current performance, set realistic target and steps to achieve it
8. **Time Management**: Recommended hours per week, distribution across topics
9. **Exam Strategy**: Tips specific to VIT exam pattern
10. **Action Items**: Top 5 immediate actions to improve

Make it:
- Specific to VIT's course structure and grading
- Personalized to their current {subject['cat1_pct']:.1f}% performance
- Actionable with clear steps
- Motivating and encouraging
- Realistic and achievable

Format with clear headings, bullet points, and emojis for readability.
"""
    
    print("🤖 Generating personalized study guide with Advanced AI...")
    print("   This may take 10-15 seconds...")
    print()
    
    try:
        response = model.generate_content(prompt)
        return clean_gemini_output(response.text)
    
    except Exception as e:
        return f"❌ Error generating study guide: {str(e)}"


def main():
    """Main function"""
    
    # Load VTOP data
    data_file = Path(__file__).parent.parent / 'current_semester_data.json'
    
    if not data_file.exists():
        print("❌ Error: current_semester_data.json not found")
        print("   Please run parse_current_semester.py first")
        sys.exit(1)
    
    vtop_data = load_vtop_data(data_file)
    
    # Extract subjects
    subjects = extract_subjects(vtop_data)
    
    if not subjects:
        print("❌ No subjects found in data")
        sys.exit(1)
    
    # Check if subject provided via command line (for web interface)
    if len(sys.argv) > 2 and sys.argv[2].isdigit():
        subject_idx = int(sys.argv[2]) - 1
        if 0 <= subject_idx < len(subjects):
            selected_subject = subjects[subject_idx]
        else:
            print(f"❌ Invalid subject number. Must be 1-{len(subjects)}")
            sys.exit(1)
    elif len(sys.argv) > 2 and sys.argv[2] == '--list':
        # List subjects in JSON format for web interface
        subjects_json = []
        for idx, subject in enumerate(subjects, 1):
            subjects_json.append({
                'number': idx,
                'name': subject['name'],
                'code': subject['code'],
                'cat1_score': subject['cat1_score'],
                'cat1_max': subject['cat1_max'],
                'cat1_pct': round(subject['cat1_pct'], 1)
            })
        print(json.dumps(subjects_json, indent=2))
        return
    else:
        # Interactive mode
        print("\n" + "="*80)
        print("📚 VIT PERSONALIZED STUDY GUIDE GENERATOR")
        print("   Powered by Advanced Gemma LLM + VIT Syllabus")
        print("="*80)
        
        # Show menu and get selection
        selected_subject = show_subject_menu(subjects)
    
    print(f"\n✓ Selected: {selected_subject['name']} ({selected_subject['code']})")
    print()
    
    # Get VIT syllabus context
    syllabus_context = get_vit_syllabus_context(
        selected_subject['code'], 
        selected_subject['name']
    )
    
    # Generate study guide
    study_guide = generate_study_guide(selected_subject, vtop_data, syllabus_context)
    
    # Display
    print("="*80)
    print(f"STUDY GUIDE: {selected_subject['name']}")
    print("="*80)
    print()
    print(study_guide)
    print()
    
    # Save to file
    safe_filename = selected_subject['code'].replace('/', '_')
    output_file = OUTPUT_DIR / f'study_guide_{safe_filename}.txt'
    
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write("="*80 + "\n")
        f.write(f"PERSONALIZED STUDY GUIDE\n")
        f.write(f"Subject: {selected_subject['name']} ({selected_subject['code']})\n")
        f.write(f"Generated: {vtop_data.get('generated_at', 'N/A')}\n")
        f.write("Powered by Advanced Gemma LLM + VIT Syllabus\n")
        f.write("="*80 + "\n\n")
        f.write(study_guide)
        f.write("\n\n" + "="*80 + "\n")
        f.write("⚠️  DISCLAIMER:\n")
        f.write("* AI-generated study guide. Adapt to your learning style.\n")
        f.write("* Always refer to official VIT syllabus and faculty instructions.\n")
        f.write("* Use as a supplement to regular classes and textbooks.\n")
        f.write("="*80 + "\n")
    
    print("="*80)
    print(f"✓ Study guide saved to: {output_file}")
    print("="*80)
    print()


if __name__ == "__main__":
    main()
