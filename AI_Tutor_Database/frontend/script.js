
// Select the hamburger button and sidebar
const hamburgerButton = document.querySelector('.hamburger-button');
const sidebar = document.querySelector('.sidebar-div');

// Add event listener to toggle sidebar
hamburgerButton.addEventListener('click', () => {
    if (sidebar.style.marginLeft === '0px') {
        sidebar.style.marginLeft = '-250px'; // Hide the sidebar
    } else {
        sidebar.style.marginLeft = '0px'; // Show the sidebar
    }
});

// When the document is loaded, fetch the syllabus
document.addEventListener("DOMContentLoaded", function () {
    fetchSyllabus();
});

function fetchSyllabus() {
    fetch("http://127.0.0.1:5000/api/syllabus") // Fetch from Flask API
        .then(response => response.json())
        .then(data => {
            displaySyllabus(data);
        })
        .catch(error => console.error("Error fetching syllabus:", error));
}

function displaySyllabus(syllabus) {
    const syllabusDiv = document.querySelector(".syllabus-div");
    syllabusDiv.innerHTML = ""; // Clear existing content

    syllabus.forEach(course => {
        let courseElement = document.createElement("div");
        courseElement.innerHTML = `<h2>${course.course_title} (${course.course_code})</h2>`;

        course.modules.forEach(module => {
            let moduleElement = document.createElement("div");
            moduleElement.innerHTML = `<h3>${module.module_title} - ${module.duration}</h3>`;

            // Add 'Questions' link
            let questionsLink = document.createElement("a");
            questionsLink.href = "#";
            questionsLink.textContent = "Questions";
            questionsLink.style.marginRight = "10px"; // Optional: Add some spacing
            questionsLink.addEventListener("click", function (event) {
                event.preventDefault();
                showModuleQuestions(module);
            });

            moduleElement.appendChild(questionsLink);

            // Existing code to render topics
            let topicList = document.createElement("ul");
            module.topics.forEach(topic => {
                let topicItem = document.createElement("li");

                // Create a clickable hyperlink for each topic
                let topicLink = document.createElement("a");
                topicLink.href = "#";
                topicLink.textContent = `${topic.title} (${topic.time} hrs)`;
                topicLink.addEventListener("click", function (event) {
                    event.preventDefault();
                    showTopicContent(topic);
                });

                topicItem.appendChild(topicLink);
                topicList.appendChild(topicItem);
            });

            moduleElement.appendChild(topicList);
            courseElement.appendChild(moduleElement);
        });

        syllabusDiv.appendChild(courseElement);
    });
}

function showTopicContent(topic) {
    const syllabusDiv = document.querySelector(".syllabus-div");
    syllabusDiv.innerHTML = ""; // Clear syllabus content

    // Create a new section for topic content
    let topicContentDiv = document.createElement("div");
    let formattedContent = marked.parse(topic.content);
    topicContentDiv.innerHTML = `
    <h2>${topic.title}</h2>
    <div class="topic-content">${formattedContent}</div>
    <button id="backButton">Back to Syllabus</button>
  `;

    syllabusDiv.appendChild(topicContentDiv);

    // Add event listener to the back button
    document.getElementById("backButton").addEventListener("click", function () {
        fetchSyllabus();
    });
}

// New function to display module questions
function showModuleQuestions(module) {
    // Fetch the questions for the module
    fetch(`http://127.0.0.1:5000/api/modules/${module.id}/questions`)
        .then(response => response.json())
        .then(questions => {
            displayModuleQuestions(questions, module);
        })
        .catch(error => {
            console.error("Error fetching module questions:", error);
        });
}

function displayModuleQuestions(questions, module) {
    const syllabusDiv = document.querySelector(".syllabus-div");
    syllabusDiv.innerHTML = ""; // Clear syllabus content

    // Create a new section for questions
    let questionsContentDiv = document.createElement("div");

    let questionsMarkup = questions.map((question, index) => {
        return `<div class="question">
              <h3>Question ${index + 1}</h3>
              ${marked.parse(question)}
            </div>`;
    }).join('<hr>'); // Add a horizontal line between questions

    questionsContentDiv.innerHTML = `
    <h2>Questions for ${module.module_title}</h2>
    <div class="questions-content">${questionsMarkup}</div>
    <button id="backButton">Back to Syllabus</button>
  `;

    syllabusDiv.appendChild(questionsContentDiv);

    // Add event listener to the back button
    document.getElementById("backButton").addEventListener("click", function () {
        fetchSyllabus();
    });
}


