/** Better VTOP Frontend - Clean Implementation */

const API_URL = 'http://localhost:5555/api';
let sessionId = 'auto-' + Date.now();
let systemReady = false;

// Elements
const output = document.getElementById('output');
const outputTitle = document.getElementById('outputTitle');
const outputBody = document.getElementById('outputBody');
const setupWizard = document.getElementById('setupWizard');
const sessionIndicator = document.getElementById('sessionIndicator');
const sessionStatus = document.getElementById('sessionStatus');

// Check system status on load
async function checkSystemStatus() {
    try {
        const res = await fetch(`${API_URL}/status`);
        const data = await res.json();
        
        systemReady = data.ready;
        
        if (!data.credentials_exist) {
            // Show setup wizard
            sessionStatus.textContent = 'Setup Required';
            sessionIndicator.className = 'session-indicator';
            showSetupWizard();
        } else if (!data.ai_context_exists) {
            // Credentials exist but AI context missing
            sessionStatus.textContent = 'AI Setup Needed';
            sessionIndicator.className = 'session-indicator';
            showAISetupStep();
        } else {
            // All good!
            sessionStatus.textContent = 'Ready ✓';
            sessionIndicator.className = 'session-indicator logged-in';
            systemReady = true;
        }
    } catch (err) {
        console.error('Status check failed:', err);
        sessionStatus.textContent = 'Server Error';
        sessionIndicator.className = 'session-indicator';
    }
}

// Show setup wizard
function showSetupWizard() {
    setupWizard.style.display = 'flex';
    document.getElementById('setupStep1').style.display = 'block';
    document.getElementById('setupStep2').style.display = 'none';
    document.getElementById('setupStep3').style.display = 'none';
}

// Show AI setup step (when creds exist but AI context missing)
function showAISetupStep() {
    setupWizard.style.display = 'flex';
    document.getElementById('setupStep1').style.display = 'none';
    document.getElementById('setupStep2').style.display = 'block';
    document.getElementById('setupStep3').style.display = 'none';
    
    // Auto-start AI context generation
    generateAIContext();
}

// Handle login in setup wizard
async function setupLogin() {
    const username = document.getElementById('setupUsername').value.trim();
    const password = document.getElementById('setupPassword').value.trim();
    const errorEl = document.getElementById('setupError');
    
    if (!username || !password) {
        errorEl.textContent = 'Please enter username and password';
        errorEl.style.display = 'block';
        return;
    }
    
    errorEl.style.display = 'none';
    
    try {
        // Show loading in step 1
        document.getElementById('setupStep1').innerHTML = '<div class="loading"><div class="spinner"></div><p>Logging in...</p></div>';
        
        const res = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await res.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Login failed');
        }
        
        sessionId = data.session_id;
        
        // Move to step 2 - AI context generation
        document.getElementById('setupStep1').style.display = 'none';
        document.getElementById('setupStep2').style.display = 'block';
        
        await generateAIContext();
        
    } catch (err) {
        // Show error in step 1
        document.getElementById('setupStep1').innerHTML = `
            <h3>❌ Login Failed</h3>
            <p style="color: red;">${err.message}</p>
            <button onclick="location.reload()" class="btn-exec" style="width: 100%; margin-top: 20px;">
                Try Again
            </button>
        `;
    }
}

// Generate AI context
async function generateAIContext() {
    try {
        const res = await fetch(`${API_URL}/setup-ai-context`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({})
        });
        
        const data = await res.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Failed to generate AI context');
        }
        
        // Show success step
        document.getElementById('setupStep2').style.display = 'none';
        document.getElementById('setupStep3').style.display = 'block';
        
        systemReady = true;
        sessionStatus.textContent = 'Ready ✓';
        sessionIndicator.className = 'session-indicator logged-in';
        
    } catch (err) {
        // Show error in step 2
        document.getElementById('setupStep2').innerHTML = `
            <h3>❌ Setup Failed</h3>
            <p style="color: red;">${err.message}</p>
            <p style="margin-top: 20px;">You can try:</p>
            <ol style="text-align: left; margin: 20px;">
                <li>Running setup.sh from the terminal</li>
                <li>Checking your internet connection</li>
                <li>Verifying VTOP is accessible</li>
            </ol>
            <button onclick="location.reload()" class="btn-exec" style="width: 100%; margin-top: 20px;">
                Try Again
            </button>
        `;
    }
}

