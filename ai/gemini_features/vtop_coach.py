#!/usr/bin/env python3
"""
Feature C: VTOP Motivational Coach
A fun AI feature that motivates students based on their performance
"""

import json
import sys
from pathlib import Path
import random

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import google.generativeai as genai
from config import GOOGLE_API_KEY, GEMINI_MODEL, TEMPERATURE, OUTPUT_DIR
from utils.formatters import clean_gemini_output


def load_vtop_data(file_path):
    """Load VTOP exported data"""
    with open(file_path, 'r') as f:
        return json.load(f)


def analyze_performance(vtop_data):
    """Analyze overall performance for coaching"""
    total_subjects = len(vtop_data.get('marks', []))
    
    strong_count = 0
    weak_count = 0
    total_internal_pct = 0
    
    attendance_issues = []
    attendance_perfect = []
    
    for course in vtop_data.get('marks', []):
        # Calculate internal percentage from components
        internal_total = 0
        components = course.get('components', [])
        
        for comp in components:
            weightage_mark = comp.get('weightage_mark', 0)
            internal_total += weightage_mark
        
        # Internal is out of 60 (CAT1+CAT2+DA+Quiz1+Quiz2)
        internal_pct = (internal_total / 60) * 100 if internal_total > 0 else 0
        total_internal_pct += internal_pct
        
        if internal_pct >= 80:
            strong_count += 1
        elif internal_pct < 70:
            weak_count += 1
    
    # Check attendance
    for att in vtop_data.get('attendance', []):
        course_code = att.get('course_code', '')
        attended = att.get('attended', 0)
        total = att.get('total', 0)
        percentage = (attended / total * 100) if total > 0 else 0
        
        if percentage < 75:
            attendance_issues.append((course_code, percentage))
        elif percentage >= 95:
            attendance_perfect.append((course_code, percentage))
    
    avg_internal_pct = total_internal_pct / total_subjects if total_subjects > 0 else 0
    
    return {
        'total_subjects': total_subjects,
        'strong_count': strong_count,
        'weak_count': weak_count,
        'avg_internal_pct': avg_internal_pct,
        'attendance_issues': attendance_issues,
        'attendance_perfect': attendance_perfect,
        'cgpa': vtop_data.get('cgpa', 0)
    }


def generate_message(vtop_data, stats, mode='motivational'):
    """Generate motivational or roast message using Advanced AI"""
    
    if not GOOGLE_API_KEY:
        return "❌ Error: GOOGLE_API_KEY not configured"
    
    # Configure Advanced AI
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
    
    # Build context
    context = f"""
Student Statistics:
- CGPA: {stats['cgpa']}
- Total Subjects: {stats['total_subjects']}
- Strong Subjects (80%+): {stats['strong_count']}
- Weak Subjects (<70%): {stats['weak_count']}
- Average Internal: {stats['avg_internal_pct']:.1f}%
- Attendance Issues (<75%): {len(stats['attendance_issues'])} subjects
- Perfect Attendance (95%+): {len(stats['attendance_perfect'])} subjects
"""
    
    if mode == 'roast':
        prompt = f"""You are a brutally honest, savage AI roast master who gives DARK and HILARIOUS roasts to VIT students about their academic performance. NO HOLDING BACK.

{context}

ROAST this student HARD. Make it DARK and FUNNY. Rules:
1. Be ABSOLUTELY SAVAGE - this is a roast, not a pep talk
2. Use dark humor, sarcasm, and brutal honesty
3. Call out every contradiction, every failure, every weak point
4. Use Gen-Z slang and meme references (💀, "bro really thought", "the audacity", etc.)
5. Compare their scores to everyday failures (like ordering extra cheese but getting none)
6. Mock their choices, their attendance, their study habits
7. End with ONE line of tough love (but still harsh)
8. Keep it under 350 words but pack MAXIMUM DAMAGE
9. Use fire emojis, skull emojis, and coffin emojis

Example style: 
"CGPA 8.44 but 30% internal average? 💀 Bro woke up and chose CONFUSION. That's like being rich on paper but broke in real life. The math ain't mathing. 

You're out here collecting participation trophies while the grades are running away like they saw their ex. Seven subjects need attention? That's not a study plan, that's a rescue mission. 

VIT really gave you admission and you said 'let me speedrun academic mediocrity' 😭 The attendance might be decent but these internals are sending thoughts and prayers to themselves.

You got the CGPA of someone who studies but the internals of someone who just discovered Netflix. Pick a struggle bestie, you can't have both.

Wake up call: CAT2 is coming and it's bringing your nightmares with it. Fix this before the semester roasts you harder than I just did. 🔥"

Now absolutely DEMOLISH this student's performance with dark humor:
"""
    
    elif mode == 'motivational':
        prompt = f"""You are an energetic, supportive AI motivational coach for VIT students.

{context}

Create an uplifting, motivational message that:
1. Celebrates their wins (even small ones)
2. Acknowledges challenges without dwelling on them
3. Provides 3 specific, actionable tips for improvement
4. Uses powerful, inspiring language
5. Includes a memorable quote or mantra
6. Keep it under 300 words
7. Use motivational emojis ⚡🔥💪

Focus on growth mindset and VIT-specific advice. Make them feel like they can ace the FAT!
"""
    
    else:  # fun facts
        prompt = f"""You are a fun, quirky AI that shares interesting academic facts and study tips.

{context}

Based on their performance, share:
1. A fun fact about learning/memory/studying
2. A lesser-known VIT hack or tip
3. A study technique that might help them
4. A motivational science fact
5. End with an encouraging message

Keep it fun, informative, and under 250 words. Use emojis! 🧠✨
"""
    
    try:
        # More aggressive settings for roast mode
        if mode == 'roast':
            response = model.generate_content(
                prompt,
                generation_config={
                    'temperature': 1.0,  # Maximum creativity for savage roasts
                    'max_output_tokens': 600,
                    'top_p': 0.95,
                    'top_k': 40
                },
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                ]
            )
        else:
            response = model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.8,
                    'max_output_tokens': 512
                },
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                ]
            )
        
        # Handle blocked responses
        if response.candidates and response.candidates[0].finish_reason == 2:
            return f"""🔥💀 ACADEMIC ROAST - NO MERCY EDITION 💀🔥

Alright, let's talk about this trainwreck:

📊 Your "Stats" (if we can even call them that):
• CGPA: {stats['cgpa']}/10 (Congrats on the bare minimum flexibility)
• Internal Average: {stats['avg_internal_pct']:.1f}% (That's not a score, that's a cry for help)
• Strong Subjects: {stats['strong_count']}/{stats['total_subjects']} (Yikes)
• Needs CPR: {stats['weak_count']}/{stats['total_subjects']} subjects

� THE BRUTAL TRUTH:
You got an {stats['cgpa']} CGPA which is... fine I guess? But that {stats['avg_internal_pct']:.1f}% internal average? BRO. 💀

That's not academic performance, that's academic EXISTENCE. You're out here collecting grades like Pokémon cards but forgetting to actually LEVEL UP.

{stats['weak_count']} subjects need attention? That's not a to-do list, that's a SURVIVAL GUIDE. You're basically the academic equivalent of "it runs but barely."

The way you're going, CAT2 isn't gonna test you - it's gonna ROAST you. And unlike me, it won't be funny.

🎯 Fix This Before It's Too Late:
1. Stop treating internals like optional side quests
2. Those {stats['weak_count']} subjects? They need a RESURRECTION, not attention
3. Study like your degree depends on it (because it literally does)

Real talk: You got into VIT. That means you CAN do better. So stop playing games and START PLAYING TO WIN. The semester won't wait for your character development arc. 

Get it together. The FAT is coming and it's bringing CONSEQUENCES. 🔥

- Your Brutally Honest AI Coach"""
        
        return clean_gemini_output(response.text)

    except Exception as e:
        return f"❌ Error generating message: {str(e)}"


