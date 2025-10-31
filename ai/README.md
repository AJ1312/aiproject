# CLI-TOP AI Features

Intelligent AI-powered analysis of your VTOP academic data.

## 🎯 Overview

This folder contains **AI-powered features** that analyze your VTOP data using:
- **Gemini AI** (7 features) - Advanced language model analysis
- **Machine Learning** (1 feature) - scikit-learn algorithms (clustering, regression)
- **Smart Data Management** - Intelligent caching and rate limiting

## 📁 Structure

```
ai/
├── features/               # AI-powered analysis features
│   ├── smart_grade_predictor.py      # Multi-semester grade prediction (Gemini)
│   ├── study_optimizer.py            # AI study plan optimization (Gemini)
│   ├── semester_insights.py          # Comprehensive semester analysis (Gemini)
│   ├── study_guide.py                # Course-specific study guides (Gemini)
│   ├── vtop_coach.py                 # Performance coaching & roasting (Gemini)
│   ├── performance_insights.py       # Deep performance analysis (Gemini)
│   ├── career_advisor.py             # Career guidance (Gemini)
│   └── academic_performance_ml.py    # ML clustering & predictions (scikit-learn)
│
├── vtop_data_manager.py    # Smart data fetching with caching & rate limiting
├── live_data_wrapper.py    # Wrapper for running features with live data
├── chatbot.py              # Interactive AI chatbot
├── run_all_features.py     # Run all AI features at once
├── config.py               # Configuration (API keys)
└── requirements.txt        # Python dependencies

```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd ai
pip install -r requirements.txt
```

### 2. Configure API Key

Create `config.py` (or `.env`):

```python
GOOGLE_API_KEY = "your-gemini-api-key-here"
GEMINI_MODEL = "gemini-2.0-flash-exp"
```

### 3. Run Features

**Individual Feature:**
```bash
python live_data_wrapper.py smart_grade_predictor
```

**All Features:**
```bash
python run_all_features.py
```

**Interactive Chatbot:**
```bash
python chatbot.py
```

## 🤖 AI Features

### Gemini-Powered Features

1. **Smart Grade Predictor** (`smart_grade_predictor.py`)
   - Analyzes multiple semesters of data
   - Uses Gemini to categorize subjects
   - Predicts final grades with AI insights
   - 5-step progress indicator

2. **Study Optimizer** (`study_optimizer.py`)
   - Creates personalized study plans
   - Optimizes time allocation
   - AI-powered recommendations

3. **Semester Insights** (`semester_insights.py`)
   - Comprehensive semester analysis
   - Performance trends
   - Actionable insights

4. **Study Guide** (`study_guide.py`)
   - Course-specific study materials
   - Syllabus-based guidance
   - Personalized recommendations

5. **VTOP Coach** (`vtop_coach.py`)
   - Performance coaching
   - Motivational roasting
   - Actionable advice

6. **Performance Insights** (`performance_insights.py`)
   - Deep dive into performance metrics
   - Comparative analysis
   - Improvement suggestions

7. **Career Advisor** (`career_advisor.py`)
   - Career path recommendations
   - Based on academic performance
   - Industry insights

### Machine Learning Feature

8. **Academic Performance ML** (`academic_performance_ml.py`)
   - **KMeans Clustering**: Groups similar courses
   - **Linear Regression**: Predicts final grades
   - **CGPA Trajectory**: Analyzes trend across semesters
   - **No API required** - Uses scikit-learn locally

## 📊 Smart Data Management

### VTOP Data Manager

The `vtop_data_manager.py` module provides intelligent data fetching:

**Features:**
- **Smart Caching**: 30-minute cache duration (configurable)
- **Rate Limiting**: Minimum 2 seconds between VTOP requests
- **Prevents Logout**: Avoids too many requests that cause session timeout
- **Automatic Refresh**: Fetches fresh data when cache expires

**Usage:**
```python
from vtop_data_manager import get_vtop_data

# Get data (uses cache if valid)
data = get_vtop_data(use_cache=True)

# Force refresh
from vtop_data_manager import get_data_manager
manager = get_data_manager()
fresh_data = manager.force_refresh()

