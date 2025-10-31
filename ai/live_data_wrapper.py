"""
Live Data Wrapper for AI Features
Uses the smart data manager for intelligent caching and rate limiting
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from vtop_data_manager import get_vtop_data


def run_feature_with_live_data(feature_name, use_cache=True):
    """
    Run any AI feature with VTOP data
    
    Args:
        feature_name: Name of the feature to run
        use_cache: Whether to use cached data (default: True for rate limiting)
    """
    print(f"🚀 Running {feature_name}...")
    
    # Get data (smart caching and rate limiting handled automatically)
    data = get_vtop_data(use_cache=use_cache)
    
    # Map feature names to actual features
    feature_map = {
        'smart_grade_predictor': 'features.smart_grade_predictor',
        'study_optimizer': 'features.study_optimizer',
        'semester_insights': 'features.semester_insights',
        'study_guide': 'features.study_guide',
        'vtop_coach': 'features.vtop_coach',
        'performance_insights': 'features.performance_insights',
        'career_advisor': 'features.career_advisor',
        'academic_performance_ml': 'features.academic_performance_ml',
    }
    
    if feature_name in feature_map:
        module_name = feature_map[feature_name]
        
        try:
            # Dynamic import
            import importlib
            module = importlib.import_module(module_name)
            
            if hasattr(module, 'main'):
                return module.main()
            else:
                print(f"❌ Feature {feature_name} doesn't have a main() function")
                return None
        except Exception as e:
            print(f"❌ Error running {feature_name}: {str(e)}")
            return None
    else:
        print(f"❌ Unknown feature: {feature_name}")
        print(f"Available features: {', '.join(feature_map.keys())}")
        return None


if __name__ == '__main__':
    if len(sys.argv) > 1:
        feature = sys.argv[1]
        run_feature_with_live_data(feature)
    else:
        print("Usage: python live_data_wrapper.py <feature_name>")
        print("\nAvailable AI Features:")
        print("  • smart_grade_predictor - Gemini-powered grade prediction")
        print("  • study_optimizer - AI study plan optimization")
        print("  • semester_insights - Semester performance insights")
        print("  • study_guide - Personalized study guides")
        print("  • vtop_coach - AI performance coach")
        print("  • performance_insights - Performance analysis")
        print("  • career_advisor - Career guidance")
        print("  • academic_performance_ml - ML-based performance analysis")
