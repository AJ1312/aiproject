#!/usr/bin/env python3
"""
Better VTOP Backend Server
Flask API to execute CLI-TOP commands and return outputs
Uses stored credentials from cli-top-config.env
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import subprocess
import json
import os
import sys
from pathlib import Path
import tempfile
import re

app = Flask(__name__, static_folder='.')
CORS(app)

# Path to CLI-TOP binary and config
CLI_TOP_PATH = Path(__file__).parent.parent / 'cli-top'
CLI_TOP_CONFIG = Path(__file__).parent.parent / 'cli-top-config.env'

if not CLI_TOP_PATH.exists():
    print(f"⚠️  Warning: CLI-TOP binary not found at {CLI_TOP_PATH}")
    print("   Build it first: go build -o cli-top main.go")

if not CLI_TOP_CONFIG.exists():
    print(f"⚠️  Warning: Config file not found at {CLI_TOP_CONFIG}")
    print("   Run CLI-TOP first to generate credentials")

# Auto-login flag - set to True to use stored credentials
AUTO_LOGIN = True

# Store session credentials temporarily
sessions = {}

def run_subprocess_safe(cmd, **kwargs):
    """
    Run subprocess with safe defaults to prevent TTY suspension.
    Always uses DEVNULL for stdin unless explicitly overridden.
    """
    # Set safe defaults
    # If caller provided 'input', subprocess.run will internally create a stdin pipe.
    # Passing both 'stdin' and 'input' causes: "stdin and input arguments may not both be used".
    # So only set stdin=DEVNULL when 'input' is not present and caller didn't override stdin.
    if 'stdin' not in kwargs and 'input' not in kwargs:
        kwargs['stdin'] = subprocess.DEVNULL
    if 'capture_output' not in kwargs:
        kwargs['capture_output'] = True
    if 'text' not in kwargs:
        kwargs['text'] = True
    
    return subprocess.run(cmd, **kwargs)

# Auto-login flag - set to True to use stored credentials
AUTO_LOGIN = os.path.exists(CLI_TOP_CONFIG) and os.path.getsize(CLI_TOP_CONFIG) > 100

# Store session credentials temporarily
sessions = {}

def check_credentials():
    """Check if valid credentials exist"""
    if not CLI_TOP_CONFIG.exists():
        return False
    
    # Read config file and check if essential fields are populated
    try:
        with open(CLI_TOP_CONFIG, 'r') as f:
            content = f.read()
            # Check if REGNO and VTOP_USERNAME have values
            if 'REGNO=""' in content or 'VTOP_USERNAME=""' in content:
                return False
            if 'REGNO=' not in content or 'VTOP_USERNAME=' not in content:
                return False
            return True
    except:
        return False

def check_ai_context():
    """Check if AI context (current_semester_data.json) exists"""
    ai_path = Path(__file__).parent.parent / 'ai'
    data_file = ai_path / 'current_semester_data.json'
    return data_file.exists()


@app.route('/api/status', methods=['GET'])
def status():
    """Get system status - credentials and AI context"""
    creds_exist = check_credentials()
    ai_context_exists = check_ai_context()
    
    return jsonify({
        'credentials_exist': creds_exist,
        'ai_context_exists': ai_context_exists,
        'ready': creds_exist and ai_context_exists,
        'auto_login': AUTO_LOGIN
    })


@app.route('/api/setup-ai-context', methods=['POST'])
def setup_ai_context():
    """Generate AI context from VTOP data"""
    try:
        # First, export AI data using CLI-TOP
        if not check_credentials():
            return jsonify({'error': 'Credentials not configured. Please login first.'}), 401
        
        # Export all data to /tmp/all_data.txt
        cmd = [str(CLI_TOP_PATH), 'ai', 'export', '-o', '/tmp/all_data.txt']
        
        print(f"🔄 Exporting VTOP data...")
        result = run_subprocess_safe(
            cmd,
            timeout=120,
            cwd=str(CLI_TOP_PATH.parent)
        )
        
        if result.returncode != 0:
            return jsonify({
                'error': 'Failed to export VTOP data',
                'details': result.stderr
            }), 500
        
        # Parse the exported data
        ai_path = Path(__file__).parent.parent / 'ai'
        parse_script = ai_path / 'parse_current_semester.py'
        
        print(f"📊 Parsing current semester data...")
        result = run_subprocess_safe(
            ['python3', str(parse_script)],
            timeout=30,
            cwd=str(ai_path)
        )
        
        if result.returncode != 0:
            return jsonify({
                'error': 'Failed to parse semester data',
                'details': result.stderr
            }), 500
        
        # Check if file was created
        if not check_ai_context():
            return jsonify({'error': 'AI context file was not created'}), 500
        
        print(f"✅ AI context generated successfully!")
        
        return jsonify({
            'success': True,
            'message': 'AI context generated successfully',
            'output': result.stdout
        })
        
    except Exception as e:
        print(f"❌ AI context setup error: {str(e)}")
        return jsonify({'error': f'Setup error: {str(e)}'}), 500


@app.route('/')
def index():
    """Serve the main HTML file"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """Serve static files (CSS, JS)"""
    return send_from_directory('.', path)


@app.route('/api/login', methods=['POST'])
def login():
    """
    Login to VTOP and store credentials
    Request: {"username": "...", "password": "..."}
    """
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        # Create credentials file
        creds_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        creds_data = {
            'username': username,
            'password': password
        }
        json.dump(creds_data, creds_file)
        creds_file.close()
        
        # Test login with a simple command
        try:
            result = run_subprocess_safe(
                [str(CLI_TOP_PATH), '--creds', creds_file.name, 'profile'],
                timeout=30
            )
            
            if result.returncode == 0:
                # Success - store session
                session_id = os.urandom(16).hex()
                sessions[session_id] = creds_file.name
                
                return jsonify({
                    'success': True,
                    'session_id': session_id,
                    'message': 'Login successful!'
                })
            else:
                os.unlink(creds_file.name)
                return jsonify({
                    'error': 'Login failed. Check your credentials.',
                    'details': result.stderr
                }), 401
                
        except subprocess.TimeoutExpired:
            os.unlink(creds_file.name)
            return jsonify({'error': 'Login timeout. VTOP might be slow.'}), 408
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout and clear session"""
    data = request.json
    session_id = data.get('session_id')
    
    if session_id in sessions:
        creds_file = sessions[session_id]
        if os.path.exists(creds_file):
            os.unlink(creds_file)
        del sessions[session_id]
    
    return jsonify({'success': True})


