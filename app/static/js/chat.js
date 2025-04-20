// Initialize variables
let isProcessing = false;
let currentBatchStart = 0;
let analysisTable = [];

// Function to show loading state
function showLoading(message = 'Processing...') {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message loading-message';
    loadingDiv.innerHTML = `
        <div class="message-content">
            <div class="spinner-border spinner-border-sm" role="status">
            </div>
            <span class="ms-2">${message}</span>
        </div>
    `;
    return loadingDiv;
}

// Function to clean up message formatting
function cleanMessageFormat(content) {
    return content
        // First clean up the markdown formatting
        .replace(/\* \*\*"([^"]+)"\*\*/g, '"$1"')  // Remove * **"text"**
        .replace(/\* \*\*([^*]+)\*\*/g, '$1')      // Remove * **text**
        .replace(/\*\*([^*]+)\*\*/g, '$1')         // Remove **text**
        .replace(/\*/g, '')                        // Remove remaining single asterisks
        // Handle paragraph spacing
        .split(/\n/)                               // Split into lines
        .map(line => line.trim())                  // Trim each line
        .filter(line => line.length > 0)           // Remove empty lines
        .join('\n\n')                             // Join with double line breaks
        .trim();
}

// Function to get appropriate emojis based on message content and sentiment
function getMessageEmojis(text, sentiment = null) {
    // Default emojis for greetings
    if (text.toLowerCase().includes('hello') || text.toLowerCase().includes('hi')) {
        return '👋 ';
    }
    
    // Emojis for sentiment analysis discussions
    if (text.includes('sentiment analysis') || text.includes('analyzed content')) {
        return '📊 ';
    }
    
    // Emojis for statistics or percentages
    if (text.match(/\d+(\.\d+)?%/) || text.includes('majority') || text.includes('proportion')) {
        return '📈 ';
    }
    
    // Emojis based on sentiment if provided
    if (sentiment) {
        switch(sentiment.toLowerCase()) {
            case 'positive':
                return '😊 ';
            case 'negative':
                return '😔 ';
            case 'neutral':
                return '😐 ';
        }
    }
    
    // Emojis for specific content types
    if (text.includes('looking at') || text.includes('we can see')) {
        return '🔍 ';
    }
    if (text.includes('important to note')) {
        return '📝 ';
    }
    if (text.includes('example')) {
        return '💡 ';
    }
    if (text.includes('suggest') || text.includes('recommendation')) {
        return '💭 ';
    }
    
    // Default emoji for other messages
    return '🤖 ';
}

// Function to format the message with paragraphs and emojis
function formatMessage(text, sentiment = null) {
    // Split into paragraphs and add emojis
    const paragraphs = text.split('\n\n').filter(p => p.trim().length > 0);
    
    return paragraphs.map((paragraph, index) => {
        // Only add emoji to the first paragraph or if it's a new thought
        const shouldAddEmoji = index === 0 || 
            paragraph.includes('However') || 
            paragraph.includes('Looking at') ||
            paragraph.includes('Based on');
            
        const emoji = shouldAddEmoji ? getMessageEmojis(paragraph, sentiment) : '';
        return `<p>${emoji}${paragraph.trim()}</p>`;
    }).join('');
}

