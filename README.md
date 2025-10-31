# CLI-TOP AI - Complete VTOP Management + AI Features

A comprehensive command-line and web interface for VIT VTOP with intelligent AI features for academic planning, performance analysis, and personalized insights.

## 🌟 Features

### VTOP Features (21 Total)
- 📊 **Academic**: Marks, Grades, CGPA tracking
- 📅 **Attendance**: Monitor and calculate attendance
- 📝 **Exams**: Schedule and timetable
- 👤 **Profile**: Student information and hostel details
- 📚 **Library**: Check dues and books
- 🧾 **Finance**: Fee receipts and payments

### AI Features (9 Offline Data-Driven)
- 📊 **Attendance Calculator**: Classes you can miss safely
- 🎯 **Grade Predictor**: Predict final grades based on current performance
- 📈 **CGPA Analyzer**: Impact analysis of different grade scenarios
- 🔄 **Attendance Recovery**: Plan to recover low attendance
- 📝 **Exam Readiness**: Calculate readiness score before exams
- ⏰ **Study Allocator**: Optimal time distribution across subjects
- 📊 **Performance Analyzer**: Identify trends and patterns
- 💪 **Weakness Identifier**: Find areas needing improvement
- 🎯 **Target Planner**: Calculate scores needed for target grades

### Advanced AI Features (6 Cloud-Powered)
- 💬 **AI Chatbot**: Natural language interface with full VTOP context
- 📊 **Performance Insights**: Deep analysis by Gemini LLM
- 💼 **Career Guidance**: AI-powered career recommendations
- 📅 **Study Optimizer**: Personalized study plans
- 📖 **Study Guide**: Topic-wise materials and practice questions
- 🎙️ **Voice Assistant**: Voice-controlled interface
- 🔥 **Roast Mode**: Brutally honest feedback (fun feature!)

## 🚀 Quick Start

### Option 1: Web Interface (Easiest)

```bash
# 1. Clone repository
git clone https://github.com/AJ1312/aiproject.git
cd aiproject

# 2. Run setup wizard
chmod +x setup.sh
./setup.sh

# 3. Start web server
cd website
python3 server.py

# 4. Open browser
# Navigate to http://localhost:5555
```

The web interface will guide you through:
1. **Login**: Enter VTOP credentials (saved securely locally)
2. **AI Setup**: Automatic personalization with your data
3. **Ready to Use**: Access all features from the browser

### Option 2: CLI (Traditional)

```bash
# 1. Build CLI-TOP
go build -o cli-top main.go

# 2. Login and use
./cli-top marks
./cli-top attendance
./cli-top profile

# 3. Setup AI features
cd ai
pip3 install -r requirements.txt
python3 parse_current_semester.py

# 4. Use AI
python3 chatbot.py
python3 run_all_features.py current_semester_data.json
```

## 📖 Detailed Setup

### Prerequisites
- **Go 1.21+** (for CLI-TOP binary)
- **Python 3.8+** (for AI features)
- **VTOP Account** (VIT student credentials)

### Installation

1. **Clone & Build**
```bash
git clone https://github.com/AJ1312/aiproject.git
cd aiproject
go build -o cli-top main.go
```

2. **Install Python Dependencies**
```bash
cd ai
pip3 install -r requirements.txt
```

3. **Configure Credentials**
   - **Web**: Use the setup wizard at http://localhost:5555
   - **CLI**: Run `./cli-top profile` (creates `cli-top-config.env` automatically)

4. **Generate AI Context** (Required for AI features)
```bash
# Export VTOP data
./cli-top ai export -o /tmp/all_data.txt

# Parse and create AI context
cd ai
python3 parse_current_semester.py
```

This creates `ai/current_semester_data.json` with your personalized academic data.

## 🎯 Usage Examples

### Web Interface

1. Open http://localhost:5555
2. Complete one-time setup if needed
3. Click any feature card to execute
4. AI features work automatically with your data