@app.route('/api/execute', methods=['POST'])
def execute_command():
    """
    Execute a CLI-TOP command
    Request: {"session_id": "...", "command": "grades view", "args": [...]}
    If AUTO_LOGIN is True, session_id is optional and stored credentials are used
    """
    try:
        data = request.json
        session_id = data.get('session_id')
        command = data.get('command')
        args = data.get('args', [])
        semester = data.get('semester')  # Get semester choice from frontend
        
        # Build command - use stored config if AUTO_LOGIN is enabled
        if AUTO_LOGIN and CLI_TOP_CONFIG.exists():
            # Use the stored credentials from cli-top-config.env
            cmd = [str(CLI_TOP_PATH)]
        else:
            # Use session-based credentials
            if not session_id or session_id not in sessions:
                return jsonify({'error': 'Invalid or expired session'}), 401
            
            creds_file = sessions[session_id]
            cmd = [str(CLI_TOP_PATH), '--creds', creds_file]
        
        # Parse command
        if isinstance(command, str):
            cmd.extend(command.split())
        else:
            cmd.extend(command)
        
        if args:
            cmd.extend(args)
        
        print(f"📡 Executing command: {' '.join(cmd)}")
        if semester:
            print(f"   Semester choice: {semester}")
        
        # Commands that require semester selection
        interactive_commands = ['marks', 'grades', 'attendance', 'da', 'syllabus', 'exams', 'timetable']
        needs_semester = any(ic in cmd for ic in interactive_commands)
        
        # Execute
        if needs_semester and semester:
            # Use provided semester choice
            result = run_subprocess_safe(
                cmd,
                input=f"{semester}\n",
                timeout=60,
                cwd=str(CLI_TOP_PATH.parent)
            )
        elif needs_semester:
            # Default to latest semester if not provided
            result = run_subprocess_safe(
                cmd,
                input="5\n",
                timeout=60,
                cwd=str(CLI_TOP_PATH.parent)
            )
        else:
            result = run_subprocess_safe(
                cmd,
                timeout=60,
                cwd=str(CLI_TOP_PATH.parent)
            )
        
        # Parse output
        output = result.stdout
        error = result.stderr
        
        print(f"Exit code: {result.returncode}")
        print(f"Output length: {len(output)} chars")
        if error:
            print(f"⚠️ Stderr: {error[:200]}")
        
        # Try to detect if output is a table and format it
        formatted_output = format_cli_output(output)
        
        return jsonify({
            'success': result.returncode == 0,
            'output': formatted_output,
            'raw_output': output,
            'error': error if error else None,
            'exit_code': result.returncode
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Command timeout (60s)'}), 408
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': f'Execution error: {str(e)}'}), 500


@app.route('/api/ai-export', methods=['POST'])
def ai_export():
    """Export AI data"""
    try:
        data = request.json
        session_id = data.get('session_id')
        
        # Use stored credentials if AUTO_LOGIN is enabled
        if AUTO_LOGIN and CLI_TOP_CONFIG.exists():
            cmd = [str(CLI_TOP_PATH)]
        else:
            if not session_id or session_id not in sessions:
                return jsonify({'error': 'Invalid session'}), 401
            
            creds_file = sessions[session_id]
            cmd = [str(CLI_TOP_PATH), '--creds', creds_file]
        
        # Create temp file for export
        export_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        export_file.close()
        
        # Execute export
        cmd.extend(['ai', 'export', '-o', export_file.name])
        
        print(f"📤 Exporting AI data: {' '.join(cmd)}")
        
        result = run_subprocess_safe(
            cmd,
            timeout=120,
            cwd=str(CLI_TOP_PATH.parent)
        )
        
        if result.returncode == 0:
            # Read exported data
            with open(export_file.name, 'r') as f:
                ai_data = json.load(f)
            
            os.unlink(export_file.name)
            
            print(f"✅ AI data exported successfully")
            
            return jsonify({
                'success': True,
                'data': ai_data
            })
        else:
            os.unlink(export_file.name)
            print(f"❌ Export failed: {result.stderr}")
            return jsonify({
                'error': 'Export failed',
                'details': result.stderr
            }), 500
            
    except Exception as e:
        print(f"❌ Export error: {str(e)}")
        return jsonify({'error': f'Export error: {str(e)}'}), 500


@app.route('/api/ai-features', methods=['POST'])
def run_ai_features():
    """Run AI features using current_semester_data.json"""
    try:
        data = request.json
        feature = data.get('feature', 'all')
        
        # Use current semester data file directly
        ai_path = Path(__file__).parent.parent / 'ai'
        data_file = ai_path / 'current_semester_data.json'
        
        if not data_file.exists():
            return jsonify({'error': 'current_semester_data.json not found. Please run parse_current_semester.py'}), 404
        
        # Determine which feature to run
        if feature == 'all':
            script = ai_path / 'run_all_features.py'
            cmd = ['python3', str(script), str(data_file)]
        else:
            # Map feature names to script names
            feature_map = {
                'attendance_calculator': 'attendance_calculator.py',
                'grade_predictor': 'grade_predictor.py',
                'cgpa_analyzer': 'cgpa_analyzer.py',
                'attendance_recovery': 'attendance_recovery.py',
                'exam_readiness': 'exam_readiness.py',
                'study_allocator': 'study_allocator.py',
                'performance_analyzer': 'performance_analyzer.py',
                'target_planner': 'target_planner.py',
                'weakness_identifier': 'weakness_identifier.py'
            }
            
            script_name = feature_map.get(feature)
            if not script_name:
                return jsonify({'error': f'Unknown feature: {feature}'}), 404
            
            script = ai_path / 'features' / script_name
            cmd = ['python3', str(script), str(data_file)]
        
        if not script.exists():
            return jsonify({'error': f'Feature not found: {script}'}), 404
        
        # Run feature
        print(f"🤖 Running AI feature: {feature}")
        print(f"Script path: {script}")
        print(f"Data file: {data_file}")
        print(f"Running command: {' '.join(cmd)}")
        
        result = run_subprocess_safe(
            cmd,
            timeout=60,
            cwd=str(ai_path)
        )
        
        print(f"Exit code: {result.returncode}")
        print(f"Output length: {len(result.stdout)} chars")
        if result.stderr:
            print(f"⚠️ Stderr: {result.stderr[:200]}")
        
        # Format AI output
        ai_output = result.stdout if result.stdout else result.stderr
        formatted_ai_output = format_cli_output(ai_output) if ai_output else {'type': 'text', 'content': 'No output'}
        
        return jsonify({
            'success': result.returncode == 0,
            'output': formatted_ai_output,
            'raw_output': result.stdout,
            'error': result.stderr if result.stderr else None
        })
        
    except Exception as e:
        return jsonify({'error': f'AI feature error: {str(e)}'}), 500


@app.route('/api/gemini-features', methods=['POST'])
def run_gemini_features():
    """Run Gemini AI features using current_semester_data.json"""
    try:
        data = request.json
        feature = data.get('feature', 'chatbot')
        subject_number = data.get('subject_number')  # For study guide
        
        # Use current semester data file directly
        ai_path = Path(__file__).parent.parent / 'ai'
        data_file = ai_path / 'current_semester_data.json'
        
        if not data_file.exists():
            return jsonify({'error': 'current_semester_data.json not found. Please run parse_current_semester.py'}), 404
        
        # Determine which Gemini feature to run
        gemini_path = ai_path / 'gemini_features'
        
        # Map features to scripts (no extra args needed - they use current_semester_data.json by default)
        feature_map = {
            'chatbot': (ai_path / 'chatbot.py', []),
            'insights': (gemini_path / 'performance_insights.py', [str(data_file)]),
            'career': (gemini_path / 'career_advisor.py', [str(data_file)]),
            'study-plan': (gemini_path / 'study_optimizer.py', [str(data_file)]),
            'study-guide': (gemini_path / 'study_guide.py', [str(data_file)]),
            'voice': (gemini_path / 'voice_assistant.py', []),
            'roast': (gemini_path / 'vtop_coach.py', [str(data_file), 'roast'])
        }
        
        if feature not in feature_map:
            return jsonify({'error': f'Unknown Gemini feature: {feature}'}), 404
        
        script, extra_args = feature_map[feature]
        
        if not script.exists():
            return jsonify({'error': f'Gemini feature not found: {script}'}), 404
        
        # Build command
        cmd = ['python3', str(script)] + extra_args
        
        # Add subject number for study guide
        if feature == 'study-guide' and subject_number:
            cmd.append(str(subject_number))
        
        # Run Gemini feature
        print(f"✨ Running Gemini feature: {feature}")
        print(f"Script path: {script}")
        print(f"Command: {' '.join(cmd)}")
        
        result = run_subprocess_safe(
            cmd,
            timeout=90,  # Gemini might take longer
            cwd=str(script.parent)
        )
        
        print(f"Exit code: {result.returncode}")
        print(f"Output length: {len(result.stdout)} chars")
        if result.stderr:
            print(f"⚠️ Stderr: {result.stderr[:500]}")
        
        # Format Gemini output
        gemini_output = result.stdout if result.stdout else result.stderr
        formatted_output = format_cli_output(gemini_output) if gemini_output else {'type': 'text', 'content': 'No output'}
        
        return jsonify({
            'success': result.returncode == 0,
            'output': formatted_output,
            'raw_output': result.stdout,
            'error': result.stderr if result.stderr else None
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Gemini feature timeout (90s) - API might be slow'}), 408
    except Exception as e:
        return jsonify({'error': f'Gemini feature error: {str(e)}'}), 500


@app.route('/api/get-subjects', methods=['GET'])
def get_subjects():
    """Get list of subjects for study guide selection"""
    try:
        ai_path = Path(__file__).parent.parent / 'ai'
        gemini_path = ai_path / 'gemini_features'
        data_file = ai_path / 'current_semester_data.json'
        script = gemini_path / 'study_guide.py'
        
        if not data_file.exists():
            return jsonify({'error': 'current_semester_data.json not found'}), 404
        
        # Run study guide with --list flag
        cmd = ['python3', str(script), str(data_file), '--list']
        
        result = run_subprocess_safe(
            cmd,
            timeout=10,
            cwd=str(script.parent)
        )
        
        if result.returncode != 0:
            return jsonify({'error': 'Failed to get subjects list', 'stderr': result.stderr}), 500
        
        # Parse JSON output (skip config messages before the JSON)
        output = result.stdout
        # Find the first '[' to start of JSON array
        json_start = output.find('[')
        if json_start == -1:
            return jsonify({'error': 'No JSON found in output'}), 500
        
        json_str = output[json_start:]
        subjects = json.loads(json_str)
        return jsonify({'subjects': subjects})
        
    except Exception as e:
        return jsonify({'error': f'Error getting subjects: {str(e)}'}), 500


@app.route('/api/smart-command', methods=['POST'])
def smart_command():
    """Execute smart context-aware multi-tool commands"""
    try:
        data = request.json
        ai_data = data.get('ai_data')
        smart_type = data.get('smart_type')
        
        if not ai_data or not smart_type:
            return jsonify({'error': 'AI data and smart_type required'}), 400
        
        # Save data to temp file
        data_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        json.dump(ai_data, data_file)
        data_file.close()
        
        ai_path = Path(__file__).parent.parent / 'ai'
        output_parts = []
        
        try:
            if smart_type == 'attendance_advice':
                # Run attendance + attendance calculator
                output_parts.append("🔄 Checking Attendance...\n")
                
                # Get attendance from CLI
                cmd = [str(CLI_TOP_PATH), 'attendance', 'calculator']
                result = run_subprocess_safe(cmd, timeout=30)
                if result.returncode == 0:
                    output_parts.append(result.stdout + "\n")
                
                # Run AI attendance calculator
                script = ai_path / 'features' / 'attendance_calculator.py'
                result = run_subprocess_safe(
                    ['python3', str(script), data_file.name],
                    timeout=30, cwd=str(ai_path)
                )
                if result.returncode == 0:
                    output_parts.append("\n📊 AI Analysis:\n" + result.stdout)
                
            elif smart_type == 'performance_overview':
                # Run CGPA + performance analyzer + insights
                output_parts.append("🔄 Analyzing Performance...\n")
                
                # Get CGPA
                cmd = [str(CLI_TOP_PATH), 'cgpa', 'view']
                result = run_subprocess_safe(cmd, timeout=30)
                if result.returncode == 0:
                    output_parts.append(result.stdout + "\n")
                
                # Run performance analyzer
                script = ai_path / 'features' / 'performance_analyzer.py'
                result = run_subprocess_safe(
                    ['python3', str(script), data_file.name],
                    timeout=30, cwd=str(ai_path)
                )
                if result.returncode == 0:
                    output_parts.append("\n📊 Performance Trends:\n" + result.stdout)
                
            elif smart_type == 'focus_advisor':
                # Run weakness identifier
                output_parts.append("🔄 Identifying Focus Areas...\n")
                
                script = ai_path / 'features' / 'weakness_identifier.py'
                result = run_subprocess_safe(
                    ['python3', str(script), data_file.name],
                    timeout=30, cwd=str(ai_path)
                )
                if result.returncode == 0:
                    output_parts.append(result.stdout)
                
            elif smart_type == 'exam_prediction':
                # Run exam readiness + grade predictor
                output_parts.append("🔄 Predicting Exam Performance...\n")
                
                # Exam readiness
                script = ai_path / 'features' / 'exam_readiness.py'
                result = run_subprocess_safe(
                    ['python3', str(script), data_file.name],
                    timeout=30, cwd=str(ai_path)
                )
                if result.returncode == 0:
                    output_parts.append(result.stdout + "\n")
                
                # Grade predictor
                script = ai_path / 'features' / 'grade_predictor.py'
                result = run_subprocess_safe(
                    ['python3', str(script), data_file.name],
                    timeout=30, cwd=str(ai_path)
                )
                if result.returncode == 0:
                    output_parts.append("\n🎯 Grade Predictions:\n" + result.stdout)
            
            os.unlink(data_file.name)
            
            combined_output = '\n'.join(output_parts)
            
            return jsonify({
                'success': True,
                'output': {'type': 'text', 'content': combined_output},
                'raw_output': combined_output
            })
            
        except Exception as e:
            os.unlink(data_file.name)
            raise e
            
    except Exception as e:
        return jsonify({'error': f'Smart command error: {str(e)}'}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """Interactive chat with AI chatbot using current_semester_data.json"""
    try:
        data = request.json
        message = data.get('message')
        
        if not message:
            return jsonify({'error': 'Message required'}), 400
        
        # Use current semester data file directly
        ai_path = Path(__file__).parent.parent / 'ai'
        data_file = ai_path / 'current_semester_data.json'
        
        if not data_file.exists():
            return jsonify({'error': 'current_semester_data.json not found'}), 404
        
        # Run chatbot with single question
        script = ai_path / 'chatbot.py'
        
        if not script.exists():
            return jsonify({'error': 'Chatbot not found'}), 404
        
        # Use subprocess with message as input
        print(f"💬 Chat query: {message}")
        
        # Run chatbot in interactive mode, send message via stdin
        result = run_subprocess_safe(
            ['python3', str(script)],
            input=f"{message}\nexit\n",
            timeout=45,
            cwd=str(ai_path)
        )
        
        # Extract response
        response = result.stdout.strip() if result.stdout else result.stderr.strip()
        
        # Clean up the response - extract only the assistant's response
        lines = response.split('\n')
        cleaned_lines = []
        skip_next = False
        in_response = False
        
        for line in lines:
            # Skip config/header lines
            if any(x in line for x in ['✅ AI Configuration', 'Model:', 'API Key', 'Output Directory', 
                                       '🤖 CLI-TOP', '=' * 10, 'Student:', 'Semester:', 'CGPA:',
                                       'have your complete', 'Ask me anything', 'Type \'quit\'',
                                       'You:', 'WARNING:', 'E0000']):
                continue
            
            # Look for Assistant: marker
            if '🤖 Assistant:' in line or 'Assistant:' in line:
                in_response = True
                # Extract text after "Assistant:"
                parts = line.split('Assistant:', 1)
                if len(parts) > 1:
                    cleaned_lines.append(parts[1].strip())
                continue
            
            # Capture lines after Assistant marker
            if in_response and line.strip():
                # Stop at next "You:" or exit indicators
                if 'You:' in line or '👋' in line or 'Goodbye' in line:
                    break
                cleaned_lines.append(line.strip())
        
        clean_response = '\n'.join(cleaned_lines).strip()
        
        # If no clean response found, try to get last meaningful output
        if not clean_response:
            # Get last non-empty lines that aren't system messages
            for line in reversed(lines):
                if line.strip() and not any(x in line for x in ['You:', 'WARNING:', 'E0000', '=' * 10]):
                    clean_response = line.strip()
                    break
        
        if not clean_response:
            clean_response = "I apologize, but I encountered an issue processing your question. Please try again."
        
        return jsonify({
            'success': True,
            'response': clean_response,
            'raw': response
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Chat timeout - AI is taking too long'}), 408
    except Exception as e:
        print(f"❌ Chat error: {str(e)}")
        return jsonify({'error': f'Chat error: {str(e)}'}), 500


@app.route('/api/voice-chat', methods=['POST'])
def voice_chat():
    """Voice assistant chat - uses chatbot with full VTOP context like terminal"""
    try:
        data = request.json
        message = data.get('message')
        
        if not message:
            return jsonify({'error': 'Message required'}), 400
        
        # Use current semester data file directly - same as terminal
        ai_path = Path(__file__).parent.parent / 'ai'
        data_file = ai_path / 'current_semester_data.json'
        
        if not data_file.exists():
            return jsonify({'error': 'current_semester_data.json not found. Please run parse_current_semester.py'}), 404
        
        # Load data
        with open(data_file, 'r') as f:
            vtop_data = json.load(f)
        
        # Enhance with raw text sections from all_data.txt (same as terminal chatbot)
        all_data_file = Path('/tmp/all_data.txt')
        if all_data_file.exists():
            try:
                with open(all_data_file, 'r') as f:
                    raw_text = f.read()
                
                # Extract sections
                sections = {
                    'raw_profile': ('PROFILE INFORMATION', 'MARKS'),
                    'raw_hostel': ('HOSTEL DETAILS', 'CGPA'),
                    'raw_cgpa': ('CGPA', 'LIBRARY'),
                    'raw_library': ('LIBRARY DUES', 'LEAVE'),
                    'raw_leave': ('LEAVE STATUS', 'MARKS')
                }
                
                for key, (start_marker, end_marker) in sections.items():
                    if start_marker in raw_text and end_marker in raw_text:
                        start_idx = raw_text.find(start_marker)
                        end_idx = raw_text.find(end_marker, start_idx)
                        vtop_data[key] = raw_text[start_idx:end_idx].strip()
            except Exception as e:
                print(f"⚠️  Could not load raw data: {e}")
        
        # Initialize chatbot context (same as terminal)
        sys.path.insert(0, str(ai_path))
        
        try:
            import google.generativeai as genai
            from config import GOOGLE_API_KEY, GEMINI_MODEL
            
            if not GOOGLE_API_KEY:
                return jsonify({'error': 'GOOGLE_API_KEY not configured'}), 500
            
            genai.configure(api_key=GOOGLE_API_KEY)
            model = genai.GenerativeModel(GEMINI_MODEL)
            
            # Build context exactly like VTOPChatbot._build_context() in chatbot.py
            reg_no = vtop_data.get('reg_no', 'N/A')
            student_name = vtop_data.get('name', 'Student')
            email = vtop_data.get('email', 'Not available')
            program = vtop_data.get('program', 'Not available')
            school = vtop_data.get('school', 'Not available')
            cgpa = vtop_data.get('cgpa', 0.0)
            credits = vtop_data.get('credits_completed', 'N/A')
            semester = vtop_data.get('semester', 'Current Semester')
            marks = vtop_data.get('marks', [])
            attendance = vtop_data.get('attendance', [])
            exams = vtop_data.get('exams', [])
            
            avg_attendance = sum(a.get('attendance_percentage', 0) for a in attendance) / len(attendance) if attendance else 0
            
            # Build context string
            context = f"""
You are {student_name}'s personal AI academic assistant with complete access to their VTOP data.

STUDENT PROFILE:
- Name: {student_name}
- Registration Number: {reg_no}
- Program: {program}
- Email: {email}
- School: {school}
- Current Semester: {semester}
- Overall CGPA: {cgpa}/10
- Credits Completed: {credits}/160

CURRENT SEMESTER ({semester}):
- Total Courses: {len(marks)}
- Average Attendance: {avg_attendance:.1f}%
- Active Courses with Marks: {len(marks)}

CURRENT SEMESTER MARKS:
"""
            for course in marks:
                course_name = course.get('course_name', 'Unknown')
                course_code = course.get('course_code', 'N/A')
                context += f"\n{course_name} ({course_code}):\n"
                
                components = course.get('components', [])
                if components:
                    for comp in components:
                        title = comp.get('title', 'Unknown')
                        scored = comp.get('weightage_mark', 0)
                        max_marks = comp.get('weightage', 0)
                        context += f"  • {title}: {scored}/{max_marks}\n"
            
            context += "\n\nATTENDANCE BREAKDOWN:\n"
            for att in attendance:
                course = att.get('course_name', att.get('course_code', 'Unknown'))
                percentage = att.get('attendance_percentage', 0)
                attended = att.get('attended_classes', 0)
                total = att.get('total_classes', 0)
                status = "✅ Safe" if percentage >= 85 else "⚠️ Monitor" if percentage >= 75 else "🚨 Critical"
                context += f"  • {course}: {percentage}% ({attended}/{total} classes) {status}\n"
            
            context += """

YOUR ROLE AS PERSONAL ACADEMIC ASSISTANT:
1. Analyze the student's academic performance with personal insights
2. Give honest opinions about their strengths and weaknesses
3. Provide encouragement when they're doing well
4. Offer constructive feedback on areas needing improvement
5. Suggest specific actions based on the data
6. Help with attendance planning and grade predictions
7. Identify trends and patterns in performance
8. Motivate and guide towards better academic outcomes
9. For voice interactions, keep responses concise (under 30 seconds when spoken)
10. Be conversational, friendly, and supportive like a mentor

Be friendly, data-driven, and genuinely invested in the student's academic journey.
"""
            
            # Generate response
            full_prompt = context + f"\n\nUser: {message}\n\nProvide a helpful, concise response:"
            
            print(f"🎙️  Voice query: {message}")
            response = model.generate_content(full_prompt)
            response_text = response.text
            
            return jsonify({
                'success': True,
                'response': response_text
            })
            
        except Exception as e:
            print(f"❌ Voice chat error: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Voice chat error: {str(e)}'}), 500
        
    except Exception as e:
        print(f"❌ Voice chat initialization error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Voice chat error: {str(e)}'}), 500


def format_cli_output(output):
    """Format CLI output for better display"""
    # Check if it's a table (contains borders like ├──, │, etc.)
    if '│' in output or '├' in output or '┌' in output:
        return {
            'type': 'table',
            'content': output
        }
    
    # Check if it's JSON
    try:
        json_data = json.loads(output)
        return {
            'type': 'json',
            'content': json_data
        }
    except:
        pass
    
    # Regular text
    return {
        'type': 'text',
        'content': output
    }


if __name__ == '__main__':
    print("="*60)
    print("🚀 Better VTOP Backend Server")
    print("="*60)
    print(f"CLI-TOP Path: {CLI_TOP_PATH}")
    print(f"Exists: {CLI_TOP_PATH.exists()}")
    print()
    print("Server starting on http://localhost:5555")
    print("Open http://localhost:5555 in your browser")
    print("="*60)
    print()
    
    # Run without debug mode and reloader to prevent TTY suspension
    # when running in background with nohup
    app.run(debug=False, port=5555, host='0.0.0.0', use_reloader=False)
