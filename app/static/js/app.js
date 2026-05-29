let currentChart = null;
let currentSessionId = localStorage.getItem('fitness_session_id');

function showSection(sectionId) {
    document.querySelectorAll('.content section').forEach(section => {
        section.style.display = 'none';
    });
    document.getElementById(sectionId).style.display = 'block';
    
    document.querySelectorAll('.sidebar nav ul li').forEach(li => {
        li.classList.remove('active');
    });
    // event.target is not always reliable if called programmatically
    if (window.event && window.event.target) {
        window.event.target.classList.add('active');
    }

    if (sectionId === 'dashboard-section') {
        loadChart('weight');
    } else if (sectionId === 'history-section') {
        loadHistory('workout');
    }
}

async function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    if (!message) return;

    appendMessage('user', message);
    input.value = '';

    // Create a placeholder for AI response
    const aiMsgDiv = appendMessage('ai', '...');
    const statusDiv = document.createElement('div');
    statusDiv.className = 'agent-status';
    aiMsgDiv.parentNode.insertBefore(statusDiv, aiMsgDiv);

    let fullResponse = '';

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, session_id: currentSessionId })
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const dataStr = line.slice(6).trim();
                    if (dataStr === '[DONE]') {
                        statusDiv.remove();
                        continue;
                    }

                    try {
                        const data = JSON.parse(dataStr);
                        
                        if (data.session_id && data.session_id !== currentSessionId) {
                            currentSessionId = data.session_id;
                            localStorage.setItem('fitness_session_id', currentSessionId);
                            loadSessions();
                        }

                        if (data.status) {
                            statusDiv.textContent = data.status;
                            statusDiv.style.display = 'block';
                        }

                        if (data.text) {
                            if (fullResponse === '') aiMsgDiv.innerHTML = '';
                            fullResponse += data.text;
                            aiMsgDiv.innerHTML = marked.parse(fullResponse);
                            document.getElementById('chat-box').scrollTop = document.getElementById('chat-box').scrollHeight;
                        }

                        if (data.error) {
                            aiMsgDiv.textContent = `Error: ${data.error}`;
                            statusDiv.remove();
                        }
                    } catch (e) {
                        console.error('Error parsing JSON chunk', e);
                    }
                }
            }
        }
    } catch (error) {
        aiMsgDiv.textContent = 'Sorry, I encountered an error. Please check your connection and try again.';
        if (statusDiv) statusDiv.remove();
    }
}

async function loadSessions() {
    try {
        const response = await fetch('/sessions');
        const sessions = await response.json();
        const list = document.getElementById('session-list');
        list.innerHTML = '';
        
        sessions.sort((a, b) => b.last_update - a.last_update).forEach(session => {
            const li = document.createElement('li');
            li.title = session.id;
            if (session.id === currentSessionId) {
                li.classList.add('active-session');
            }
            
            const titleSpan = document.createElement('span');
            titleSpan.textContent = session.title;
            titleSpan.className = 'session-title';
            titleSpan.onclick = () => switchSession(session.id);
            
            const deleteBtn = document.createElement('button');
            deleteBtn.innerHTML = '×';
            deleteBtn.className = 'delete-session-btn';
            deleteBtn.onclick = (e) => {
                e.stopPropagation();
                deleteSession(session.id);
            };
            
            li.appendChild(titleSpan);
            li.appendChild(deleteBtn);
            list.appendChild(li);
        });
    } catch (error) {
        console.error('Error loading sessions:', error);
    }
}

async function deleteSession(sessionId) {
    if (!confirm('Are you sure you want to delete this chat?')) return;
    
    try {
        const response = await fetch(`/chat/${sessionId}`, {
            method: 'DELETE'
        });
        if (response.ok) {
            if (currentSessionId === sessionId) {
                newChat();
            }
            loadSessions();
        }
    } catch (error) {
        console.error('Error deleting session:', error);
    }
}

async function switchSession(sessionId) {
    currentSessionId = sessionId;
    localStorage.setItem('fitness_session_id', currentSessionId);
    showSection('chat-section');
    await loadChatHistory();
    loadSessions(); // Update highlights
}

async function loadChatHistory() {
    if (!currentSessionId) return;

    try {
        const response = await fetch(`/chat/${currentSessionId}/history`);
        if (!response.ok) return;
        
        const history = await response.json();
        const chatBox = document.getElementById('chat-box');
        chatBox.innerHTML = '';
        
        if (history.length === 0) {
            appendMessage('ai', 'This session has no messages yet.');
        } else {
            history.forEach(msg => {
                appendMessage(msg.role === 'user' ? 'user' : 'ai', msg.text);
            });
        }
    } catch (error) {
        console.error('Error loading chat history:', error);
    }
}

function newChat() {
    currentSessionId = null;
    localStorage.removeItem('fitness_session_id');
    document.getElementById('chat-box').innerHTML = '';
    loadSessions(); // Clear highlights
    appendMessage('ai', 'Started a new session. How can I help you today?');
}

function appendMessage(role, text) {
    const chatBox = document.getElementById('chat-box');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}-message`;
    
    if (role === 'ai') {
        msgDiv.innerHTML = marked.parse(text);
    } else {
        msgDiv.textContent = text;
    }
    
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    return msgDiv;
}

async function loadChart(metricType) {
    try {
        const response = await fetch(`/metrics?metric_type=${metricType}`);
        const data = await response.json();

        const labels = data.map(d => new Date(d.date).toLocaleDateString());
        const values = data.map(d => d.value);

        const ctx = document.getElementById('progressChart').getContext('2d');
        
        if (currentChart) {
            currentChart.destroy();
        }

        currentChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: metricType.replace('_', ' ').toUpperCase(),
                    data: values,
                    borderColor: '#2ecc71',
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    } catch (error) {
        console.error('Error loading chart:', error);
    }
}

async function loadHistory(type) {
    const historyList = document.getElementById('history-list');
    historyList.innerHTML = 'Loading...';

    try {
        const response = await fetch(`/history?history_type=${type}`);
        const data = await response.json();

        historyList.innerHTML = '';
        if (data.length === 0) {
            historyList.innerHTML = 'No history found.';
            return;
        }

        data.forEach(item => {
            const div = document.createElement('div');
            div.className = 'history-item';
            if (type === 'workout') {
                div.innerHTML = `<strong>${new Date(item.date).toLocaleDateString()}</strong>: ${item.exercise} - ${item.sets} sets x ${item.reps} reps @ ${item.weight} lbs`;
            } else {
                div.innerHTML = `<strong>${new Date(item.date).toLocaleDateString()}</strong>: ${item.meal_name} - ${item.calories} cal (P:${item.macros.p} C:${item.macros.c} F:${item.macros.f})`;
            }
            historyList.appendChild(div);
        });
    } catch (error) {
        historyList.innerHTML = 'Error loading history.';
    }
}

// Handle enter key in input
document.getElementById('user-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Load chat history and sessions on startup
loadChatHistory();
loadSessions();