// Close setup wizard
function closeSetup() {
    setupWizard.style.display = 'none';
}

// Init
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Better VTOP Loaded');
    
    // Check system status first
    checkSystemStatus();
    
    // Attach handlers
    document.querySelectorAll('.card').forEach(card => {
        const btn = card.querySelector('.btn-exec');
        if (btn) {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                handleClick(card);
            });
        }
    });
    
    console.log('✅ Ready');
});

// Handle card click
async function handleClick(card) {
    // Check if system is ready
    if (!systemReady) {
        alert('Please complete setup first!');
        showSetupWizard();
        return;
    }
    
    const type = card.dataset.type;
    const cmd = card.dataset.cmd;
    const feature = card.dataset.feature;
    const mode = card.dataset.mode;
    const title = card.querySelector('h3').textContent;
    
    console.log('▶', type, feature || cmd);
    
    showOutput(title);
    
    try {
        if (type === 'vtop') {
            await runVTOP(cmd);
        } else if (type === 'ai') {
            await runAI(feature);
        } else if (type === 'gemini') {
            await runGemini(feature, mode);
        }
    } catch (err) {
        showError(err.message);
    }
}

// Run VTOP
async function runVTOP(cmd) {
    // Check if this command needs semester selection
    const needsSemester = ['marks', 'grades', 'attendance', 'da', 'syllabus', 'exams', 'timetable'].includes(cmd);
    
    let semesterChoice = null;
    if (needsSemester) {
        semesterChoice = await showSemesterSelector();
        if (semesterChoice === null) return; // User cancelled
    }
    
    const res = await fetch(`${API_URL}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            session_id: sessionId, 
            command: cmd,
            semester: semesterChoice
        })
    });
    
    const data = await res.json();
    if (data.success) displayOutput(data.output);
    else throw new Error(data.error || 'Failed');
}

// Run AI
async function runAI(feature) {
    // Run directly - no export needed, uses current_semester_data.json
    const res = await fetch(`${API_URL}/ai-features`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feature })
    });
    
    const data = await res.json();
    if (data.success) displayOutput(data.output);
    else throw new Error(data.error || 'AI failed');
}

// Run Gemini
async function runGemini(feature, mode) {
    // Special handling for chatbot - open interactive chat
    if (feature === 'chatbot') {
        showChatInterface();
        return;
    }
    
    // Special handling for voice assistant - show instructions
    if (feature === 'voice') {
        showVoiceInstructions();
        return;
    }
    
    // Special handling for study guide - show subject selection
    if (feature === 'study-guide') {
        await showSubjectSelection();
        return;
    }
    
    // Run directly - no export needed, uses current_semester_data.json
    const res = await fetch(`${API_URL}/gemini-features`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ feature })
    });
    
    const data = await res.json();
    if (data.success) displayOutput(data.output);
    else throw new Error(data.error || 'Gemini failed');
}

// Show output
function showOutput(title) {
    outputTitle.textContent = title;
    outputBody.className = 'panel-body';
    outputBody.innerHTML = '<div class="loading"><div class="spinner"></div><p>EXECUTING...</p></div>';
    output.classList.add('active');
}

// Display
function displayOutput(data) {
    outputBody.className = 'panel-body';
    let content = '';
    
    if (typeof data === 'string') {
        content = data;
    } else if (data && typeof data === 'object') {
        content = data.content || JSON.stringify(data, null, 2);
    } else {
        content = String(data);
    }
    
    outputBody.innerHTML = `<pre>${escape(content)}</pre>`;
}

// Error
function showError(msg) {
    outputBody.className = 'panel-body error';
    outputBody.innerHTML = `<div style="padding:2rem;text-align:center;"><h3 style="margin-bottom:1rem;">❌ ERROR</h3><pre>${escape(msg)}</pre></div>`;
}

// Close
function closeOutput() {
    output.classList.remove('active');
}

// Escape
function escape(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Convert markdown-style bold (**text**) to HTML
function formatMarkdown(text) {
    // Escape HTML first
    const escaped = escape(text);
    // Convert **text** to <strong>text</strong>
    return escaped.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
}

// Click outside to close
output.addEventListener('click', (e) => {
    if (e.target === output) closeOutput();
});

// ESC to close
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeOutput();
});

// Show Subject Selection for Study Guide
async function showSubjectSelection() {
    outputTitle.textContent = '📚 Study Guide - Select Subject';
    outputBody.className = 'panel-body';
    outputBody.innerHTML = '<div class="loading"><div class="spinner"></div><p>Loading subjects...</p></div>';
    output.classList.add('active');
    
    try {
        // Get subjects list
        const res = await fetch(`${API_URL}/get-subjects`);
        const data = await res.json();
        
        if (!data.subjects || data.subjects.length === 0) {
            throw new Error('No subjects found');
        }
        
        // Build subject selection UI
        let html = '<div style="padding: 1rem;">';
        html += '<h3 style="margin-bottom: 1.5rem; color: #00ff00;">📚 SELECT SUBJECT FOR STUDY GUIDE</h3>';
        html += '<div style="display: grid; gap: 1rem;">';
        
        data.subjects.forEach(subject => {
            const status = subject.cat1_pct >= 80 ? '🟢' : subject.cat1_pct >= 60 ? '🟡' : '🔴';
            html += `
                <button class="subject-btn" data-subject="${subject.number}" style="
                    background: rgba(0, 255, 0, 0.1);
                    border: 1px solid #00ff00;
                    padding: 1rem;
                    text-align: left;
                    cursor: pointer;
                    border-radius: 4px;
                    transition: all 0.3s;
                ">
                    <div style="font-size: 1.2rem; font-weight: bold; margin-bottom: 0.5rem;">
                        ${status} ${subject.name}
                    </div>
                    <div style="font-size: 0.9rem; color: #00aa00;">
                        Code: ${subject.code} | CAT1: ${subject.cat1_score}/${subject.cat1_max} (${subject.cat1_pct}%)
                    </div>
                </button>
            `;
        });
        
        html += '</div></div>';
        
        outputBody.innerHTML = html;
        
        // Add click handlers
        document.querySelectorAll('.subject-btn').forEach(btn => {
            btn.addEventListener('mouseover', function() {
                this.style.background = 'rgba(0, 255, 0, 0.2)';
                this.style.borderColor = '#00ff00';
            });
            btn.addEventListener('mouseout', function() {
                this.style.background = 'rgba(0, 255, 0, 0.1)';
            });
            btn.addEventListener('click', async function() {
                const subjectNum = this.getAttribute('data-subject');
                await generateStudyGuide(subjectNum);
            });
        });
        
    } catch (err) {
        showError(`Failed to load subjects: ${err.message}`);
    }
}

// Generate Study Guide for selected subject
async function generateStudyGuide(subjectNumber) {
    outputTitle.textContent = '📚 Generating Study Guide...';
    outputBody.className = 'panel-body';
    outputBody.innerHTML = '<div class="loading"><div class="spinner"></div><p>Generating personalized study guide with Advanced AI...<br/>This may take 10-15 seconds...</p></div>';
    
    try {
        const res = await fetch(`${API_URL}/gemini-features`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                feature: 'study-guide',
                subject_number: subjectNumber
            })
        });
        
        const data = await res.json();
        
        if (data.success) {
            outputTitle.textContent = '📚 Study Guide Generated';
            displayOutput(data.output);
        } else {
            throw new Error(data.error || 'Failed to generate study guide');
        }
        
    } catch (err) {
        showError(`Failed to generate study guide: ${err.message}`);
    }
}

// Chat Interface
function showChatInterface() {
    outputTitle.textContent = '💬 AI Chatbot';
    outputBody.className = 'panel-body chat-mode';
    outputBody.innerHTML = `
        <div class="chat-container">
            <div class="chat-messages" id="chatMessages">
                <div class="chat-message bot">
                    <strong>AI:</strong> Hello! I'm your CLI-TOP chatbot with full access to your VTOP data. Ask me anything about your academics!
                </div>
            </div>
            <div class="chat-input-container">
                <input type="text" id="chatInput" placeholder="Ask me anything..." />
                <button id="chatSend" class="btn-exec">Send</button>
            </div>
        </div>
    `;
    output.classList.add('active');
    
    // Setup chat handlers
    const chatInput = document.getElementById('chatInput');
    const chatSend = document.getElementById('chatSend');
    const chatMessages = document.getElementById('chatMessages');
    
    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;
        
        // Add user message
        const userMsg = document.createElement('div');
        userMsg.className = 'chat-message user';
        userMsg.innerHTML = `<strong>You:</strong> ${escape(message)}`;
        chatMessages.appendChild(userMsg);
        chatInput.value = '';
        
        // Add loading
        const loadingMsg = document.createElement('div');
        loadingMsg.className = 'chat-message bot loading';
        loadingMsg.innerHTML = '<strong>AI:</strong> <span class="typing">Thinking...</span>';
        chatMessages.appendChild(loadingMsg);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        try {
            // Call chat endpoint directly - no export needed
            const res = await fetch(`${API_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });
            
            const data = await res.json();
            
            // Remove loading
            loadingMsg.remove();
            
            // Add bot response
            const botMsg = document.createElement('div');
            botMsg.className = 'chat-message bot';
            botMsg.innerHTML = `<strong>AI:</strong> ${formatMarkdown(data.response || data.error || 'No response')}`;
            chatMessages.appendChild(botMsg);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
        } catch (err) {
            loadingMsg.remove();
            const errorMsg = document.createElement('div');
            errorMsg.className = 'chat-message bot error';
            errorMsg.innerHTML = `<strong>Error:</strong> ${escape(err.message)}`;
            chatMessages.appendChild(errorMsg);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    
    chatSend.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    chatInput.focus();
}

