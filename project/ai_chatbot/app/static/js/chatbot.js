document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    const typingIndicator = document.getElementById('typing-indicator');
    const clearChatBtn = document.getElementById('clear-chat');
    const submitBtn = chatForm.querySelector('button[type="submit"]');

    // Auto-scroll to bottom
    const scrollToBottom = () => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    // Add message to UI
    const addMessage = (content, isUser = false) => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `flex items-start ${isUser ? 'justify-end' : ''}`;
        
        // Simple line break replacement for Phase 1
        const formattedContent = content.replace(/\n/g, '<br>');

        if (isUser) {
            messageDiv.innerHTML = `
                <div class="mr-3 bg-primary text-white p-3 rounded-2xl rounded-tr-none shadow-sm max-w-[80%]">
                    <p class="text-sm">${formattedContent}</p>
                </div>
                <div class="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 text-sm">
                    <i class="fas fa-user"></i>
                </div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white text-sm">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="ml-3 bg-white p-3 rounded-2xl rounded-tl-none shadow-sm border border-gray-100 max-w-[80%]">
                    <p class="text-gray-800 text-sm">${formattedContent}</p>
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
        userInput.disabled = isTyping;
    };

    // Handle form submission
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const message = userInput.value.trim();
        if (!message) return;

        // Add user message to UI
        addMessage(message, true);
        userInput.value = '';
        
        // Show typing indicator
        setTyping(true);

        try {
            // Send request to API
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            
            // Add AI response to UI
            addMessage(data.response, false);
            
        } catch (error) {
            console.error('Error:', error);
            addMessage('Sorry, I encountered an error connecting to the server. Please check the backend console.', false);
        } finally {
            setTyping(false);
            userInput.focus();
        }
    });

    // Clear chat
    clearChatBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to clear the chat?')) {
            // Keep only the welcome message
            const welcomeMsg = chatMessages.firstElementChild;
            chatMessages.innerHTML = '';
            chatMessages.appendChild(welcomeMsg);
        }
    });
});