# Check cache status
age = manager.get_cache_age()
print(f"Cache age: {age}")
```

## 🔧 Configuration

### Cache Duration

Modify cache duration in `vtop_data_manager.py`:

```python
manager = VTOPDataManager(cache_duration_minutes=30)  # Default: 30 min
```

### Rate Limiting

Adjust minimum request interval:

```python
# In vtop_data_manager.py
self.min_request_interval = 2.0  # Seconds between requests
```

## 📝 Data Format

All features expect VTOP data in this format:

```json
{
  "reg_no": "21BCE9999",
  "semester": "Fall 2025",
  "cgpa": 8.5,
  "marks": [...],
  "attendance": [...],
  "exams": [...],
  "cgpa_trend": [...],
  "generated_at": "2025-10-31T12:00:00"
}
```

Data is fetched automatically using `./cli-top ai export`.

## 🎭 Running Features

### Method 1: Live Data Wrapper (Recommended)

```bash
python live_data_wrapper.py <feature_name>
```

**Available features:**
- `smart_grade_predictor`
- `study_optimizer`
- `semester_insights`
- `study_guide`
- `vtop_coach`
- `performance_insights`
- `career_advisor`
- `academic_performance_ml`

### Method 2: Direct Execution

```bash
cd features
python smart_grade_predictor.py
```

### Method 3: All Features

```bash
python run_all_features.py
```

## 🔐 API Keys

**Gemini API Key** (Free):
1. Visit https://makersuite.google.com/app/apikey
2. Create an API key
3. Add to `config.py` or `cli-top-config.env`

**No API Key Required:**
- Academic Performance ML feature
- Chatbot can work without API (limited)

## 🎯 Best Practices

1. **Use Caching**: Always use `use_cache=True` unless you need fresh data
2. **Rate Limiting**: Let the data manager handle requests automatically
3. **Batch Operations**: Run multiple features at once with `run_all_features.py`
4. **Monitor Cache**: Check cache age to understand freshness

## 🐛 Troubleshooting

**"Login succeeded but credentials not saved"**
- Use CLI-TOP login in terminal: `./cli-top login --username YOUR_USERNAME --password YOUR_PASSWORD --regno YOUR_REGNO`
- Credentials saved to `cli-top-config.env`

**"Too many requests" / Session logout**
- Data manager prevents this with rate limiting
- Increase cache duration if needed
- Wait 2 seconds between manual VTOP calls

**"Import errors"**
- Install dependencies: `pip install -r requirements.txt`
- Ensure Python 3.8+

**"No Gemini API key"**
- Add key to `config.py`
- Or use ML feature (no API needed)

## 📚 Examples

### Example 1: Check Cache Status

```bash
python vtop_data_manager.py --status
```

### Example 2: Force Data Refresh

```bash
python vtop_data_manager.py --refresh
```

### Example 3: Clear Cache

```bash
python vtop_data_manager.py --clear
```

### Example 4: Run Specific Feature

```bash
python live_data_wrapper.py academic_performance_ml
```

## 🌟 Features Removed

The following **non-AI algorithm-only features** have been removed:
- `grade_predictor.py` - Simple calculation, no AI
- `performance_analyzer.py` - Basic statistics, no AI
- `study_allocator.py` - Simple allocation, no AI
- `weakness_identifier.py` - Rule-based, no AI

**Reason**: Focus on actual AI features (Gemini + ML)

## 📄 License

Part of CLI-TOP project. See main README for license.

## 🤝 Contributing

To add a new AI feature:

1. Create feature file in `features/`
2. Add `main()` function
3. Use `get_vtop_data()` for data
4. Update `live_data_wrapper.py` feature map
5. Update this README

## ⚡ Performance

- **Caching**: ~10ms (cache hit)
- **Fresh Fetch**: ~5-10s (VTOP export + parse)
- **Rate Limiting**: 2s minimum between requests
- **Gemini Features**: 2-5s per feature (API call)
- **ML Features**: <1s (local computation)

## 🔮 Future Enhancements

- [ ] Multi-semester comparison
- [ ] Predictive analytics for next semester
- [ ] Peer comparison (anonymized)
- [ ] Study group recommendations
- [ ] Real-time performance tracking

---

**Made with ❤️ for VIT Students**
