# 🚀 CLI-TOP Quick Start Guide

## For New Users - Complete Setup in 5 Minutes

### Step 1: Build CLI-TOP (One Time)
```bash
cd "/Users/ajiteshsharma/Pictures/cli-top-dev 2"
go build -o cli-top main.go
```

### Step 2: Login (One Time - Saves Credentials)
```bash
./cli-top login --username YOUR_USERNAME --password YOUR_PASSWORD --regno YOUR_REGNO
```
This saves your credentials to `cli-top-config.env` - you never need to login again!

### Step 3: Install Python Dependencies (One Time)
```bash
cd ai
pip install -r requirements.txt
```

### Step 4: Configure Gemini API (Optional - for AI features)
Edit `ai/config.py`:
```python
GOOGLE_API_KEY = "your-google-gemini-api-key-here"
```

### Step 5: Start the Web Server
```bash
cd website
python server.py
```
Server starts on `http://localhost:5555`

### Step 6: Use the Terminal Interface
Open in browser: **http://localhost:5555/terminal.html**

---

## Terminal Commands Reference

### System Commands
```bash
help                 # Show all commands
clear                # Clear terminal output
```

### VTOP Commands
```bash
marks                # Current semester marks
cgpa view            # CGPA history
attendance           # Attendance status
timetable            # Class schedule
exams                # Exam schedule
profile              # Student profile
grades view          # All grades
da                   # Digital assignments
```

### AI Commands (Offline - No API Required)
```bash
ai-attendance        # Skip planning & recovery optimizer
ai-cgpa              # What-if CGPA calculator
ai-exam              # Study time allocation optimizer
ai-all               # Run all offline features
```

### AI Commands (Gemini - Requires API Key)
```bash
ai-predict           # Smart grade predictor with AI categorization
```

---

## Quick Examples

### Example 1: Check Your Marks
1. Open `http://localhost:5555/terminal.html`
2. Type: `marks`
3. Press Enter or click RUN

### Example 2: Get CGPA What-If Scenarios
```bash
$ ai-cgpa
```
Shows:
- Current CGPA prediction
- What grades you need for target CGPA
- Grade distribution analysis

### Example 3: Smart Grade Predictor
```bash
$ ai-predict
```
Uses Gemini AI to:
1. Categorize your previous semester subjects
2. Find similar subjects in current semester
3. Predict your final grades based on patterns

### Example 4: Optimize Attendance
```bash
$ ai-attendance
```
Shows:
- Which classes you can skip
- How many more classes needed for 75%
- Recovery plans if below threshold

---

## Understanding the Terminal Interface

### Status Indicator
- 🟢 **"Logged in as 21BCE1234"** - Ready to use
- 🔴 **"Not logged in"** - Run `./cli-top login` in terminal first

### Command Input
- Type your command in the input box
- Press Enter or click RUN button
- Or click on command suggestions to auto-fill

### Output Area
- Scrolls automatically to show latest output
- Color-coded:
  - 🔵 Blue = Commands you typed
  - 🟢 Green = Success/Output
  - 🔴 Red = Errors
  - 🟡 Yellow = Info messages

---

## Troubleshooting

### ❌ "Not logged in" error
**Solution:**
```bash
./cli-top login --username X --password Y --regno Z
```

### ❌ "Connection error"
**Solution:**
```bash
cd website
python server.py
```

### ❌ "Gemini API Error"
**Solution:** Check `ai/config.py` has valid `GOOGLE_API_KEY`

### ❌ Smart predictor shows no data
**Solution:** Fetch VTOP data first:
```bash
./cli-top marks
./cli-top cgpa view
```

---

## What Makes This Special?

### 🎯 Smart Features
- **AI Subject Categorization**: Gemini understands course relationships
- **Grade Predictions**: Based on your historical performance patterns
- **Auto-Login**: Login once, use everywhere
- **Smart Caching**: 30-minute cache prevents VTOP logout

### ⚡ Fast & Efficient
- **Offline AI**: 3 features work without internet
- **Rate Limiting**: 2-second delays protect your session
- **Background Processing**: Long operations don't block UI

### 🛡️ Safe & Secure
- Credentials stored locally (never sent to cloud)
- No data logging or tracking
- Open source - verify yourself

---

## Project Structure

```
cli-top-dev 2/
├── cli-top              # Binary (run VTOP commands)
├── cli-top-config.env   # Your saved credentials
│
├── ai/
│   ├── features/
│   │   ├── smart_marks_predictor.py    # NEW: Gemini predictor
│   │   ├── attendance_optimizer.py     # Offline
│   │   ├── cgpa_calculator.py          # Offline
│   │   └── exam_schedule_optimizer.py  # Offline
│   │
│   ├── vtop_data_manager.py   # Smart caching
│   └── run_all_features.py    # Batch runner
│
└── website/
    ├── server.py         # Flask backend
    ├── terminal.html     # NEW: Terminal interface
    └── index.html        # Old button interface
```

---

## Advanced Usage

### Run All AI Features at Once
```bash
$ ai-all
```

### Direct Python Execution
```bash
cd ai
python features/smart_marks_predictor.py
```

### Batch Mode (Terminal)
```bash
cd ai
python run_all_features.py              # Offline features
python run_all_features.py --gemini     # Gemini features
python run_all_features.py --all        # Everything
```

---

## Tips & Tricks

1. **Quick Commands**: Click on suggested commands to auto-fill
2. **Clear Screen**: Type `clear` when output gets cluttered
3. **Help Anytime**: Type `help` to see all commands
4. **Test First**: Use offline AI features before configuring Gemini
5. **Keep Server Running**: Leave `python server.py` running in background

---

## Feature Count

**Total: 12 AI Features**

1. 🤖 **Offline AI (3)** - Work without API:
   - Attendance Optimizer
   - CGPA Calculator  
   - Exam Schedule Optimizer

2. 🌟 **Gemini AI (8)** - Require API key:
   - **Smart Marks Predictor** ⭐ NEW
   - Study Optimizer
   - Semester Insights
   - Study Guide
   - VTOP Coach
   - Performance Insights
   - Career Advisor
   - Voice Assistant

3. 🧮 **ML (1)** - Requires sklearn:
   - Academic Performance ML

---

## Next Steps

1. ✅ **Test Basic Commands**: Try `marks`, `cgpa view`
2. ✅ **Test Offline AI**: Run `ai-attendance`, `ai-cgpa`
3. ✅ **Configure Gemini**: Add API key to `config.py`
4. ✅ **Test Smart Predictor**: Run `ai-predict`
5. ✅ **Explore More**: Try all commands from help section

---

## Documentation

- **Terminal Guide**: `docs/TERMINAL_INTERFACE.md`
- **Implementation**: `docs/TERMINAL_SMART_PREDICTOR_SUMMARY.md`
- **AI Features**: `FINAL_AI_FEATURES_SUMMARY.md`
- **Main README**: `README.md`

---

## Support

**Issues?** Check troubleshooting section above

**Questions?** Read the comprehensive docs

**Want to Contribute?** Project is open source!

---

**Built with ❤️ for VIT students**

*Enjoy your terminal-like VTOP experience!* 🚀