const uploadButton = document.getElementById('uploadButton');
const syllabusUpload = document.getElementById('syllabusUpload');

// Trigger file input when the upload button is clicked
uploadButton.addEventListener("click", () => {
    syllabusUpload.click();
});

// Handle file selection
syllabusUpload.addEventListener("change", () => {
    if (syllabusUpload.files.length === 0) return;

    const file = syllabusUpload.files[0];
    const formData = new FormData();
    formData.append("file", file);

    fetch("http://127.0.0.1:5000/api/upload-syllabus", {
        method: "POST",
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Syllabus uploaded successfully!");
                fetchSyllabus(); // Reload syllabus view
            } else {
                alert("Error: " + data.error);
            }
        })
        .catch(error => {
            console.error("Upload error:", error);
            alert("Error uploading syllabus.");
        });
});

// Fetch syllabus when the page loads
function fetchSyllabus() {
    fetch("http://127.0.0.1:5000/api/syllabus")
        .then(response => response.json())
        .then(data => {
            displaySyllabus(data);
        })
        .catch(error => console.error("Error fetching syllabus:", error));
}






// const themeToggle = document.querySelector('.theme-toggle');
// const body = document.body;
// const chatContainer = document.getElementById('chatContainer');
// const messageInput = document.querySelector('.message-input');
// const sendButton = document.querySelector('.send-button');
// const typingIndicator = document.querySelector('.typing-indicator');

// // Theme toggling
// let isDarkTheme = false;
// themeToggle.addEventListener('click', () => {
//     isDarkTheme = !isDarkTheme;
//     body.setAttribute('data-theme', isDarkTheme ? 'dark' : 'light');
//     themeToggle.innerHTML = isDarkTheme ?
//         '<i class="fas fa-sun"></i>' :
//         '<i class="fas fa-moon"></i>';
// });

// // Chat functionality
// function createMessageElement(content, isUser = false) {
//     const messageDiv = document.createElement('div');
//     messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;

//     messageDiv.innerHTML = `
//         <div class="avatar">${isUser ? 'U' : 'AI'}</div>
//         <div class="message-bubble">${content}</div>
//     `;

//     return messageDiv;
// }

// function addMessage(content, isUser = false) {
//     const messageElement = createMessageElement(content, isUser);
//     chatContainer.appendChild(messageElement);
//     chatContainer.scrollTop = chatContainer.scrollHeight;
// }

// function showTypingIndicator() {
//     typingIndicator.style.display = 'block';
//     chatContainer.scrollTop = chatContainer.scrollHeight;
// }

// function hideTypingIndicator() {
//     typingIndicator.style.display = 'none';
// }

// function simulateBotResponse(userMessage) {
//     showTypingIndicator();
//     // Simulate varying response times
//     setTimeout(() => {
//         hideTypingIndicator();
//         const responses = [
//             "I understand you're asking about " + userMessage + ". Could you elaborate?",
//             "That's an interesting point about " + userMessage + ". Let me help you with that.",
//             "I've analyzed your message about " + userMessage + ". Here's what I think..."
//         ];
//         const randomResponse = responses[Math.floor(Math.random() * responses.length)];
//         addMessage(randomResponse);
//     }, Math.random() * 1000 + 1500);
//     // // Make API call to Flask backend for Gemini AI response
//     // fetch('http://127.0.0.1:5000/api/chat', {
//     //     method: 'POST',
//     //     headers: {
//     //         'Content-Type': 'application/json'
//     //     },
//     //     body: JSON.stringify({ message: userMessage })
//     // })
//     // .then(response => response.json())
//     // .then(data => {
//     //     hideTypingIndicator();
//     //     addMessage(data.ai_response);  // Display Gemini AI's response
//     // })
//     // .catch(error => {
//     //     hideTypingIndicator();
//     //     addMessage("Sorry, I couldn't process that.");
//     //     console.error('Error:', error);
//     // });
// }

// function handleSendMessage() {
//     const message = messageInput.value.trim();
//     if (message) {
//         addMessage(message, true);
//         messageInput.value = '';
//         simulateBotResponse(message);
//     }
// }

// sendButton.addEventListener('click', handleSendMessage);
// messageInput.addEventListener('keypress', (e) => {
//     if (e.key === 'Enter') {
//         handleSendMessage();
//     }
// });

// setTimeout(() => {
//     addMessage("Hello! I'm your AI assistant. How can I help you today?");
// }, 500);