// Function to append a message to the chat
function appendMessage(sender, message) {
    const messagesContainer = document.querySelector('.chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (sender === 'user') {
        contentDiv.innerHTML = `<p>👤 ${message}</p>`;
    } else {
        // Clean up the message format and handle line breaks
        const cleanedMessage = cleanMessageFormat(message);
        contentDiv.innerHTML = formatMessage(cleanedMessage);
    }
    
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Function to format the reason text
function formatReason(reason, sentiment, confidence) {
    if (!reason) return '';
    
    // Extract the tweet text from the reason if available
    const tweetMatch = reason.match(/"([^"]+)"/);
    const tweet = tweetMatch ? tweetMatch[1] : '';
    
    // Format confidence as percentage
    const confidencePercent = confidence.toFixed(2);
    
    // Create a concise explanation
    let explanation = `Why the tweet "${tweet}" was classified as ${sentiment.toLowerCase()} with ${confidencePercent}% confidence. `;
    
    // Clean up the text and extract key points
    let mainText = reason
        .replace(/\*\*/g, '')
        .replace(/\*[^*]+\*/g, '')
        .replace(/Let's break down[^:]+:/g, '')
        .replace(/Key Words and Phrases:/g, '')
        .replace(/Overall Tone:/g, '')
        .replace(/Context Clues:/g, '')
        .replace(/In Summary:/g, '')
        .split(/[.!?]+/)
        .filter(s => s.trim().length > 0)
        .map(s => s.trim())
        .filter(s => 
            !s.startsWith('Let\'s break') && 
            !s.includes('requested points') && 
            !s.includes('requested elements') &&
            !s.includes('was classified as') && // Remove repeated classification statements
            s.length > 10
        );
    
    // Remove duplicate sentences
    mainText = [...new Set(mainText)];
    
    // Join all unique, relevant sentences
    let keyPoints = mainText.join('. ');
    
    // Ensure proper ending punctuation
    if (keyPoints && !keyPoints.endsWith('.')) {
        keyPoints += '.';
    }
    
    return explanation + keyPoints;
}

// Function to update the analysis table
function updateAnalysisTable(analyses, isNewBatch = true) {
    const tableBody = document.querySelector('#detailedAnalysisTable tbody');
    if (!tableBody) return;
    
    // Clear existing rows if this is a new batch
    if (isNewBatch) {
        tableBody.innerHTML = '';
    }
    
    // Add new rows to the table
    analyses.forEach(analysis => {
        const row = document.createElement('tr');
        const sentimentClass = `sentiment-${(analysis.sentiment || '').toLowerCase()}`;
        const confidenceScore = parseFloat(analysis.confidence || analysis.score || 0);
        const confidencePercent = confidenceScore.toFixed(2);
        const commentText = analysis.comment || analysis.text || 'No comment available';
        const formattedReason = formatReason(analysis.reason, analysis.sentiment, confidenceScore);
        
        row.innerHTML = `
            <td class="text-cell">${commentText}</td>
            <td class="sentiment-cell">
                <span class="sentiment-badge ${sentimentClass}">
                    ${analysis.sentiment || 'Unknown'}
                </span>
            </td>
            <td class="score-cell">
                <div class="confidence-wrapper">
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${confidencePercent}%"></div>
                    </div>
                    <div class="confidence-value">${confidencePercent}%</div>
                </div>
            </td>
            <td class="reason-cell">
                ${formattedReason || '<div class="loading-reason"><div class="mini-loader"></div></div>'}
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

// Function to get detailed analysis for a batch
async function getDetailedAnalysis(batchStart = 0) {
    if (isProcessing) return;
    let data = null;
    
    try {
        isProcessing = true;
        
        // Show loading state in modal footer
        const modalFooter = document.querySelector('.modal-footer');
        const viewMoreBtn = modalFooter.querySelector('.view-more-btn');
        if (viewMoreBtn) {
            viewMoreBtn.disabled = true;
            viewMoreBtn.innerHTML = '<div class="mini-loader"></div>';
        }
        
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: 'detailed_analysis',
                batch_start: batchStart
            })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        data = await response.json();
        
        if (data.data && data.data.length > 0) {
            // Update table with new batch
            updateAnalysisTable(data.data, batchStart === 0);
            
            // Update view more button
            updateViewMoreButton(data.metadata);
        }
        
    } catch (error) {
        console.error('Error:', error);
        const modalBody = document.querySelector('.modal-body');
        modalBody.innerHTML = '<div class="error-message">Error loading analyses. Please try again.</div>';
    } finally {
        isProcessing = false;
        
        // Reset view more button state
        const viewMoreBtn = document.querySelector('.view-more-btn');
        if (viewMoreBtn) {
            viewMoreBtn.disabled = false;
            viewMoreBtn.textContent = `View More (${data?.metadata?.remaining || 0})`;
        }
    }
}

// Function to update the view more button
function updateViewMoreButton(metadata) {
    const modalFooter = document.querySelector('.modal-footer');
    let viewMoreBtn = modalFooter.querySelector('.view-more-btn');
    
    if (metadata?.has_more) {
        if (!viewMoreBtn) {
            viewMoreBtn = document.createElement('button');
            viewMoreBtn.className = 'view-more-btn';
            modalFooter.appendChild(viewMoreBtn);
        }
        
        viewMoreBtn.textContent = `View More (${metadata.remaining} remaining)`;
        viewMoreBtn.onclick = () => getDetailedAnalysis(metadata.batch_end);
        viewMoreBtn.style.display = 'block';
    } else if (viewMoreBtn) {
        viewMoreBtn.style.display = 'none';
    }
}

// Function to show the detailed analysis modal
function showDetailedAnalysis() {
    const modal = document.getElementById('detailedAnalysisModal');
    if (!modal) return;
    
    // Reset the table and batch counter
    currentBatchStart = 0;
    
    // Show the modal
    modal.style.display = 'block';
    
    // Start loading the first batch
    getDetailedAnalysis(0);
}

// Initialize event listeners when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Hamburger menu toggle
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            // Toggle active class for animation
            this.classList.toggle('active');
            navbarCollapse.classList.toggle('show');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!navbarToggler.contains(event.target) && !navbarCollapse.contains(event.target)) {
                navbarCollapse.classList.remove('show');
                navbarToggler.classList.remove('active');
            }
        });
    }

    // Chat form submission
    const chatForm = document.getElementById('chatForm');
    if (chatForm) {
        chatForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            if (isProcessing) return;
            
            const messageInput = document.getElementById('messageInput');
            const message = messageInput.value.trim();
            
            if (!message) return;
            
            try {
                isProcessing = true;
                messageInput.value = '';
                appendMessage('user', message);
                
                const loadingMessage = showLoading();
                document.querySelector('.chat-messages').appendChild(loadingMessage);
                
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: message,
                        type: 'general'
                    })
                });
                
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                
                const data = await response.json();
                loadingMessage.remove();
                
                if (data.error) {
                    appendMessage('assistant', 'Error: ' + data.error);
                } else {
                    appendMessage('assistant', data.response);
                }
                
            } catch (error) {
                console.error('Error:', error);
                loadingMessage?.remove();
                appendMessage('assistant', 'Sorry, I encountered an error. Please try again.');
            } finally {
                isProcessing = false;
            }
        });
    }
    
    // View Detailed Analysis button
    const viewDetailedAnalysisBtn = document.getElementById('viewDetailedAnalysis');
    if (viewDetailedAnalysisBtn) {
        viewDetailedAnalysisBtn.addEventListener('click', showDetailedAnalysis);
    }
    
    // Modal close button
    const closeBtn = document.querySelector('.close');
    if (closeBtn) {
        closeBtn.addEventListener('click', function() {
            const modal = document.getElementById('detailedAnalysisModal');
            if (modal) {
                modal.style.display = 'none';
            }
        });
    }
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('detailedAnalysisModal');
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}); 