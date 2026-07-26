document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const toggleBtn = document.getElementById('chatbot-toggle-btn');
    const closeBtn = document.getElementById('chatbot-close-btn');
    const clearBtn = document.getElementById('chatbot-clear-btn');
    const chatWindow = document.getElementById('chatbot-window');
    const chatForm = document.getElementById('chatbot-form');
    const chatInput = document.getElementById('chatbot-input');
    const chatMessages = document.getElementById('chatbot-messages');
    const typingIndicator = document.getElementById('chatbot-typing-indicator');
    const submitBtn = chatForm.querySelector('button[type="submit"]');

    // API Configuration
    // If running locally on a custom port, connect directly to the chatbot port (Django port + 1).
    // Otherwise (in production), use the relative Nginx proxy path.
    const isLocalDev = (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost') && window.location.port;
    const chatbotPort = isLocalDev ? (parseInt(window.location.port) + 1) : 8001;
    const API_URL = isLocalDev ? `http://${window.location.hostname}:${chatbotPort}/api/chat` : '/chatbot_api/chat';
    
    // Conversation Memory - get existing session or start null
    let currentSessionId = sessionStorage.getItem('chatbot_session_id') || null;

    // Auto-resize textarea
    chatInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight < 96 ? this.scrollHeight : 96) + 'px';
        if(this.value === '') {
            this.style.height = 'auto';
        }
    });

    // Handle Enter key (submit on Enter, newline on Shift+Enter)
    chatInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (this.value.trim() !== '') {
                chatForm.dispatchEvent(new Event('submit'));
            }
        }
    });

    // Toggle Chat Window
    const toggleChat = () => {
        const isHidden = chatWindow.classList.contains('hidden');
        if (isHidden) {
            chatWindow.classList.remove('hidden');
            chatWindow.classList.add('flex');
            // Small delay to allow display:flex to apply before animating opacity/transform
            setTimeout(() => {
                chatWindow.classList.remove('opacity-0', 'scale-95');
                chatWindow.classList.add('opacity-100', 'scale-100');
                chatInput.focus();
                scrollToBottom();
            }, 10);
            
            // Change icon to 'X'
            toggleBtn.innerHTML = '<i class="fas fa-times text-2xl"></i>';
        } else {
            chatWindow.classList.remove('opacity-100', 'scale-100');
            chatWindow.classList.add('opacity-0', 'scale-95');
            
            // Wait for animation to finish before hiding
            setTimeout(() => {
                chatWindow.classList.add('hidden');
                chatWindow.classList.remove('flex');
            }, 300);
            
            // Change icon back to chat
            toggleBtn.innerHTML = '<i class="fas fa-comment-dots text-2xl"></i>';
        }
    };

    toggleBtn.addEventListener('click', toggleChat);
    closeBtn.addEventListener('click', toggleChat);

    // Auto-scroll to bottom
    const scrollToBottom = () => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    // Format basic markdown (bold, lists, code)
    const formatMessage = (text) => {
        if (!text) return '';
        
        let formatted = text
            // Code blocks
            .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
            // Inline code
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            // Bold
            .replace(/\*\*([^\*]+)\*\*/g, '<strong>$1</strong>')
            // Links
            .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" class="text-blue-600 hover:underline">$1</a>')
            // Lists
            .replace(/^\s*[-*]\s+(.+)$/gm, '<ul><li>$1</li></ul>')
            // Fix nested/adjacent lists
            .replace(/<\/ul>\s*<ul>/g, '')
            // Paragraphs/Newlines
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br>');
            
        return `<div class="chat-msg-content"><p>${formatted}</p></div>`;
    };

    // Add message to UI
    const addMessage = (content, isUser = false) => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `flex items-start ${isUser ? 'justify-end' : ''}`;
        
        const formattedContent = isUser ? content.replace(/\n/g, '<br>') : formatMessage(content);

        if (isUser) {
            messageDiv.innerHTML = `
                <div class="mr-3 chat-msg-user p-3 rounded-2xl rounded-tr-none shadow-sm max-w-[85%] text-sm">
                    ${formattedContent}
                </div>
                <div class="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 text-xs shadow-sm">
                    <i class="fas fa-user"></i>
                </div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="flex-shrink-0 w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs shadow-sm">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="ml-3 chat-msg-ai p-3 rounded-2xl rounded-tl-none shadow-sm border border-gray-100 max-w-[85%] text-sm">
                    ${formattedContent}
                </div>
            `;
        }

        chatMessages.appendChild(messageDiv);
        scrollToBottom();
    };

    // Show/hide typing indicator
    const setTyping = (isTyping) => {
        if (isTyping) {
            typingIndicator.classList.remove('hidden');
            scrollToBottom();
        } else {
            typingIndicator.classList.add('hidden');
        }
        submitBtn.disabled = isTyping;
        chatInput.disabled = isTyping;
    };

    // Handle form submission
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const message = chatInput.value.trim();
        if (!message) return;

        // Add user message to UI
        addMessage(message, true);
        
        // Reset input
        chatInput.value = '';
        chatInput.style.height = 'auto';
        
        // Show typing indicator
        setTyping(true);

        try {
            // Send request to FastAPI backend with memory
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ 
                    message: message,
                    session_id: currentSessionId
                })
            });

            if (!response.ok) {
                throw new Error(`Server returned ${response.status}`);
            }

            const data = await response.json();
            
            // Save the session ID to remember context!
            if (data.session_id) {
                currentSessionId = data.session_id;
                sessionStorage.setItem('chatbot_session_id', currentSessionId);
            }
            
            // Add AI response to UI
            addMessage(data.response, false);
            
        } catch (error) {
            console.error('Chatbot API Error:', error);
            addMessage(`⚠️ Sorry, I could not connect to the AI server. Please make sure the backend is running on port ${chatbotPort}.`, false);
        } finally {
            setTyping(false);
            chatInput.focus();
        }
    });

    // Clear chat
    clearBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to clear the chat history?')) {
            // Keep only the welcome message
            const welcomeMsg = chatMessages.firstElementChild;
            chatMessages.innerHTML = '';
            chatMessages.appendChild(welcomeMsg);
            
            // Clear memory
            currentSessionId = null;
            sessionStorage.removeItem('chatbot_session_id');
        }
    });
});
