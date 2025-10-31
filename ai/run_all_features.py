#!/usr/bin/env python3
"""
All AI Features Runner
Runs all offline AI features (default) or Gemini features (with --gemini flag)
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path

# Add features directory to path
sys.path.insert(0, str(Path(__file__).parent))

from vtop_data_manager import get_vtop_data
from utils.formatters import print_header, print_section


def run_offline_features():
    """
    Execute all offline AI features (no API required)
    
    Offline Features:
    1. Attendance Optimizer - Skip planning & recovery
    2. CGPA Calculator - What-if scenarios
    3. Exam Schedule Optimizer - Study time allocation
    4. Academic Performance ML - Clustering & predictions (if sklearn available)
    """
    
    print_header("CLI-TOP OFFLINE AI FEATURES")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    # Get VTOP data (uses smart caching)
    print("📊 Loading VTOP data...")
    vtop_data = get_vtop_data(use_cache=True)
    
    print(f"Student: {vtop_data.get('reg_no', 'N/A')}")
    print(f"CGPA: {vtop_data.get('cgpa', 'N/A')}")
    print("=" * 80)
    print()
    
    offline_features = [
        ('attendance_optimizer', '📊 Attendance Optimizer'),
        ('cgpa_calculator', '🎯 CGPA Calculator'),
        ('exam_schedule_optimizer', '📅 Exam Schedule Optimizer'),
    ]
    
    # Try to add ML feature if sklearn is available
    try:
        import sklearn
        offline_features.append(('academic_performance_ml', '🤖 Academic Performance ML'))
    except ImportError:
        print("⚠️  sklearn not available - skipping ML feature")
        print()
    
    feature_count = 0
    
    for idx, (feature_module, feature_name) in enumerate(offline_features, 1):
        print_section(f"{idx}. {feature_name}")
        try:
            # Dynamic import and run
            import importlib
            module = importlib.import_module(f'features.{feature_module}')
            
            if hasattr(module, 'main'):
                module.main()
                feature_count += 1
            else:
                print(f"  ⚠️  No main() function in {feature_module}")
            print()
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            import traceback
            traceback.print_exc()
            print()
    
    # Summary
    print("=" * 80)
    print_header("SUMMARY")
    print(f"✅ Features executed: {feature_count}/{len(offline_features)}")
    print()
    print("💡 All features ran offline without API keys!")
    print("=" * 80)


def run_gemini_features():
    """
    Execute all Gemini-powered AI features (requires API key)
    
    Gemini Features:
    1. Smart Grade Predictor
    2. Study Optimizer
    3. Semester Insights
    4. Study Guide
    5. VTOP Coach
    6. Performance Insights
    7. Career Advisor
    """
    
    print_header("CLI-TOP GEMINI AI FEATURES")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    # Get VTOP data
    print("📊 Loading VTOP data...")
    vtop_data = get_vtop_data(use_cache=True)
    
    print(f"Student: {vtop_data.get('reg_no', 'N/A')}")
    print(f"CGPA: {vtop_data.get('cgpa', 'N/A')}")
    print("=" * 80)
    print()
    
    gemini_features = [
        ('smart_grade_predictor', 'Smart Grade Predictor'),
        ('study_optimizer', 'Study Optimizer'),
        ('semester_insights', 'Semester Insights'),
        ('study_guide', 'Personalized Study Guide'),
        ('vtop_coach', 'VTOP Coach & Roaster'),
        ('performance_insights', 'Performance Insights'),
        ('career_advisor', 'Career Advisor'),
    ]
    
    feature_count = 0
    
    for idx, (feature_module, feature_name) in enumerate(gemini_features, 1):
        print_section(f"{idx}. {feature_name} (Gemini AI)")
        try:
            from live_data_wrapper import run_feature_with_live_data
            
            result = run_feature_with_live_data(feature_module, use_cache=True)
            
            if result is not None or result != False:
                feature_count += 1
            print()
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            print()
    
    # Summary
    print("=" * 80)
    print_header("SUMMARY")
    print(f"✅ Features executed: {feature_count}/{len(gemini_features)}")
    print()
    print("� All Gemini features use smart caching")
    print("=" * 80)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Run CLI-TOP AI Features')
    parser.add_argument('--gemini', action='store_true', 
                       help='Run Gemini-powered features instead of offline features')
    parser.add_argument('--all', action='store_true',
                       help='Run both offline and Gemini features')
    
    args = parser.parse_args()
    
    if args.all:
        print("🚀 Running ALL features (offline + Gemini)...")
        print()
        run_offline_features()
        print("\n\n")
        run_gemini_features()
    elif args.gemini:
        print("🚀 Running Gemini AI features...")
        print()
        run_gemini_features()
    else:
        print("🚀 Running offline AI features (no API required)...")
        print("   Use --gemini to run Gemini features instead")
        print("   Use --all to run both offline and Gemini features")
        print()
        run_offline_features()


if __name__ == "__main__":
    main()