// Voice Assistant - Web-based version
let voiceRecognition = null;
let voiceSynthesis = window.speechSynthesis;
let isListening = false;

function showVoiceInstructions() {
    outputTitle.textContent = '🎙️ Voice Chatbot';
    outputBody.className = 'panel-body voice-mode';
    outputBody.innerHTML = `
        <div class="voice-container">
            <div class="voice-status">
                <div class="voice-indicator" id="voiceIndicator">
                    <div class="mic-icon">🎤</div>
                    <div class="status-text" id="statusText">Click "Start Listening" to begin</div>
                </div>
            </div>
            
            <div class="voice-controls">
                <button id="startVoice" class="btn-voice btn-start">🎤 Start Listening</button>
                <button id="stopVoice" class="btn-voice btn-stop" style="display:none;">⏹️ Stop</button>
            </div>
            
            <div class="voice-transcript" id="voiceTranscript">
                <h4>📝 Your Question:</h4>
                <div class="transcript-content" id="transcriptContent">
                    <p class="help-text">This is the AI Chatbot with voice! Ask me anything:</p>
                    <ul class="voice-commands">
                        <li>"Which subject has the lowest marks?"</li>
                        <li>"How is my attendance in Compiler Design?"</li>
                        <li>"What should I focus on for upcoming exams?"</li>
                        <li>"Can I skip classes in Database Systems?"</li>
                        <li>"What's my predicted grade in Artificial Intelligence?"</li>
                    </ul>
                </div>
            </div>
            
            <div class="voice-response" id="voiceResponse" style="display:none;">
                <h4>🤖 AI Response:</h4>
                <div class="response-content" id="responseContent"></div>
            </div>
        </div>
    `;
    output.classList.add('active');
    
    // Initialize Web Speech API
    initVoiceRecognition();
}

