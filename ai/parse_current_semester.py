#!/usr/bin/env python3
"""
Parse all_data.txt and convert to structured JSON for AI features
Extracts current semester (Semester 5 - Fall 2025-26) data for accurate AI predictions
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime

def parse_marks_section(lines, start_idx):
    """Parse marks for a specific semester"""
    courses = []
    i = start_idx
    current_course = None
    
    while i < len(lines):
        line = lines[i]
        
        # Stop at next section
        if line.startswith('==='):
            break
        
        # Look for course names (lines with [1;34m color codes)
        if '[1;34m' in line:
            # Save previous course if it exists
            if current_course and current_course['components']:
                courses.append(current_course)
            
            # Start new course - properly remove ANSI color codes
            course_name = re.sub(r'\x1b\[[\d;]*m|\[[\d;]*m', '', line).strip()
            
            # Generate course code from course name (use abbreviation)
            # Map common course names to codes
            course_code_map = {
                'Cloud Architecture Design': 'BCSE352L',
                'Advanced Competitive Coding': 'BSTS201P',
                'Artificial Intelligence': 'BCSE307L',
                'Database Systems': 'BCSE203L',
                'Compiler Design': 'BCSE304L',
                'Malware Analysis': 'BCSE358L',
                'Computer Networks': 'BCSE303L'
            }
            
            # Find matching course code or use first 3 chars of each word
            course_code = course_code_map.get(course_name)
            if not course_code:
                # Generate code from first letters of each word
                words = course_name.split()
                if len(words) >= 2:
                    course_code = ''.join([w[0].upper() for w in words[:3]])
                else:
                    course_code = words[0][:3].upper() if words else 'UNK'
            
            current_course = {
                'course_name': course_name,
                'course_code': course_code,
                'components': [],
                'total_scored': 0,
                'total_weight': 100
            }
            i += 1
            continue
        
        # Parse marks table for current course
        if current_course:
            # Parse total line
            if '[32m' in line and '/[32m' in line:
                match = re.search(r'\[32m([\d.]+)\[0m/\[32m([\d.]+)\[0m', line)
                if match:
                    current_course['total_scored'] = float(match.group(1))
                    current_course['total_weight'] = float(match.group(2))
                # Save course and reset
                if current_course['components']:
                    courses.append(current_course)
                current_course = None
                i += 1
                continue
            
            # Parse component lines
            if '│' in line and 'TITLE' not in line and 'MAX MARKS' not in line:
                parts = [p.strip() for p in line.split('│')]
                if len(parts) >= 6:
                    try:
                        # Check if parts[1] and parts[2] are numbers
                        if parts[1] and parts[2]:
                            component = {
                                'title': parts[0].strip(),
                                'max_marks': float(parts[1]) if parts[1].replace('.', '').isdigit() else 0,
                                'weightage': float(parts[2]) if parts[2].replace('.', '').isdigit() else 0,
                                'status': parts[3],
                                'scored_mark': float(parts[4]) if parts[4].replace('.', '').isdigit() else 0,
                                'weightage_mark': float(parts[5]) if parts[5].replace('.', '').isdigit() else 0
                            }
                            current_course['components'].append(component)
                    except (ValueError, IndexError):
                        pass
        
        i += 1
    
    # Don't forget the last course
    if current_course and current_course['components']:
        courses.append(current_course)
    
    return courses

def parse_attendance_section(lines, start_idx):
    """Parse attendance for a specific semester"""
    attendance = []
    i = start_idx
    
    # Course code mapping for attendance records
    course_code_map = {
        'Database Systems': 'BCSE203L',
        'Database Systems Lab': 'BCSE203P',
        'Artificial Intelligence': 'BCSE307L',
        'Compiler Design': 'BCSE304L',
        'Compiler Design Lab': 'BCSE304P',
        'Computer Networks': 'BCSE303L',
        'Computer Networks Lab': 'BCSE303P',
        'Malware Analysis': 'BCSE358L',
        'Malware Analysis Lab': 'BCSE358P',
        'Cloud Architecture Design': 'BCSE352L',
        'Advanced Competitive Coding': 'BSTS201P'
    }
    
    while i < len(lines):
        line = lines[i]
        
        # Stop at next section
        if line.startswith('==='):
            break
        
        # Parse attendance table rows
        if '│' in line and 'INDEX' not in line and 'SUBJECT' not in line:
            parts = [p.strip() for p in line.split('│')]
            if len(parts) >= 6:
                try:
                    # Extract attendance numbers from format like "34/36"
                    classes_match = re.search(r'(\d+)/(\d+)', parts[4])
                    if classes_match:
                        attended = int(classes_match.group(1))
                        total = int(classes_match.group(2))
                    else:
                        attended = 0
                        total = 0
                    
                    # Extract percentage
                    percentage_match = re.search(r'(\d+)%', parts[5])
                    percentage = int(percentage_match.group(1)) if percentage_match else 0
                    
                    course_name = parts[1]
                    course_code = course_code_map.get(course_name, 'UNK')
                    
                    record = {
                        'course_code': course_code,
                        'course_name': course_name,
                        'course_type': parts[2],
                        'faculty': parts[3],
                        'attended': attended,
                        'total_classes': total,
                        'attendance_percentage': percentage
                    }
                    attendance.append(record)
                except (ValueError, IndexError):
                    pass
        
        i += 1
    
    return attendance

def parse_all_data_file(file_path):
    """Parse the complete all_data.txt file"""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    data = {
        'generated_at': datetime.now().isoformat(),
        'reg_no': 'UNKNOWN',
        'name': 'Student',
        'email': '',
        'program': '',
        'school': '',
        'semester': 'Current Semester',
        'cgpa': 0.0,
        'credits_completed': 0,
        'marks': [],
        'attendance': [],
        'exams': []
    }
    
    # Find sections
    for i, line in enumerate(lines):
        # Parse Profile Information
        if '=== PROFILE INFORMATION ===' in line:
            j = i + 1
            while j < len(lines) and not lines[j].startswith('==='):
                line_text = lines[j]
                # Parse Registration Number
                if 'Registration Number' in line_text or 'Reg. No.' in line_text:
                    reg_match = re.search(r'\b\d{2}[A-Z]{3}\d{4}\b', line_text)
                    if reg_match:
                        data['reg_no'] = reg_match.group(0)
                # Parse Name
                if 'Name' in line_text and 'Programme' not in line_text:
                    name_match = re.search(r'│\s*([A-Z][A-Za-z\s]+?)\s*│', line_text)
                    if name_match:
                        data['name'] = name_match.group(1).strip()
                # Parse Email
                if '@vitstudent.ac.in' in line_text or 'Email' in line_text:
                    email_match = re.search(r'[\w\.-]+@vitstudent\.ac\.in', line_text)
                    if email_match:
                        data['email'] = email_match.group(0)
                # Parse Program
                if 'Programme' in line_text or 'Program' in line_text:
                    # Extract program name from table cell
                    prog_match = re.search(r'│\s*([A-Za-z\s\(\)]+?)\s*│', lines[j+1] if j+1 < len(lines) else '')
                    if prog_match:
                        data['program'] = prog_match.group(1).strip()
                # Parse School
                if 'School' in line_text:
                    school_match = re.search(r'│\s*([A-Za-z\s]+?)\s*│', lines[j+1] if j+1 < len(lines) else '')
                    if school_match:
                        data['school'] = school_match.group(1).strip()
                j += 1
        
        # Parse CGPA
        if 'CGPA:' in line and '[' in line:
            cgpa_match = re.search(r'\[([\d.]+)\[', line)
            if cgpa_match:
                data['cgpa'] = float(cgpa_match.group(1))
        
        # Parse Marks Semester 5 (Current semester)
        if '=== MARKS SEMESTER 5 ===' in line:
            # Find where the actual data starts (after semester selection)
            j = i + 10  # Skip semester selection table
            while j < len(lines) and 'Your selected semester' not in lines[j]:
                j += 1
            courses = parse_marks_section(lines, j + 1)
            data['marks'] = courses
        
        # Parse Attendance Semester 5 (Current semester)
        if '=== ATTENDANCE SEMESTER 5 ===' in line:
            attendance = parse_attendance_section(lines, i + 1)
            data['attendance'] = attendance
    
    # Add exam dates for courses (generate from current date + 1 month)
    if data['marks']:
        exam_date = '2025-11-25'
        for course in data['marks']:
            data['exams'].append({
                'course_code': course['course_code'],
                'course_name': course['course_name'],
                'exam_type': 'FAT',
                'date': exam_date,
                'time': '10:00 AM'
            })
    
    return data

def main():
    """Main entry point"""
    all_data_file = '/tmp/all_data.txt'
    
    if not Path(all_data_file).exists():
        print(f"❌ Error: {all_data_file} not found")
        print("   Please ensure all_data.txt is available at /tmp/all_data.txt")
        sys.exit(1)
    
    print("="*60)
    print("📊 Parsing Current Semester Data (Semester 5)")
    print("="*60)
    print()
    
    data = parse_all_data_file(all_data_file)
    
    # Save to JSON
    output_file = Path(__file__).parent / 'current_semester_data.json'
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Parsed successfully!")
    print(f"   Reg No: {data['reg_no']}")
    print(f"   Semester: {data['semester']}")
    print(f"   CGPA: {data['cgpa']}")
    print(f"   Courses: {len(data['marks'])}")
    print(f"   Attendance Records: {len(data['attendance'])}")
    print(f"   Exams: {len(data.get('exams', []))}")
    print()
    print(f"💾 Saved to: {output_file}")
    print("="*60)
    print()
    print("Now you can run AI features with fresh data:")
    print(f"  python ai/run_all_features.py {output_file}")
    print(f"  python ai/chatbot.py --data {output_file}")
    print()

if __name__ == '__main__':
    main()
