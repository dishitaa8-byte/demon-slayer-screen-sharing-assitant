/**
 * FRIDAY - AI Desktop Assistant
 * Frontend Application Logic
 * 
 * Handles:
 * - Chat interface interactions
 * - Vision analysis (screen capture and analysis)
 * - Image upload functionality
 * - Chat clearing
 * - Status management
 * - Notification system
 * - API communication with Flask backend
 */

// DOM Elements
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const uploadImageButton = document.getElementById('uploadImageButton');
const captureButton = document.getElementById('captureButton');
const clearChatButton = document.getElementById('clearChatButton');
const imageUpload = document.getElementById('imageUpload');
const chatMessages = document.getElementById('chatMessages');
const filePreview = document.getElementById('filePreview');
const fileName = document.getElementById('fileName');
const removeFile = document.getElementById('removeFile');
const loadingOverlay = document.getElementById('loadingOverlay');
const notificationContainer = document.getElementById('notificationContainer');



// State
let currentImage = null;

// ============================================
// Notification System
// ============================================

/**
 * Show a notification
 * @param {string} type - 'error', 'warning', or 'success'
 * @param {string} title - Notification title
 * @param {string} message - Notification message
 */
function showNotification(type, title, message) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    // Icon based on type
    let iconSvg = '';
    if (type === 'error') {
        iconSvg = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
        `;
    } else if (type === 'warning') {
        iconSvg = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
        `;
    } else {
        iconSvg = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
        `;
    }
    
    notification.innerHTML = `
        <div class="notification-icon">
            ${iconSvg}
        </div>
        <div class="notification-content">
            <p class="notification-title">${escapeHtml(title)}</p>
            <p class="notification-message">${escapeHtml(message)}</p>
        </div>
        <button class="notification-close">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
        </button>
    `;
    
    // Add close button functionality
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        hideNotification(notification);
    });
    
    // Auto-hide after 5 seconds
    const autoHide = setTimeout(() => {
        hideNotification(notification);
    }, 5000);
    
    notificationContainer.appendChild(notification);
}

/**
 * Hide a notification with animation
 */
function hideNotification(notification) {
    notification.classList.add('hiding');
    notification.addEventListener('animationend', () => {
        notification.remove();
    });
}

// ============================================
// Status Management
// ============================================

/**
 * Update status indicator
 * @param {string} statusId - ID of status element
 * @param {string} status - 'online', 'offline', or 'warning'
 * @param {string} text - Status text
 */
function updateStatus(statusId, status, text) {
    const statusElement = document.getElementById(statusId);
    if (!statusElement) return;
    
    const indicator = statusElement.querySelector('.status-indicator');
    const textElement = statusElement.querySelector('.status-text');
    
    // Remove all status classes
    indicator.classList.remove('status-online', 'status-offline', 'status-warning');
    
    // Add new status class
    indicator.classList.add(`status-${status}`);
    
    // Update text if provided
    if (text) {
        textElement.textContent = text;
    }
}

// ============================================
// Chat Functions
// ============================================

/**
 * Send a message to the chat API
 */
async function sendMessage() {
    const message = messageInput.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessage(message, 'user');
    
    // Clear input
    messageInput.value = '';
    updateSendButton();
    
    // Disable send button
    sendButton.disabled = true;
    let loadingMessage;
    try {
        // Create loading message element directly without typing animation
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant-message';
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 4c1.1 0 2 .9 2 2s-.9 2-2 2-2-.9-2-2 .9-2 2-2zm4 0c1.1 0 2 .9 2 2s-.9 2-2 2-2-.9-2-2 .9-2 2-2zm-2 6c-1.66 0-3-1.34-3-3h6c0 1.66-1.34 3-3 3z"/>
            </svg>
        `;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = `
            <p class="message-sender">Kasugai Crow</p>
            <p class="message-text">Kasugai Crows are gathering information...</p>
        `;
        
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        loadingMessage = messageDiv;
        
        console.log("Before fetch");
        
        // Send to API
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });

        console.log("After fetch");
        
        const data = await response.json();
        
        console.log(data);
        
        if (response.ok) {
            // Remove the temporary loading message
            loadingMessage.remove();

            // Show the real response
            addMessage(data.response, 'assistant');
        } else {
            // Remove loading message if there was an error
            loadingMessage.remove();

            showNotification('error', 'Chat Error', data.error);
        }
    } catch (error) {
        console.log(error); 
        if(loadingMessage){
            loadingMessage.remove();
        }
        showNotification(
            'error',
            'Network Error',
            'Failed to connect to the server. Please check your connection.'
        );
    } finally {
        // Re-enable send button
        sendButton.disabled = false;
        messageInput.focus();
    }
}

/**
 * Add a message to the chat interface
 */