function initVoiceRecognition() {
    // Check browser support
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        document.getElementById('statusText').textContent = '❌ Voice recognition not supported in this browser';
        document.getElementById('startVoice').disabled = true;
        return;
    }
    
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    voiceRecognition = new SpeechRecognition();
    
    voiceRecognition.continuous = false;
    voiceRecognition.interimResults = true;
    voiceRecognition.lang = 'en-US';
    
    const startBtn = document.getElementById('startVoice');
    const stopBtn = document.getElementById('stopVoice');
    const indicator = document.getElementById('voiceIndicator');
    const statusText = document.getElementById('statusText');
    const transcriptContent = document.getElementById('transcriptContent');
    const responseDiv = document.getElementById('voiceResponse');
    const responseContent = document.getElementById('responseContent');
    
    // Start listening
    startBtn.addEventListener('click', () => {
        voiceRecognition.start();
        isListening = true;
        startBtn.style.display = 'none';
        stopBtn.style.display = 'inline-block';
        indicator.classList.add('listening');
        statusText.textContent = '🎤 Listening... Speak now!';
        transcriptContent.innerHTML = '<p class="interim">Listening...</p>';
    });
    
    // Stop listening
    stopBtn.addEventListener('click', () => {
        voiceRecognition.stop();
        isListening = false;
        startBtn.style.display = 'inline-block';
        stopBtn.style.display = 'none';
        indicator.classList.remove('listening');
        statusText.textContent = 'Click "Start Listening" to begin';
    });
    
    // Handle results
    voiceRecognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                finalTranscript += transcript;
            } else {
                interimTranscript += transcript;
            }
        }
        
        if (interimTranscript) {
            transcriptContent.innerHTML = `<p class="interim">${escape(interimTranscript)}</p>`;
        }
        
        if (finalTranscript) {
            transcriptContent.innerHTML = `<p class="final">You said: "${escape(finalTranscript)}"</p>`;
            statusText.textContent = '⏳ Processing...';
            indicator.classList.remove('listening');
            indicator.classList.add('processing');
            
            // Process the command
            processVoiceCommand(finalTranscript, responseDiv, responseContent, indicator, statusText, startBtn, stopBtn);
        }
    };
    
    // Handle errors
    voiceRecognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        isListening = false;
        startBtn.style.display = 'inline-block';
        stopBtn.style.display = 'none';
        indicator.classList.remove('listening', 'processing');
        
        if (event.error === 'no-speech') {
            statusText.textContent = '❌ No speech detected. Try again!';
        } else if (event.error === 'not-allowed') {
            statusText.textContent = '❌ Microphone access denied';
        } else {
            statusText.textContent = `❌ Error: ${event.error}`;
        }
    };
    
    // Handle end
    voiceRecognition.onend = () => {
        if (isListening) {
            // Restart if manually stopped
            isListening = false;
            startBtn.style.display = 'inline-block';
            stopBtn.style.display = 'none';
            indicator.classList.remove('listening');
        }
    };
}

