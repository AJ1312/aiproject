#!/usr/bin/env python3
"""
All AI Features Runner
Executes all Gemini-powered AI features with smart data fetching
"""

import sys
from datetime import datetime
from pathlib import Path

# Add features directory to path
sys.path.insert(0, str(Path(__file__).parent))

from vtop_data_manager import get_vtop_data
from utils.formatters import print_header, print_section


def run_all_ai_features():
    """
    Execute all Gemini-powered AI features sequentially.
    
    AI Features (Gemini-powered):
    1. Smart Grade Predictor - Multi-semester AI analysis
    2. Study Optimizer - AI-powered study plans  
    3. Semester Insights - Comprehensive semester analysis
    4. Study Guide - Course-specific study guides
    5. VTOP Coach - Performance coaching and roasting
    6. Performance Insights - Deep performance analysis
    7. Career Advisor - Career guidance based on performance
    8. Academic Performance ML - ML-based clustering and predictions
    """
    
    print_header("CLI-TOP AI FEATURES - COMPREHENSIVE REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    # Get VTOP data (uses smart caching and rate limiting)
    print("📊 Loading VTOP data...")
    vtop_data = get_vtop_data(use_cache=True)
    
    print(f"Student: {vtop_data.get('reg_no', 'N/A')}")
    print(f"Semester: {vtop_data.get('semester', 'N/A')}")
    print(f"CGPA: {vtop_data.get('cgpa', 'N/A')}")
    print("=" * 80)
    print()
    
    feature_count = 0
    features = [
        ('smart_grade_predictor', 'Smart Grade Predictor (Gemini AI)'),
        ('study_optimizer', 'Study Optimizer (Gemini AI)'),
        ('semester_insights', 'Semester Insights (Gemini AI)'),
        ('study_guide', 'Personalized Study Guide (Gemini AI)'),
        ('vtop_coach', 'VTOP Coach & Roaster (Gemini AI)'),
        ('performance_insights', 'Performance Insights (Gemini AI)'),
        ('career_advisor', 'Career Advisor (Gemini AI)'),
        ('academic_performance_ml', 'Academic Performance ML (scikit-learn)'),
    ]
    
    for idx, (feature_module, feature_name) in enumerate(features, 1):
        print_section(f"{idx}. {feature_name}")
        try:
            # Dynamic import and run
            from live_data_wrapper import run_feature_with_live_data
            
            result = run_feature_with_live_data(feature_module, use_cache=True)
            
            if result is not None or result != False:
                print(f"  ✅ {feature_name} completed")
                feature_count += 1
            else:
                print(f"  ⚠️  {feature_name} returned no results")
            print()
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            print()
    
    # Summary
    print("=" * 80)
    print_header("SUMMARY")
    print(f"✅ Features executed: {feature_count}/{len(features)}")
    print(f"📊 Total courses: {len(vtop_data.get('marks', []))}")
    print()
    print("💡 7 Gemini-powered features + 1 ML feature")
    print("🔒 Smart caching prevents VTOP logout")
    print("=" * 80)


def main():
    """Main entry point."""
    print("=" * 80)
    print("CLI-TOP AI Features Runner")
    print("=" * 80)
    print()
    print("🚀 Running all AI features...")
    print("⚡ Using smart data caching to prevent logout")
    print()
    
    run_all_ai_features()


if __name__ == "__main__":
    main()

