#!/usr/bin/env python3
"""
Manual Cache Builder - Build comprehensive cache from individual CLI-TOP command outputs
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime

CLI_TOP = Path(__file__).parent.parent / 'cli-top'
CACHE_FILE = Path(__file__).parent / 'vtop_cache.json'

def run_command(cmd, input_text=None):
    """Run CLI command and return output"""
    try:
        kwargs = {
            'capture_output': True,
            'text': True,
            'timeout': 60
        }
        
        if input_text:
            kwargs['input'] = input_text
        else:
            kwargs['stdin'] = subprocess.DEVNULL
            
        result = subprocess.run(
            [str(CLI_TOP)] + cmd,
            **kwargs
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception as e:
        print(f"⚠️  Error: {e}")
        return None

def get_ai_export():
    """Get AI export JSON data"""
    print("📊 Fetching AI export...")
    result = subprocess.run(
        [str(CLI_TOP), 'ai', 'export', '-o', '-'],
        input="5\n5\n5\n",
        capture_output=True,
        text=True,
        timeout=120
    )
    
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            print("⚠️  Failed to parse AI export JSON")
            return None
    return None

def main():
    """Build comprehensive cache"""
    print("="*60)
    print("🚀 Building Complete VTOP Cache - Manual Mode")
    print("="*60)
    print()
    
    cache = {
        'generated_at': datetime.now().isoformat(),
        'reg_no': 'EXAMPLE001',
        'ai_export': None,
        'profile': None,
        'hostel': None,
        'cgpa': None,
        'library': None,
        'leave_status': None,
        'nightslip': None,
        'marks_by_semester': {},
        'attendance_by_semester': {},
        'grades_by_semester': {},
        'timetable_by_semester': {},
        'exams_by_semester': {},
    }
    
    # Get AI export (current semester JSON data)
    ai_export = get_ai_export()
    if ai_export:
        cache['ai_export'] = ai_export
        print(f"✅ AI Export: {len(ai_export.get('marks', []))} courses")
    
    # Get non-interactive commands
    print("\n📋 Fetching basic info...")
    cache['profile'] = run_command(['profile'])
    cache['hostel'] = run_command(['hostel'])
    cache['cgpa'] = run_command(['cgpa', 'view'])
    cache['library'] = run_command(['library-dues'])
    cache['leave_status'] = run_command(['leave'])
    cache['nightslip'] = run_command(['nightslip'])
    print("✅ Basic info loaded")
    
    # Get semester-wise data
    print("\n📚 Fetching semester-wise data...")
    for sem in range(1, 6):
        sem_input = f"{sem}\n"
        
        # Marks
        marks = run_command(['marks'], sem_input)
        if marks and len(marks) > 100:
            cache['marks_by_semester'][f'semester_{sem}'] = marks
            print(f"  ✓ Marks semester {sem}")
        
        # Attendance
        attendance = run_command(['attendance'], sem_input)
        if attendance and len(attendance) > 100:
            cache['attendance_by_semester'][f'semester_{sem}'] = attendance
            print(f"  ✓ Attendance semester {sem}")
        
        # Grades
        grades = run_command(['grades'], sem_input)
        if grades and len(grades) > 100:
            cache['grades_by_semester'][f'semester_{sem}'] = grades
            print(f"  ✓ Grades semester {sem}")
        
        # Timetable
        timetable = run_command(['timetable'], sem_input)
        if timetable and len(timetable) > 100:
            cache['timetable_by_semester'][f'semester_{sem}'] = timetable
            print(f"  ✓ Timetable semester {sem}")
        
        # Exams
        exams = run_command(['exams'], sem_input)
        if exams and len(exams) > 100:
            cache['exams_by_semester'][f'semester_{sem}'] = exams
            print(f"  ✓ Exams semester {sem}")
    
    print(f"\n✅ Collected data for {len(cache['marks_by_semester'])} semesters")
    
    # Save cache
    print("\n" + "="*60)
    print(f"💾 Saving cache to {CACHE_FILE}")
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)
    
    file_size = CACHE_FILE.stat().st_size / 1024
    print(f"✅ Cache saved successfully!")
    print(f"📊 File size: {file_size:.1f} KB")
    print(f"📦 Contains:")
    print(f"   - AI Export: {'✓' if cache['ai_export'] else '✗'}")
    print(f"   - Marks: {len(cache['marks_by_semester'])} semesters")
    print(f"   - Attendance: {len(cache['attendance_by_semester'])} semesters")
    print(f"   - Grades: {len(cache['grades_by_semester'])} semesters")
    print(f"   - Timetable: {len(cache['timetable_by_semester'])} semesters")
    print(f"   - Exams: {len(cache['exams_by_semester'])} semesters")
    print("="*60)

if __name__ == '__main__':
    main()