async function processVoiceCommand(command, responseDiv, responseContent, indicator, statusText, startBtn, stopBtn) {
    try {
        // Use chatbot API directly (same as AI Chatbot feature)
        const res = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: command })
        });
        
        const data = await res.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Failed to get response');
        }
        
        const response = data.response || 'No response received';
        
        // Display result
        responseDiv.style.display = 'block';
        responseContent.innerHTML = `<pre>${formatMarkdown(response)}</pre>`;
        
        // Speak the response
        speak(response);
        
        // Update UI
        indicator.classList.remove('processing');
        indicator.classList.add('done');
        statusText.textContent = '✅ Response ready! Click "Start Listening" for another question';
        startBtn.style.display = 'inline-block';
        stopBtn.style.display = 'none';
        
    } catch (error) {
        console.error('Voice command error:', error);
        responseDiv.style.display = 'block';
        responseContent.innerHTML = `<p style="color:#ff6b6b;">❌ Error: ${escape(error.message)}</p>`;
        
        indicator.classList.remove('processing');
        statusText.textContent = '❌ Error occurred. Try again!';
        startBtn.style.display = 'inline-block';
        stopBtn.style.display = 'none';
        
        // Speak error
        speak('Sorry, I encountered an error. Please try again.');
    }
}

async function executeSmartCommand(smartType) {
    // Export data first
    const exp = await fetch(`${API_URL}/ai-export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
    });
    
    const expData = await exp.json();
    if (!expData.success) throw new Error(expData.error);
    
    // Call smart command endpoint
    const res = await fetch(`${API_URL}/smart-command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ai_data: expData.data, smart_type: smartType })
    });
    
    const data = await res.json();
    if (!data.success) throw new Error(data.error);
    
    return typeof data.output === 'object' ? data.output.content : data.output;
}

