#!/usr/bin/env python3
"""
CLI-TOP Chatbot
Interactive chatbot powered by Advanced AI with full VTOP context
"""

import json
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import google.generativeai as genai
    from config import GOOGLE_API_KEY, GEMINI_MODEL
except ImportError:
    print("❌ Error: Required packages not installed")
    print("   Run: pip install -r ai/requirements.txt")
    sys.exit(1)

from utils.formatters import clean_gemini_output

class VTOPChatbot:
    """AI Chatbot with VTOP context"""
    
    def __init__(self, vtop_data):
        """Initialize chatbot with VTOP data"""
        self.vtop_data = vtop_data
        self.conversation_history = []
        
        # Configure Advanced AI
        if not GOOGLE_API_KEY:
            print("❌ Error: GOOGLE_API_KEY not configured")
            print("   Please set it in ai/.env file")
            sys.exit(1)
        
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Build context
        self.context = self._build_context()
    
    def _build_context(self):
        """Build comprehensive context from VTOP data with personal insights"""
        # Extract basic info
        reg_no = self.vtop_data.get('reg_no', 'N/A')
        cgpa = self.vtop_data.get('cgpa', 8.41)
        semester = self.vtop_data.get('semester', 'Fall Semester 2025-26')
        
        # Get current semester data
        marks = self.vtop_data.get('marks', [])
        attendance = self.vtop_data.get('attendance', [])
        exams = self.vtop_data.get('exams', [])
        
        # Calculate statistics
        avg_attendance = sum(a.get('attendance_percentage', 0) for a in attendance) / len(attendance) if attendance else 0
        low_attendance = [a for a in attendance if a.get('attendance_percentage', 100) < 80]
        
        # Get raw data sections for extra context
        profile_text = self.vtop_data.get('raw_profile', '')
        hostel_text = self.vtop_data.get('raw_hostel', '')
        cgpa_text = self.vtop_data.get('raw_cgpa', '')
        library_text = self.vtop_data.get('raw_library', '')
        leave_text = self.vtop_data.get('raw_leave', '')
        
        context = f"""
You are {self.vtop_data.get('name', 'the student')}'s personal AI academic assistant with complete access to their VTOP data.

STUDENT PROFILE:
- Name: {self.vtop_data.get('name', 'Student')}
- Registration Number: {reg_no}
- Program: {self.vtop_data.get('program', 'BTech Computer Science and Engineering')}
- Email: {self.vtop_data.get('email', 'Not available')}
- School: {self.vtop_data.get('school', 'Not available')}
- Current Semester: {semester}
- Overall CGPA: {cgpa}/10
- Credits Completed: {self.vtop_data.get('credits_completed', 'N/A')}/160

"""
        if hostel_text:
            context += f"\nHOSTEL INFORMATION:\n{hostel_text}\n"
        else:
            context += "\nHOSTEL INFORMATION:\n"
            context += "- Block: SOCRATES BLOCK (G - Block)\n"
            context += "- Room: 208F\n"
            context += "- Bed Type: 4-BED AC\n"
            context += "- Mess: VEG - RSM-V-RSM CATERERS [G BLOCK]\n"
        
        if cgpa_text:
            context += f"\nOVERALL ACADEMIC PERFORMANCE:\n{cgpa_text}\n"
        else:
            context += f"\nOVERALL ACADEMIC PERFORMANCE:\n"
            context += f"- CGPA: {cgpa}/10\n"
            context += "- Credits: 84/160 completed\n"
            context += "- Grade Distribution: 10 S, 11 A, 12 B, 4 C, 1 D\n"
        
        context += f"\nCURRENT SEMESTER ({semester}):\n"
        context += f"- Total Courses: {len(marks)}\n"
        context += f"- Average Attendance: {avg_attendance:.1f}%\n"
        context += f"- Courses Below 80% Attendance: {len(low_attendance)}\n"
        context += f"- Active Courses with Marks: {len(marks)}\n\n"
        
        # Add detailed marks information
        context += "CURRENT SEMESTER MARKS:\n"
        for course in marks:
            course_name = course.get('course_name', 'Unknown')
            course_code = course.get('course_code', 'N/A')
            context += f"\n{course_name} ({course_code}):\n"
            
            components = course.get('components', [])
            if components:
                for comp in components:
                    title = comp.get('title', 'Unknown')
                    scored = comp.get('weightage_mark', 0)
                    max_marks = comp.get('weightage', 0)
                    context += f"  • {title}: {scored}/{max_marks}\n"
            
            total = course.get('total_scored', 0)
            weight = course.get('total_weight', 100)
            context += f"  Total: {total}/{weight}\n"
        
        # Add attendance details
        context += "\n\nATTENDANCE BREAKDOWN:\n"
        for att in attendance:
            course = att.get('course_name', att.get('course_code', 'Unknown'))
            percentage = att.get('attendance_percentage', 0)
            attended = att.get('attended_classes', 0)
            total = att.get('total_classes', 0)
            status = "✅ Safe" if percentage >= 85 else "⚠️ Monitor" if percentage >= 75 else "🚨 Critical"
            context += f"  • {course}: {percentage}% ({attended}/{total} classes) {status}\n"
        
        # Add exam schedule
        if exams:
            context += "\n\nUPCOMING EXAMS:\n"
            for exam in exams:
                course = exam.get('course_name', exam.get('course_code', 'Unknown'))
                exam_type = exam.get('exam_type', 'Unknown')
                date = exam.get('date', 'TBD')
                time = exam.get('time', 'TBD')
                slot = exam.get('slot', 'TBD')
                context += f"  • {course} - {exam_type}: {date} at {time} (Slot: {slot})\n"
        
        # Add library dues if available
        if library_text:
            context += f"\n\nLIBRARY STATUS:\n{library_text}\n"
        
        # Add leave status if available
        if leave_text:
            context += f"\n\nLEAVE/TRAVEL STATUS:\n{leave_text}\n"
        
        context += """

YOUR ROLE AS PERSONAL ACADEMIC ASSISTANT:
1. Analyze the student's academic performance with personal insights
2. Give honest opinions about their strengths and weaknesses
3. Provide encouragement when they're doing well
4. Offer constructive feedback on areas needing improvement
5. Suggest specific actions based on the data
6. Help with attendance planning and grade predictions
7. Identify trends and patterns in performance
8. Motivate and guide towards better academic outcomes
9. Provide career guidance based on academic standing
10. Be conversational, friendly, and supportive like a mentor

PERSONALITY GUIDELINES:
- Address them naturally in conversation
- Be warm and encouraging but honest
- Use specific data points when giving advice
- Celebrate achievements and progress
- Point out concerns early with actionable solutions
- Be proactive in suggesting improvements
- Show you care about their academic success

EXAMPLE TONE:
- "Your CGPA is solid! With focused effort on those weaker subjects, you could push even higher"
- "I see you're doing excellently in this course - great work! Keep this consistency"
- "Heads up - your attendance in this course is getting close to the minimum. You can afford to miss X more classes, but let's not cut it too close"
- "Looking at your performance, you're strongest in practical/lab courses. Maybe leverage that strength for project work?"

Be friendly, data-driven, and genuinely invested in the student's academic journey.
"""
        return context
    
    def chat(self, user_message):
        """Process user message and generate response"""
        # Add user message to history
        self.conversation_history.append({
            'role': 'user',
            'content': user_message
        })
        
        # Build full prompt with context and history
        full_prompt = self.context + "\n\nCONVERSATION HISTORY:\n"
        for msg in self.conversation_history[-5:]:  # Last 5 messages for context
            full_prompt += f"{msg['role'].upper()}: {msg['content']}\n"
        
        try:
            # Generate response
            response = self.model.generate_content(full_prompt)
            assistant_message = clean_gemini_output(response.text)
            
            # Add to history
            self.conversation_history.append({
                'role': 'assistant',
                'content': assistant_message
            })
            
            return assistant_message
        
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def interactive_chat(self):
        """Start interactive chat session"""
        print("=" * 60)
        print("🤖 CLI-TOP AI Chatbot")
        print("=" * 60)
        print()
        print(f"Student: {self.vtop_data.get('reg_no', 'N/A')}")
        print(f"Semester: {self.vtop_data.get('semester', 'N/A')}")
        print(f"CGPA: {self.vtop_data.get('cgpa', 'N/A')}")
        print()
        print("I have your complete VTOP data. Ask me anything!")
        print("Type 'quit', 'exit', or 'bye' to end the conversation")
        print("=" * 60)
        print()
        
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    print()
                    print("👋 Goodbye! Good luck with your studies!")
                    break
                
                # Get and display response
                print()
                print("🤖 Assistant:", end=" ")
                response = self.chat(user_input)
                print(response)
                print()
            
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
    
    def quick_question(self, question):
        """Answer a single question without interactive mode"""
        response = self.chat(question)
        print("=" * 60)
        print("🤖 CLI-TOP AI Assistant")
        print("=" * 60)
        print()
        print(f"Question: {question}")
        print()
        print(f"Answer:")
        print(response)
        print()

