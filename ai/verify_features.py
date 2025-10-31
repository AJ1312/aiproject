#!/usr/bin/env python3
"""
Quick verification script to ensure all AI features are accessible
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("CLI-TOP AI Features Verification")
print("=" * 60)
print()

# Check imports
print("📦 Checking imports...")
try:
    from vtop_data_manager import get_vtop_data, get_data_manager
    print("  ✅ vtop_data_manager")
except Exception as e:
    print(f"  ❌ vtop_data_manager: {e}")

try:
    from live_data_wrapper import run_feature_with_live_data
    print("  ✅ live_data_wrapper")
except Exception as e:
    print(f"  ❌ live_data_wrapper: {e}")

print()

# Check features
print("🎯 Checking AI features...")
features = [
    ('features.smart_grade_predictor', 'Smart Grade Predictor (Gemini)'),
    ('features.study_optimizer', 'Study Optimizer (Gemini)'),
    ('features.semester_insights', 'Semester Insights (Gemini)'),
    ('features.study_guide', 'Study Guide (Gemini)'),
    ('features.vtop_coach', 'VTOP Coach (Gemini)'),
    ('features.performance_insights', 'Performance Insights (Gemini)'),
    ('features.career_advisor', 'Career Advisor (Gemini)'),
    ('features.academic_performance_ml', 'Academic Performance ML (scikit-learn)'),
]

feature_count = 0
for module_name, display_name in features:
    try:
        import importlib
        module = importlib.import_module(module_name)
        if hasattr(module, 'main'):
            print(f"  ✅ {display_name}")
            feature_count += 1
        else:
            print(f"  ⚠️  {display_name} (no main() function)")
    except Exception as e:
        print(f"  ❌ {display_name}: {e}")

print()

# Check data manager
print("🔧 Checking data manager...")
try:
    manager = get_data_manager()
    age = manager.get_cache_age()
    is_valid = manager._is_cache_valid()
    
    if age:
        print(f"  📊 Cache age: {age}")
        print(f"  📊 Cache valid: {is_valid}")
    else:
        print("  📊 No cache present")
    
    print("  ✅ Data manager functional")
except Exception as e:
    print(f"  ❌ Data manager: {e}")

print()

# Summary
print("=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"✅ Working features: {feature_count}/8")
print()

if feature_count == 8:
    print("🎉 All AI features are accessible!")
    print()
    print("Usage:")
    print("  python live_data_wrapper.py <feature_name>")
    print("  python run_all_features.py")
    print("  python chatbot.py")
else:
    print("⚠️  Some features may have issues")

print("=" * 60)