def main():
    if len(sys.argv) < 2:
        print("Usage: python vtop_coach.py <vtop_data.json> [mode]")
        print("Modes: motivational (default), roast, funfacts")
        sys.exit(1)
    
    vtop_file = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else 'motivational'
    
    if not Path(vtop_file).exists():
        print(f"❌ Error: File not found: {vtop_file}")
        sys.exit(1)
    
    mode_emojis = {
        'motivational': '💪 MOTIVATIONAL COACH',
        'roast': '🔥 ROAST MODE ACTIVATED',
        'funfacts': '🧠 VTOP FUN FACTS'
    }
    
    titles = {
        'motivational': 'MOTIVATIONAL COACH',
        'roast': 'ROAST MODE ACTIVATED',
        'funfacts': 'VTOP FUN FACTS'
    }
    
    print("="*80)
    print(mode_emojis.get(mode, '🎮 VTOP COACH'))
    print("Powered by Advanced Gemma LLM")
    print("="*80)
    print()
    
    # Load data
    vtop_data = load_vtop_data(vtop_file)
    
    # Analyze performance
    print("📊 Analyzing your performance...")
    stats = analyze_performance(vtop_data)
    
    # Generate message
    print(f"🤖 Generating {mode} message...\n")
    message = generate_message(vtop_data, stats, mode)
    
    # Display
    print(message)
    print()
    
    # Save to file
    output_file = OUTPUT_DIR / f'vtop_coach_{mode}.txt'
    
    with open(output_file, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write(f"{titles[mode]}\n")
        f.write("=" * 70 + "\n\n")
        f.write(message)
        f.write("\n\n" + "=" * 70 + "\n")
        f.write("Powered by Advanced Gemma LLM\n")
        f.write("=" * 70 + "\n")
    
    print(f"✓ Message saved to: {output_file}")
    print()
    
    # Show quick stats
    print("📊 Quick Stats:")
    print(f"   CGPA: {stats['cgpa']}")
    print(f"   Average Internal: {stats['avg_internal_pct']:.1f}%")
    print(f"   Strong Subjects: {stats['strong_count']}/{stats['total_subjects']}")
    print(f"   Needs Attention: {stats['weak_count']}/{stats['total_subjects']}")
    print()


if __name__ == "__main__":
    main()