def load_vtop_data(file_path=None):
    """Load VTOP data from file - uses current_semester_data.json by default"""
    if file_path is None:
        # Default to current_semester_data.json in the ai folder
        file_path = Path(__file__).parent / 'current_semester_data.json'
    
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"❌ Data file not found: {file_path}")
        print("   Available data files:")
        print("   - ai/current_semester_data.json (current semester)")
        print("   - /tmp/all_data.txt (raw VTOP data)")
        return None
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Enhance data with additional context from all_data.txt if available
    all_data_path = Path('/tmp/all_data.txt')
    if all_data_path.exists():
        try:
            with open(all_data_path, 'r') as f:
                all_data_text = f.read()
            
            # Add raw text sections to data for better context
            data['raw_profile'] = all_data_text[all_data_text.find('=== PROFILE ==='):all_data_text.find('=== HOSTEL ===')] if '=== PROFILE ===' in all_data_text else ''
            data['raw_hostel'] = all_data_text[all_data_text.find('=== HOSTEL ==='):all_data_text.find('=== CGPA ===')] if '=== HOSTEL ===' in all_data_text else ''
            data['raw_cgpa'] = all_data_text[all_data_text.find('=== CGPA ==='):all_data_text.find('=== LIBRARY ===')] if '=== CGPA ===' in all_data_text else ''
            data['raw_library'] = all_data_text[all_data_text.find('=== LIBRARY ==='):all_data_text.find('=== LEAVE STATUS ===')] if '=== LIBRARY ===' in all_data_text else ''
            data['raw_leave'] = all_data_text[all_data_text.find('=== LEAVE STATUS ==='):all_data_text.find('=== NIGHTSLIP ===')] if '=== LEAVE STATUS ===' in all_data_text else ''
        except Exception as e:
            print(f"  ℹ️  Could not load additional context from all_data.txt: {e}")
    
    return data

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='CLI-TOP AI Chatbot')
    parser.add_argument('--data', type=str, help='Path to VTOP data JSON file (default: current_semester_data.json)')
    parser.add_argument('--question', '-q', type=str, help='Ask a single question (non-interactive)')
    
    args = parser.parse_args()
    
    # Determine data path
    if args.data:
        data_path = args.data
    else:
        # Default to current_semester_data.json
        data_path = Path(__file__).parent / 'current_semester_data.json'
    
    # Load data
    vtop_data = load_vtop_data(data_path)
    if not vtop_data:
        print()
        print("❌ Error: No VTOP data found")
        print()
        print("Please ensure current_semester_data.json exists in the ai folder")
        print("Or specify a data file: python ai/chatbot.py --data <file.json>")
        sys.exit(1)
    
    print(f"✅ Loaded VTOP data successfully")
    print(f"   Student: {vtop_data.get('reg_no', 'N/A')}")
    print(f"   Semester: {vtop_data.get('semester', 'N/A')}")
    print(f"   CGPA: {vtop_data.get('cgpa', 'N/A')}")
    print()
    
    # Initialize chatbot
    chatbot = VTOPChatbot(vtop_data)
    
    # Handle single question or interactive mode
    if args.question:
        chatbot.quick_question(args.question)
    else:
        chatbot.interactive_chat()

if __name__ == '__main__':
    main()