async function executeVTOPCommand(cmd) {
    const res = await fetch(`${API_URL}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, command: cmd })
    });
    
    const data = await res.json();
    if (!data.success) throw new Error(data.error);
    
    return typeof data.output === 'object' ? data.output.content : data.output;
}

async function executeAIFeature(feature) {
    const exp = await fetch(`${API_URL}/ai-export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
    });
    
    const expData = await exp.json();
    if (!expData.success) throw new Error(expData.error);
    
    const res = await fetch(`${API_URL}/ai-features`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ai_data: expData.data, feature })
    });
    
    const data = await res.json();
    if (!data.success) throw new Error(data.error);
    
    return typeof data.output === 'object' ? data.output.content : data.output;
}

async function executeChatCommand(message) {
    // Use voice-chat endpoint which has full VTOP context like terminal version
    const res = await fetch(`${API_URL}/voice-chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
    });
    
    const data = await res.json();
    if (!data.success) throw new Error(data.error);
    
    return data.response || 'No response';
}

function speak(text) {
    if ('speechSynthesis' in window) {
        // Cancel any ongoing speech
        speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        
        speechSynthesis.speak(utterance);
    }
}

// Semester selector
async function showSemesterSelector() {
    return new Promise((resolve) => {
        outputTitle.textContent = 'Select Semester';
        outputBody.className = 'panel-body';
        outputBody.innerHTML = `
            <div style="padding:2rem;">
                <h3 style="margin-bottom:1.5rem;">Choose a semester:</h3>
                <div class="semester-list">
                    <button class="semester-btn" data-sem="1">1. Fall Semester 2023-24</button>
                    <button class="semester-btn" data-sem="2">2. Winter Semester 2023-24</button>
                    <button class="semester-btn" data-sem="3">3. Fall Semester 2024-25</button>
                    <button class="semester-btn" data-sem="4">4. Winter Semester 2024-25</button>
                    <button class="semester-btn" data-sem="5">5. Fall Semester 2025-26 (Current)</button>
                </div>
                <button class="btn-cancel" style="margin-top:1.5rem;">Cancel</button>
            </div>
        `;
        output.classList.add('active');
        
        // Add click handlers
        document.querySelectorAll('.semester-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const choice = btn.dataset.sem;
                resolve(choice);
            });
        });
        
        // Handle cancel
        const cancelBtn = outputBody.querySelector('.btn-cancel');
        cancelBtn.addEventListener('click', () => {
            output.classList.remove('active');
            resolve(null);
        });
    });
}

console.log('%c╔══════════════════════════════════════╗\n║   BETTER VTOP v2.0                ║\n║   Neo-Brutalism + Advanced AI     ║\n╚══════════════════════════════════════╝', 'color:#FF6B9D;font-weight:bold;font-size:14px;');
