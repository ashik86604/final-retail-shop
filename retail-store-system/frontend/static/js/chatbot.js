const CHATBOT_URL = 'http://localhost:5000/api/chatbot';

let chatHistory = [];

document.addEventListener('DOMContentLoaded', () => {
    console.log('Chatbot page loaded');
    setupChatForm();
    loadChatHistory();
});

function setupChatForm() {
    const chatForm = document.getElementById('chatForm');
    const messageInput = document.getElementById('messageInput');
    
    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const message = messageInput.value.trim();
            if (!message) return;

            // Add user message to chat
            addMessageToChat('user', message);
            messageInput.value = '';

            try {
                const response = await fetch(`${CHATBOT_URL}/ask`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message })
                });

                const result = await response.json();

                if (result.status === 'success') {
                    addMessageToChat('bot', result.response);
                } else {
                    addMessageToChat('bot', 'Error: ' + result.message);
                }
            } catch (error) {
                console.error('Error:', error);
                addMessageToChat('bot', 'Error connecting to chatbot: ' + error.message);
            }
        });
    }
}

function addMessageToChat(sender, message) {
    const chatBody = document.getElementById('chatBody');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `mb-3 text-${sender === 'user' ? 'end' : 'start'}`;
    
    const messageContent = document.createElement('div');
    messageContent.className = `d-inline-block px-3 py-2 rounded-3 ${
        sender === 'user' 
            ? 'bg-primary text-white' 
            : 'bg-light text-dark'
    }`;
    messageContent.style.maxWidth = '70%';
    messageContent.style.wordWrap = 'break-word';
    messageContent.innerHTML = message;
    
    messageDiv.appendChild(messageContent);
    chatBody.appendChild(messageDiv);
    
    // Auto scroll to bottom
    chatBody.scrollTop = chatBody.scrollHeight;
}

function loadChatHistory() {
    // Load initial greeting
    addMessageToChat('bot', '👋 Welcome to RetailHub Assistant! Ask me about your sales, inventory, customers, or any business metrics. What would you like to know?');
}

function clearChat() {
    const chatBody = document.getElementById('chatBody');
    chatBody.innerHTML = '';
    loadChatHistory();
}