function addMessage(content, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;
    
    // Add avatar for assistant messages
    if (type === 'assistant') {
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 4c1.1 0 2 .9 2 2s-.9 2-2 2-2-.9-2-2 .9-2 2-2zm4 0c1.1 0 2 .9 2 2s-.9 2-2 2-2-.9-2-2 .9-2 2-2zm-2 6c-1.66 0-3-1.34-3-3h6c0 1.66-1.34 3-3 3z"/>
            </svg>
        `;
        messageDiv.appendChild(avatarDiv);
    }
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (type === 'assistant') {
        contentDiv.innerHTML = `
            <p class="message-sender">Kasugai Crow</p>
            <p class="message-text"></p>
        `;
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        
        // Typing animation for assistant messages
        typeMessage(contentDiv.querySelector('.message-text'), content);
    } else {
        contentDiv.innerHTML = `<p class="message-text">${escapeHtml(content)}</p>`;
        messageDiv.appendChild(contentDiv);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom immediately for user messages
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    return messageDiv;
}

/**
 * Type message character by character with animation
 * @param {HTMLElement} element - The element to type into
 * @param {string} text - The text to type
 */
function typeMessage(element, text) {
    let index = 0;
    const speed = 15; // milliseconds per character
    
    function type() {
        if (index < text.length) {
            element.textContent += text.charAt(index);
            index++;
            chatMessages.scrollTop = chatMessages.scrollHeight;
            setTimeout(type, speed);
        }
    }
    
    type();
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Clear chat history
 */
function clearChat() {
    // Keep only the welcome message
    chatMessages.innerHTML = `
        <div class="message assistant-message">
            <div class="message-avatar">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 4c1.1 0 2 .9 2 2s-.9 2-2 2-2-.9-2-2 .9-2 2-2zm4 0c1.1 0 2 .9 2 2s-.9 2-2 2-2-.9-2-2 .9-2 2-2zm-2 6c-1.66 0-3-1.34-3-3h6c0 1.66-1.34 3-3 3z"/>
                </svg>
            </div>
            <div class="message-content">
                <p class="message-sender">Kasugai Crow</p>
                <p class="message-text">Greetings. I am the Kasugai Crow, your AI assistant. How may I assist you today?</p>
            </div>
        </div>
    `;
}

/**
 * Update send button state based on input
 */
function updateSendButton() {
    const hasText = messageInput.value.trim().length > 0;
    sendButton.disabled = !hasText;
}

// ============================================
// Vision Functions
// ============================================

/**
 * Capture screen and analyze it
 */
async function captureAndAnalyze() {
    captureButton.classList.add('loading');

    try {
        // Ask browser to share the screen
        const stream = await navigator.mediaDevices.getDisplayMedia({
            video: true
        });

        // Create video element
        const video = document.createElement('video');
        video.srcObject = stream;

        await video.play();

        // Draw one frame to canvas
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);

        // Stop sharing immediately
        stream.getTracks().forEach(track => track.stop());

        // Convert image to Base64
        const image = canvas.toDataURL('image/png');

        // Ask the user what they want to know
        const question = prompt("What would you like to know about this screen?");

        if (!question || !question.trim()) {
            return;
        }

        // Send image directly to backend
        const analyzeResponse = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image: image,
                question: question.trim()
            })
        });

        const analyzeData = await analyzeResponse.json();

        if (analyzeResponse.ok) {
            addMessage(
                `Screen Analysis: ${analyzeData.analysis}`,
                "assistant"
            );
        } else {
            showNotification(
                "error",
                "Analysis Failed",
                analyzeData.error
            );
        }

    } catch (err) {
        console.error(err);

        showNotification(
            "error",
            "Capture Failed",
            err.message
        );
    } finally {
        captureButton.classList.remove("loading");
    }
}
/**
 * Handle image upload
 */
function handleImageUpload() {
    imageUpload.click();
}

/**
 * Process uploaded image
 */
imageUpload.addEventListener('change', function(e) {
    const file = e.target.files[0];
    
    if (!file) return;
    
    // Show file preview
    fileName.textContent = file.name;
    filePreview.style.display = 'flex';
    
    const reader = new FileReader();
    
    reader.onload = function(event) {
        const imageBase64 = event.target.result;
        currentImage = imageBase64;
        
        // Ask for question
        const question = prompt('What would you like to know about this image?');
        
        if (question && question.trim()) {
            // Analyze the image
            analyzeImage(imageBase64, question.trim());
        }
    };
    
    reader.readAsDataURL(file);
    
    // Reset input
    imageUpload.value = '';
});

/**
 * Remove file preview
 */
function removeFilePreview() {
    filePreview.style.display = 'none';
    fileName.textContent = '';
    currentImage = null;
    imageUpload.value = '';
}

/**
 * Analyze uploaded image
 */
async function analyzeImage(imageBase64, question) {
    showLoading();
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image: imageBase64,
                question: question
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            addMessage(`Image Analysis: ${data.analysis}`, 'assistant');
            removeFilePreview();
        } else {
            showNotification('error', 'Analysis Failed', data.error);
        }
    } catch (error) {
        showNotification('error', 'Network Error', 'Failed to connect to the server. Please check your connection.');
    } finally {
        hideLoading();
    }
}

// ============================================
// Loading Functions
// ============================================

/**
 * Show loading overlay
 */
function showLoading() {
    loadingOverlay.classList.add('active');
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    loadingOverlay.classList.remove('active');
}

// ============================================
// Event Listeners
// ============================================

// Chat input
sendButton.addEventListener('click', sendMessage);

messageInput.addEventListener('input', updateSendButton);

messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// New buttons
captureButton.addEventListener('click', captureAndAnalyze);
uploadImageButton.addEventListener('click', handleImageUpload);
clearChatButton.addEventListener('click', clearChat);
removeFile.addEventListener('click', removeFilePreview);

// ============================================
// Initialization
// ============================================

// Focus on message input on load
messageInput.focus();
updateSendButton();
