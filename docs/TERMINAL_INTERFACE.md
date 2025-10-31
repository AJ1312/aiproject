# CLI-TOP Terminal Interface 🖥️

## Overview

The new terminal-like interface provides a seamless command-line experience in your browser. No more clicking buttons - just type commands like you would in a terminal!

## Quick Start

### 1. Login (Terminal Required - One Time Only)

```bash
cd "/Users/ajiteshsharma/Pictures/cli-top-dev 2"
./cli-top login --username YOUR_USERNAME --password YOUR_PASSWORD --regno YOUR_REGNO
```

### 2. Start the Web Server

```bash
cd website
python server.py
```

### 3. Open Terminal Interface

Navigate to: `http://localhost:5555/terminal.html`

## Features

### Auto-Login Detection
- ✅ Automatically detects saved credentials
- ✅ Shows login status in header
- ✅ No need to login again in browser

### Terminal-Like Interface
- Type commands instead of clicking buttons
- Command history (up/down arrows)
- Monospace font with green-on-black theme
- Auto-scrolling output
- Click on command suggestions to auto-fill

### Available Commands

#### VTOP Commands
```
marks                - View current semester marks
cgpa view            - View CGPA history
attendance           - Check attendance status
timetable            - View class timetable
exams                - View exam schedule
profile              - View student profile
grades view          - View all grades
da                   - View digital assignments
```

#### AI Commands (Offline - No API Required)
```
ai-all               - Run all AI features
ai-attendance        - Attendance skip/recovery optimizer
ai-cgpa              - CGPA what-if calculator
ai-exam              - Exam study time optimizer
```

#### AI Commands (Gemini-Powered - Requires API Key)
```
ai-predict           - Smart grade predictor with subject categorization
```

#### System Commands
```
help                 - Show all available commands
clear                - Clear terminal output
```

## Smart Grade Predictor 🎯

The new **Smart Marks & Grade Predictor** uses Gemini AI to:

1. **Categorize Previous Subjects**: Analyzes your CGPA trend to categorize courses from previous semesters
2. **Categorize Current Subjects**: Maps your current semester courses
3. **Find Similar Subjects**: Uses AI to match current courses with similar previous ones
4. **Predict Grades**: Predicts final marks and grades based on historical patterns

### How It Works

```
Current Semester Course: Advanced Data Structures
                              ↓
                    [Gemini AI Analysis]
                              ↓
Similar Previous Courses: Data Structures & Algorithms (Grade: A)
                         Programming Fundamentals (Grade: S)
                              ↓
                    [Pattern Analysis]
                              ↓
Predicted Grade: A (85% confidence)
```

### Usage

**In Terminal:**
```bash
cd ai
python features/smart_marks_predictor.py
```

**In Web Interface:**
```
$ ai-predict
```

## API Endpoints

### Check Login Status
```
GET /api/check-login

Response:
{
  "logged_in": true,
  "regno": "21BCE1234"
}
```

### Run VTOP Command
```
POST /api/run-command
{
  "command": "marks"
}

Response:
{
  "success": true,
  "output": "... marks data ..."
}
```

### Run All AI Features
```
GET /api/run-all-ai

Response:
{
  "success": true,
  "results": [
    {
      "feature": "Attendance Optimizer",
      "status": "success",
      "data": {...}
    },
    ...
  ]
}
```

### Run Smart Predictor
```
POST /api/smart-grade-predictor

Response:
{
  "success": true,
  "output": {
    "type": "text",
    "content": "... predictions ..."
  }
}
```

## Complete Workflow for New Users

### Step 1: First Time Setup (Terminal)
```bash
# Build CLI-TOP
go build -o cli-top main.go

# Login (saves credentials to cli-top-config.env)
./cli-top login --username YOUR_USERNAME --password YOUR_PASSWORD --regno YOUR_REGNO
```

### Step 2: Install Python Dependencies
```bash
cd ai
pip install -r requirements.txt
```

### Step 3: Configure Gemini API (Optional - for AI features)
```bash
# Edit ai/config.py
GOOGLE_API_KEY = "your-api-key-here"
```

### Step 4: Start Web Server
```bash
cd website
python server.py
```

