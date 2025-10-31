"""
Live Data Wrapper for AI Features
Ensures AI features always use fresh VTOP data instead of cached JSON
"""

import subprocess
import tempfile
import json
from pathlib import Path
import sys


def fetch_live_data():
    """Fetch fresh VTOP data and return as dict"""
    cli_top_path = Path(__file__).parent.parent / 'cli-top'
    
    # Export to temp file
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
    temp_file.close()
    
    try:
        # Export all data
        cmd = [str(cli_top_path), 'ai', 'export', '-o', temp_file.name]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            raise Exception(f"Failed to export data: {result.stderr}")
        
        # Parse
        parse_script = Path(__file__).parent / 'parse_current_semester.py'
        sys.path.insert(0, str(Path(__file__).parent))
        
        from parse_current_semester import parse_all_data_file
        
        return parse_all_data_file(temp_file.name)
        
    finally:
        Path(temp_file.name).unlink(missing_ok=True)


def run_feature_with_live_data(feature_name):
    """Run any AI feature with fresh live data"""
    print(f"🔄 Fetching live VTOP data for {feature_name}...")
    
    data = fetch_live_data()
    
    print(f"✅ Data fetched! Running {feature_name}...\n")
    
    # Import and run the feature
    if feature_name == 'grade_predictor':
        from features.grade_predictor import run_grade_predictor
        return run_grade_predictor(data)
    
    elif feature_name == 'attendance_calculator':
        from features.attendance_calculator import main
        # Temporarily save data
        temp_json = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(data, temp_json)
        temp_json.close()
        try:
            result = main(temp_json.name)
            return result
        finally:
            Path(temp_json.name).unlink(missing_ok=True)
    
    elif feature_name == 'cgpa_analyzer':
        from features.cgpa_analyzer import main
        temp_json = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(data, temp_json)
        temp_json.close()
        try:
            return main(temp_json.name)
        finally:
            Path(temp_json.name).unlink(missing_ok=True)
    
    elif feature_name == 'exam_readiness':
        from features.exam_readiness import main
        temp_json = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(data, temp_json)
        temp_json.close()
        try:
            return main(temp_json.name)
        finally:
            Path(temp_json.name).unlink(missing_ok=True)
    
    else:
        # Generic handler
        feature_map = {
            'attendance_recovery': 'features.attendance_recovery',
            'study_allocator': 'features.study_allocator',
            'performance_analyzer': 'features.performance_analyzer',
            'target_planner': 'features.target_planner',
            'weakness_identifier': 'features.weakness_identifier'
        }
        
        if feature_name in feature_map:
            module_name = feature_map[feature_name]
            temp_json = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
            json.dump(data, temp_json)
            temp_json.close()
            
            try:
                # Dynamic import
                import importlib
                module = importlib.import_module(module_name)
                if hasattr(module, 'main'):
                    return module.main(temp_json.name)
                else:
                    print(f"Feature {feature_name} doesn't have a main() function")
                    return None
            finally:
                Path(temp_json.name).unlink(missing_ok=True)
    
    return None


if __name__ == '__main__':
    if len(sys.argv) > 1:
        feature = sys.argv[1]
        run_feature_with_live_data(feature)
    else:
        print("Usage: python live_data_wrapper.py <feature_name>")
        print("Features: grade_predictor, attendance_calculator, cgpa_analyzer, etc.")