### CLI Interface

```bash
# View marks
./cli-top marks

# Check attendance
./cli-top attendance

# Calculate CGPA
./cli-top cgpa view

# Run AI grade predictor
cd ai
python3 features/grade_predictor.py current_semester_data.json

# Chat with AI
python3 chatbot.py

# Run all AI analyses
python3 run_all_features.py current_semester_data.json
```

### Advanced AI Features

```bash
# Career guidance (requires Google Gemini API key)
cd ai/gemini_features
python3 career_advisor.py ../current_semester_data.json

# Performance insights
python3 performance_insights.py ../current_semester_data.json

# Study plan
python3 study_optimizer.py ../current_semester_data.json

# Voice assistant (requires microphone)
python3 voice_assistant.py
```

## 🔐 Privacy & Security

- **All data stored locally** on your machine
- **No cloud storage** of credentials or academic data
- **Open source** - audit the code yourself
- **Encrypted credentials** in local config file
- **Gemini API** used only for advanced AI features (optional)

## 🛠️ Configuration

### Environment Variables

Create `ai/config.py` for Gemini features:

```python
# Google Gemini API (optional - for advanced AI features only)
GOOGLE_API_KEY = "your-api-key-here"  # Get from https://makersuite.google.com/app/apikey
GEMINI_MODEL = "gemini-2.0-flash-exp"  # Or gemini-1.5-pro

# Paths (auto-configured)
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / 'outputs'
DATA_DIR = BASE_DIR / 'data'
```

### Credentials File

`cli-top-config.env` is auto-generated on first login:
```env
CSRF="..."
JSESSIONID="..."
KEY="..."
PASSWORD="..."
REGNO="..."
SERVERID="..."
UUID="..."
VTOP_USERNAME="..."
```

**Never commit this file to Git!**

## 📊 Project Structure

```
cli-top/
├── main.go                 # CLI-TOP main entry
├── setup.sh               # Setup wizard script
├── cli-top                # Compiled binary
├── cmd/                   # CLI commands
├── features/              # VTOP feature implementations
├── helpers/               # Utility functions
├── ai/                    # AI features
│   ├── chatbot.py        # Interactive AI chatbot
│   ├── parse_current_semester.py  # Data parser
│   ├── config.py         # AI configuration
│   ├── features/         # Offline AI features
│   │   ├── grade_predictor.py
│   │   ├── attendance_calculator.py
│   │   └── ...
│   └── gemini_features/  # Cloud AI features
│       ├── career_advisor.py
│       ├── performance_insights.py
│       └── ...
└── website/              # Web interface
    ├── server.py         # Flask backend
    ├── index.html        # Frontend
    ├── script.js         # Frontend logic
    └── styles.css        # Styling
```

## 🤝 Contributing

Contributions welcome! This project is designed to be easily customizable for any VIT student.

1. Fork the repository
2. Create your feature branch
3. Test thoroughly
4. Submit a pull request

## 📝 License

MIT License - Feel free to use and modify for your needs.

## ⚠️ Disclaimer

This project is an unofficial tool created by students for students. It is not affiliated with or endorsed by VIT University. Use responsibly and follow your institution's policies.

## 🙏 Credits

- Built by VIT students for VIT students
- Uses Google Gemini for advanced AI features
- Inspired by the need for better VTOP access

## 📞 Support

- **Issues**: Open a GitHub issue
- **Discussions**: Use GitHub Discussions
- **Documentation**: Check `docs/` folder for detailed guides

## 🎓 For Students

This tool helps you:
- ✅ Track academic performance easily
- ✅ Plan attendance strategically  
- ✅ Predict grades before exams
- ✅ Get personalized AI study advice
- ✅ Access VTOP faster than the official portal
- ✅ Make data-driven academic decisions

**Study smart, not just hard!** 🚀

---

Made with ❤️ for VIT Students | Star ⭐ if you find this helpful!