### Step 5: Use Terminal Interface
1. Open `http://localhost:5555/terminal.html`
2. Interface auto-detects your login
3. Type commands or click suggestions
4. Enjoy terminal-like experience!

## Features for New Users

✅ **One-Time Login**: Login once in terminal, never again in browser
✅ **Auto-Detection**: Website detects saved credentials automatically
✅ **Smart Caching**: VTOP data cached for 30 minutes (prevents logout)
✅ **Rate Limiting**: 2-second delay between requests (protects session)
✅ **Offline AI**: 3 AI features work without any API keys
✅ **Gemini AI**: 8 advanced features with Google Gemini API
✅ **Terminal UX**: Command-line interface in browser
✅ **Progress Indicators**: See loading states for long operations
✅ **Error Handling**: Clear error messages with recovery steps

## Architecture

```
User Terminal
     ↓
./cli-top login
     ↓
cli-top-config.env (credentials saved)
     ↓
     ├─→ CLI-TOP Binary (Go) ──→ VTOP Website
     │        ↓
     │   Data Export (JSON)
     │        ↓
     └─→ Python AI Features
              ├─→ Offline (3 features)
              └─→ Gemini (8 features)
                       ↓
              Flask Web Server (:5555)
                       ↓
              Browser Terminal Interface
```

## File Structure

```
website/
├── server.py           - Flask backend with all endpoints
├── terminal.html       - New terminal-like interface
├── index.html          - Original button-based interface (legacy)
├── script.js           - Original JavaScript
└── styles.css          - Original styles

ai/
├── features/
│   ├── smart_marks_predictor.py    - NEW: Gemini-powered predictor
│   ├── attendance_optimizer.py     - Offline AI
│   ├── cgpa_calculator.py          - Offline AI
│   └── exam_schedule_optimizer.py  - Offline AI
├── vtop_data_manager.py  - Smart caching & rate limiting
└── run_all_features.py   - Batch runner
```

## Troubleshooting

### "Not logged in" Error
```bash
# Solution: Login in terminal first
./cli-top login --username X --password Y --regno Z
```

### "VTOP data not found" Error
```bash
# Solution: Export data first
./cli-top marks  # Any command that fetches data
```

### "Gemini API Error"
```bash
# Solution: Check API key in ai/config.py
# Make sure GOOGLE_API_KEY is set correctly
```

### Smart Predictor Not Working
```bash
# Solution: Ensure you have marks and CGPA trend data
./cli-top marks
./cli-top cgpa view
# Then run predictor
python ai/features/smart_marks_predictor.py
```

## Comparison: Old vs New Interface

| Feature | Old Interface | New Terminal Interface |
|---------|--------------|----------------------|
| Input Method | Click buttons | Type commands |
| UX | Web app | Terminal emulator |
| Login | Re-login in browser | Auto-detected |
| Commands | Limited buttons | All CLI-TOP commands |
| Output | Formatted cards | Raw terminal output |
| AI Features | Separate buttons | Type `ai-` commands |
| Learning Curve | Easy | Requires knowing commands |
| Power User | No | Yes ✅ |

## Tips & Tricks

1. **Use Tab Completion**: Click on command suggestions to auto-fill
2. **Command History**: Use up/down arrows (coming soon)
3. **Batch Operations**: Use `ai-all` to run all features at once
4. **Clear Output**: Type `clear` to clean terminal
5. **Help Anytime**: Type `help` for command reference

## Future Enhancements

- [ ] Command history (up/down arrows)
- [ ] Tab auto-completion
- [ ] Streaming output for long operations
- [ ] WebSocket for real-time updates
- [ ] Command aliases (e.g., `m` for `marks`)
- [ ] Batch command execution
- [ ] Export terminal output
- [ ] Dark/Light theme toggle

## Credits

Built with ❤️ for VIT students by Ajitesh Sharma

**Technologies:**
- Backend: Python Flask
- Frontend: Vanilla JavaScript
- CLI: Go
- AI: Google Gemini API
- Offline AI: Custom algorithms + sklearn

---

Enjoy your new terminal-like VTOP experience! 🚀
