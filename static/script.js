document.addEventListener('DOMContentLoaded', () => {
    const connectBtn = document.getElementById('connectBtn');
    const sendBtn = document.getElementById('sendBtn');
    const userQuery = document.getElementById('userQuery');
    const chatContainer = document.getElementById('chatContainer');
    const connectionStatus = document.getElementById('connectionStatus');
    const statusText = connectionStatus.querySelector('.status-text');

    // --- Helper Functions ---
    function addMessage(text, type) {
        const div = document.createElement('div');
        div.className = `message ${type}`;
        div.innerHTML = `<div class="message-content">${text}</div>`;
        chatContainer.appendChild(div);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function setStatus(connected, msg) {
        if (connected) {
            connectionStatus.classList.add('connected');
            statusText.textContent = msg || "Connected";
            sendBtn.disabled = false;
        } else {
            connectionStatus.classList.remove('connected');
            statusText.textContent = msg || "Disconnected";
            sendBtn.disabled = true;
        }
    }

    // --- Event Listeners ---

    // Connect to Database
    connectBtn.addEventListener('click', async () => {
        const originalText = connectBtn.innerHTML;
        connectBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Checking Server...';
        connectBtn.disabled = true;

        // Step 1: Check basic connectivity
        try {
            const healthReq = await fetch('http://127.0.0.1:5000/health');
            if (!healthReq.ok) throw new Error("Server Health Check Failed");
        } catch (e) {
            setStatus(false, "Server Unreachable");
            addMessage(`CRITIAL ERROR: Cannot reach Flask Server at http://127.0.0.1:5000. \nDetails: ${e.message}`, 'system-message');
            connectBtn.innerHTML = originalText;
            connectBtn.disabled = false;
            return;
        }

        connectBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Connecting DB...';

        const data = {
            host: document.getElementById('host').value,
            port: document.getElementById('port').value,
            user: document.getElementById('username').value,
            password: document.getElementById('password').value,
            database: document.getElementById('database').value
        };

        try {
            const response = await fetch('http://127.0.0.1:5000/api/connect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.success) {
                setStatus(true, "Connected to " + data.database);
                addMessage(`Successfully connected to database: ${data.database}`, 'system-message');
            } else {
                setStatus(false, "Connection Failed");
                addMessage(`Connection failed: ${result.error}`, 'system-message');
            }
        } catch (error) {
            setStatus(false, "Network Error");
            addMessage(`Network error during DB Connect: ${error.message}. Is the server running?`, 'system-message');
        } finally {
            connectBtn.innerHTML = originalText;
            connectBtn.disabled = false;
        }
    });

    // Send Chat Message
    async function sendMessage() {
        const query = userQuery.value.trim();
        if (!query) return;

        addMessage(query, 'user');
        userQuery.value = '';
        sendBtn.disabled = true;

        // Create a temporary "Thinking..." placeholder
        const thinkingId = 'thinking-' + Date.now();
        const thinkingHtml = `
            <div id="${thinkingId}" class="message bot thinking-message">
                <i class="fa-solid fa-microchip fa-bounce"></i> Analyzing...
            </div>`;
        chatContainer.insertAdjacentHTML('beforeend', thinkingHtml);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        try {
            const response = await fetch('http://127.0.0.1:5000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            });
            const result = await response.json();

            // Remove thinking placeholder
            const thinkingEl = document.getElementById(thinkingId);
            if (thinkingEl) thinkingEl.remove();

            if (result.success) {
                // 1. Show Thinking Process
                if (result.thought_process && result.thought_process.length > 0) {
                    let stepsHtml = '<div class="thought-process"><div class="process-title"><i class="fa-solid fa-brain"></i> AI Reasoning</div><ul class="process-steps">';
                    result.thought_process.forEach(step => {
                        stepsHtml += `<li><i class="fa-solid fa-check"></i> ${step}</li>`;
                    });
                    stepsHtml += '</ul></div>';

                    const processDiv = document.createElement('div');
                    processDiv.className = 'message bot process-container';
                    processDiv.innerHTML = stepsHtml;
                    chatContainer.appendChild(processDiv);
                }

                // 2. Show SQL Preview (Collapsible)
                if (result.is_sql_query && result.sql_query) {
                    const sqlId = 'sql-' + Date.now();
                    const sqlHtml = `
                        <div class="sql-container">
                            <button class="sql-header" onclick="document.getElementById('${sqlId}').classList.toggle('visible')">
                                <span><i class="fa-solid fa-code"></i> View Generated SQL</span>
                                <i class="fa-solid fa-chevron-down"></i>
                            </button>
                            <div id="${sqlId}" class="sql-code-block">
                                <pre><code class="language-sql">${result.sql_query}</code></pre>
                            </div>
                        </div>`;

                    const sqlDiv = document.createElement('div');
                    sqlDiv.className = 'message bot no-bg'; // Special class for non-bubble
                    sqlDiv.innerHTML = sqlHtml;
                    chatContainer.appendChild(sqlDiv);
                }

                // 3. Show Final Response
                addMessage(result.response, 'bot');

            } else {
                addMessage(`Error: ${result.error}`, 'bot');
            }
        } catch (error) {
            const thinkingEl = document.getElementById(thinkingId);
            if (thinkingEl) thinkingEl.remove();
            addMessage(`Communication Error: ${error.message}`, 'bot');
        } finally {
            sendBtn.disabled = false;
            userQuery.focus();
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }

    // --- Voice Interaction Logic ---
    const micBtn = document.getElementById('micBtn');

    // Check browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.lang = 'en-US';
        recognition.interimResults = false;

        recognition.onstart = () => {
            micBtn.classList.add('listening');
            userQuery.placeholder = "Listening...";
        };

        recognition.onend = () => {
            micBtn.classList.remove('listening');
            userQuery.placeholder = "Ask a question about your data...";
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            userQuery.value = transcript;
            // Auto-send after a brief pause for user to verify, or let user click send
            // Let's keep it manual send for accuracy, or just focus the input
            userQuery.focus();

            // Optional: Auto-click send if confidence is high? 
            // For now, let's just fill the input.
        };

        recognition.onerror = (event) => {
            console.error("Speech Error:", event.error);
            micBtn.classList.remove('listening');
            userQuery.placeholder = "Error. Try typing.";
        };

        micBtn.addEventListener('click', () => {
            if (micBtn.classList.contains('listening')) {
                recognition.stop();
            } else {
                recognition.start();
            }
        });
    } else {
        // Fallback for browsers without support
        micBtn.style.display = 'none';
        console.warn("Web Speech API not supported in this browser.");
    }

    sendBtn.addEventListener('click', sendMessage);
    userQuery.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
});
