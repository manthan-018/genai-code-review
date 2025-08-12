// Global utility functions
function showLoading(show) {
    const loading = document.getElementById('loading');
    if (loading) {
        if (show) {
            loading.classList.add('show');
            // Reset loading message
            const loadingText = loading.querySelector('.loading-spinner p');
            if (loadingText) {
                loadingText.textContent = 'AI is analyzing your code...';
            }
        } else {
            loading.classList.remove('show');
        }
    }
}

function showMessage(message, type = 'success') {
    const messageEl = document.getElementById('message');
    if (messageEl) {
        messageEl.textContent = message;
        messageEl.className = `message ${type}`;
        messageEl.classList.add('show');
        
        setTimeout(() => {
            messageEl.classList.remove('show');
        }, 4000);
    }
}

// Code editor functionality
function initCodeEditor() {
    const codeTextarea = document.getElementById('codeInput');
    if (codeTextarea) {
        // Add line numbers and syntax highlighting
        codeTextarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
        
        // Tab key support
        codeTextarea.addEventListener('keydown', function(e) {
            if (e.key === 'Tab') {
                e.preventDefault();
                const start = this.selectionStart;
                const end = this.selectionEnd;
                
                this.value = this.value.substring(0, start) + '    ' + this.value.substring(end);
                this.selectionStart = this.selectionEnd = start + 4;
            }
        });
    }
}

// Review code functionality
async function reviewCode() {
    const code = document.getElementById('codeInput').value.trim();
    const language = document.getElementById('languageSelect').value;
    const title = document.getElementById('titleInput').value.trim() || 'Code Review';
    
    if (!code) {
        showMessage('Please enter some code to review', 'error');
        return;
    }
    
    // Show faster loading messages
    const loadingMessages = [
        'Initializing AI analysis...',
        'Processing your code...',
        'Generating insights...',
        'Almost done...'
    ];
    
    let messageIndex = 0;
    const loadingInterval = setInterval(() => {
        const loadingText = document.querySelector('.loading-spinner p');
        if (loadingText && messageIndex < loadingMessages.length) {
            loadingText.textContent = loadingMessages[messageIndex];
            messageIndex++;
        }
    }, 1500);
    
    try {
        showLoading(true);
        
        const startTime = Date.now();
        const response = await fetch('/api/review-code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                code: code,
                language: language,
                title: title
            })
        });
        
        const result = await response.json();
        const processingTime = ((Date.now() - startTime) / 1000).toFixed(1);
        
        clearInterval(loadingInterval);
        
        if (result.success) {
            displayReviewResult(result.review);
            showMessage(`Code review completed in ${processingTime}s!`, 'success');
        } else {
            showMessage(result.error || 'Failed to review code', 'error');
        }
    } catch (error) {
        clearInterval(loadingInterval);
        showMessage('An error occurred while reviewing code', 'error');
        console.error('Error:', error);
    } finally {
        showLoading(false);
    }
}

// Debug code functionality
async function debugCode() {
    const code = document.getElementById('codeInput').value.trim();
    const error = document.getElementById('errorInput').value.trim();
    const language = document.getElementById('languageSelect').value;
    
    if (!code) {
        showMessage('Please enter some code to debug', 'error');
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch('/api/debug-code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                code: code,
                error: error,
                language: language
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayDebugResult(result.debug_result);
            showMessage('Debug analysis completed!', 'success');
        } else {
            showMessage(result.error || 'Failed to debug code', 'error');
        }
    } catch (error) {
        showMessage('An error occurred while debugging code', 'error');
        console.error('Error:', error);
    } finally {
        showLoading(false);
    }
}

