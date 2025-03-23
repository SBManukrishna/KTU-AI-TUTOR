// frontend/chat_bot.js (Updated for Markdown Support)

// Select DOM elements
const themeToggle = document.querySelector('.theme-toggle');
const chatContainer = document.getElementById('chatContainer');
const messageInput = document.querySelector('.message-input');
const sendButton = document.querySelector('.send-button');
const typingIndicator = document.querySelector('.typing-indicator');

// Theme toggling
let isDarkTheme = false;
const chatDiv = document.querySelector('.chat-div');
themeToggle.addEventListener('click', () => {
    isDarkTheme = !isDarkTheme;
    chatDiv.setAttribute('data-theme', isDarkTheme ? 'dark' : 'light');
    themeToggle.innerHTML = isDarkTheme ?
        '<i class="fas fa-sun"></i>' :
        '<i class="fas fa-moon"></i>';
});

// Create chat message elements; now using Markdown to HTML conversion for the message content
function createMessageElement(content, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;

    // Parse Markdown content using marked library
    const parsedContent = marked.parse(content);

    messageDiv.innerHTML = `
        <div class="avatar">${isUser ? 'U' : 'AI'}</div>
        <div class="message-bubble">${parsedContent}</div>
    `;
    return messageDiv;
}

function addMessage(content, isUser = false) {
    const messageElement = createMessageElement(content, isUser);
    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showTypingIndicator() {
    typingIndicator.style.display = 'block';
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function hideTypingIndicator() {
    typingIndicator.style.display = 'none';
}

// API Setup for Together AI
const apiKey = "3524c3a5bde0b9a8bd4120ad72ab2a049ebf88ca0b5dba2abc599445e668fd4b";  // Replace with your actual key
const apiUrl = "https://api.together.xyz/v1/chat/completions";

// Store the conversation history
const conversationHistory = [];

// Modified function to get bot response with conversation history
async function getBotResponse(userMessage) {
    // Add the user's message to conversation history
    conversationHistory.push({ role: "user", content: userMessage });

    showTypingIndicator();

    // Retrieve course context (if needed)
    const syllabusDiv = document.querySelector('.syllabus-div');
    const courseContext = syllabusDiv ? syllabusDiv.innerText.trim() : "No course context available.";

    try {
        const response = await fetch(apiUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                model: "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", // Free model
                messages: [
                    { role: "system", content: `You are a helpful AI assistant. Use the following course materials as context for your responses:\n\n${courseContext}` },
                    ...conversationHistory // Include full conversation history
                ],
                max_tokens: 200,
                temperature: 0.7,
                top_p: 0.7,
                top_k: 50,
                repetition_penalty: 1,
                stop: ["<|eot_id|>", "<|eom_id|>"]
            })
        });

        const data = await response.json();
        hideTypingIndicator();

        if (data.choices && data.choices.length > 0) {
            const botMessage = data.choices[0].message.content;
            addMessage(botMessage); // Display the bot's message

            // Add the bot's message to conversation history
            conversationHistory.push({ role: "assistant", content: botMessage });
        } else {
            addMessage("Sorry, I couldn't process that.");
        }
    } catch (error) {
        hideTypingIndicator();
        addMessage("Error reaching AI server. Please try again later.");
        console.error("Error:", error);
    }
}

function handleSendMessage() {
    const message = messageInput.value.trim();
    if (!message) return; // Prevent empty messages

    // Add user's message to the chat interface
    addMessage(message, true);

    messageInput.value = '';
    getBotResponse(message);
}

sendButton.addEventListener('click', handleSendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleSendMessage();
    }
});

// Initial welcome message
setTimeout(() => {
    addMessage("Hello! I'm your AI doubt solver, how can I help you?");
}, 500);