// Display review result
function displayReviewResult(reviewText) {
    const resultContainer = document.getElementById('reviewResult');
    if (!resultContainer) return;
    
    try {
        // Try to parse as JSON first
        const review = JSON.parse(reviewText);
        
        let html = `
            <div class="review-summary">
                <div class="rating">
                    <span class="rating-label">Overall Rating:</span>
                    <div class="rating-stars">
                        ${generateStars(review.overall_rating || 0)}
                        <span class="rating-number">${review.overall_rating || 'N/A'}/10</span>
                    </div>
                </div>
                <p class="summary">${review.summary || 'No summary available'}</p>
            </div>
        `;
        
        if (review.issues && review.issues.length > 0) {
            html += `
                <div class="review-section">
                    <h3><i class="fas fa-exclamation-triangle"></i> Issues Found</h3>
                    <ul class="issue-list">
                        ${review.issues.map(issue => `<li>${issue}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        if (review.suggestions && review.suggestions.length > 0) {
            html += `
                <div class="review-section">
                    <h3><i class="fas fa-lightbulb"></i> Suggestions</h3>
                    <ul class="suggestion-list">
                        ${review.suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        if (review.security_notes && review.security_notes.length > 0) {
            html += `
                <div class="review-section">
                    <h3><i class="fas fa-shield-alt"></i> Security Notes</h3>
                    <ul class="security-list">
                        ${review.security_notes.map(note => `<li>${note}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        if (review.performance_tips && review.performance_tips.length > 0) {
            html += `
                <div class="review-section">
                    <h3><i class="fas fa-rocket"></i> Performance Tips</h3>
                    <ul class="performance-list">
                        ${review.performance_tips.map(tip => `<li>${tip}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        resultContainer.innerHTML = html;
    } catch (e) {
        // If not JSON, display as plain text
        resultContainer.innerHTML = `
            <div class="review-text">
                <pre>${reviewText}</pre>
            </div>
        `;
    }
    
    resultContainer.style.display = 'block';
    resultContainer.scrollIntoView({ behavior: 'smooth' });
}

// Display debug result
function displayDebugResult(debugText) {
    const resultContainer = document.getElementById('debugResult');
    if (!resultContainer) return;
    
    try {
        const debug = JSON.parse(debugText);
        
        let html = `
            <div class="debug-section">
                <h3><i class="fas fa-info-circle"></i> Issue Explanation</h3>
                <p>${debug.issue_explanation || 'No explanation available'}</p>
            </div>
        `;
        
        if (debug.fixed_code) {
            html += `
                <div class="debug-section">
                    <h3><i class="fas fa-code"></i> Fixed Code</h3>
                    <pre><code class="language-${document.getElementById('languageSelect').value}">${debug.fixed_code}</code></pre>
                </div>
            `;
        }
        
        if (debug.fix_explanation) {
            html += `
                <div class="debug-section">
                    <h3><i class="fas fa-wrench"></i> Fix Explanation</h3>
                    <p>${debug.fix_explanation}</p>
                </div>
            `;
        }
        
        if (debug.prevention_tips && debug.prevention_tips.length > 0) {
            html += `
                <div class="debug-section">
                    <h3><i class="fas fa-shield-alt"></i> Prevention Tips</h3>
                    <ul>
                        ${debug.prevention_tips.map(tip => `<li>${tip}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        resultContainer.innerHTML = html;
    } catch (e) {
        resultContainer.innerHTML = `
            <div class="debug-text">
                <pre>${debugText}</pre>
            </div>
        `;
    }
    
    resultContainer.style.display = 'block';
    resultContainer.scrollIntoView({ behavior: 'smooth' });
    
    // Re-initialize Prism for syntax highlighting
    if (typeof Prism !== 'undefined') {
        Prism.highlightAll();
    }
}

// Generate star rating
function generateStars(rating, mini = false) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;
    let stars = '';
    const starClass = mini ? 'mini-star' : '';
    
    for (let i = 0; i < fullStars; i++) {
        stars += `<i class="fas fa-star ${starClass}"></i>`;
    }
    
    if (hasHalfStar) {
        stars += `<i class="fas fa-star-half-alt ${starClass}"></i>`;
    }
    
    const emptyStars = 10 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
        stars += `<i class="far fa-star ${starClass}"></i>`;
    }
    
    return stars;
}

// Clear results
function clearResults() {
    const reviewResult = document.getElementById('reviewResult');
    const debugResult = document.getElementById('debugResult');
    
    if (reviewResult) reviewResult.style.display = 'none';
    if (debugResult) debugResult.style.display = 'none';
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initCodeEditor();
    
    // Add smooth scrolling to all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});

// Export functions for global use
window.reviewCode = reviewCode;
window.debugCode = debugCode;
window.clearResults = clearResults;
window.analyzeCode = analyzeCode;
window.quickReview = quickReview;