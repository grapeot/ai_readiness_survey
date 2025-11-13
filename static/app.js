// Survey application main logic
let questions = [];
let currentQuestionIndex = 0;
let answers = {};

// Initialize application
async function init() {
    try {
        // Load question list
        const response = await fetch('/api/questions');
        const data = await response.json();
        questions = data.questions;
        
        // Initialize answer object
        questions.forEach(q => {
            if (q.is_open) {
                answers[q.id] = '';
            } else {
                answers[q.id] = null;
            }
        });
        
        // Show first question
        showQuestion(0);
    } catch (error) {
        console.error('Initialization failed:', error);
        alert('Failed to load survey. Please refresh the page and try again.');
    }
}

// Show question
function showQuestion(index) {
    if (index < 0 || index >= questions.length) return;
    
    currentQuestionIndex = index;
    const question = questions[index];
    const container = document.getElementById('question-container');
    
    // Update progress bar
    const progress = ((index + 1) / questions.length) * 100;
    document.getElementById('progress-fill').style.width = progress + '%';
    
    // Build question HTML
    let html = `
        <div class="question-number">Question ${index + 1} / ${questions.length}</div>
        <div class="question-text">${question.text}</div>
    `;
    
    if (question.is_open) {
        // Open-ended question
        html += `
            <div class="option-item">
                <label class="option-label">
                    <textarea 
                        id="answer-${question.id}" 
                        class="option-text" 
                        rows="4" 
                        placeholder="Please enter your answer here..."
                        style="width: 100%; padding: 1rem; border: 2px solid var(--border-color); border-radius: 8px; font-family: inherit; font-size: 1rem; resize: vertical;"
                    >${answers[question.id] || ''}</textarea>
                </label>
            </div>
        `;
    } else {
        // Multiple choice question
        html += '<ul class="options-list">';
        Object.entries(question.options).forEach(([key, value]) => {
            const isSelected = answers[question.id] === key;
            html += `
                <li class="option-item">
                    <label class="option-label ${isSelected ? 'selected' : ''}">
                        <input 
                            type="radio" 
                            name="question-${question.id}" 
                            value="${key}"
                            ${isSelected ? 'checked' : ''}
                            onchange="selectOption('${question.id}', '${key}')"
                        >
                        <span class="option-text">${key}. ${value}</span>
                    </label>
                </li>
            `;
        });
        html += '</ul>';
    }
    
    container.innerHTML = html;
    
    // If open-ended question, bind input event
    if (question.is_open) {
        const textarea = document.getElementById(`answer-${question.id}`);
        if (textarea) {
            textarea.addEventListener('input', (e) => {
                answers[question.id] = e.target.value;
            });
            // Restore previous value
            if (answers[question.id]) {
                textarea.value = answers[question.id];
            }
        }
    }
    
    // Update button status
    updateButtons();
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Select option
function selectOption(questionId, option) {
    answers[questionId] = option;
    
    // Update UI selected state
    const labels = document.querySelectorAll(`input[name="question-${questionId}"]`);
    labels.forEach(label => {
        const labelElement = label.closest('.option-label');
        if (label.value === option) {
            labelElement.classList.add('selected');
        } else {
            labelElement.classList.remove('selected');
        }
    });
    
    updateButtons();
}

// Update button status
function updateButtons() {
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const submitBtn = document.getElementById('submit-btn');
    
    // Previous button
    prevBtn.style.display = currentQuestionIndex > 0 ? 'block' : 'none';
    
    // Next/Submit button
    const isLastQuestion = currentQuestionIndex === questions.length - 1;
    const currentAnswer = answers[questions[currentQuestionIndex].id];
    const hasAnswer = currentAnswer !== null && currentAnswer !== '';
    
    if (isLastQuestion) {
        nextBtn.style.display = 'none';
        submitBtn.style.display = hasAnswer ? 'block' : 'none';
    } else {
        nextBtn.style.display = hasAnswer ? 'block' : 'none';
        submitBtn.style.display = 'none';
    }
    
    // Disable next button if no answer
    if (!isLastQuestion) {
        nextBtn.disabled = !hasAnswer;
    }
}

// Previous question
function prevQuestion() {
    if (currentQuestionIndex > 0) {
        showQuestion(currentQuestionIndex - 1);
    }
}

// Next question
function nextQuestion() {
    const currentAnswer = answers[questions[currentQuestionIndex].id];
    if (currentAnswer === null || currentAnswer === '') {
        alert('Please answer the current question first');
        return;
    }
    
    if (currentQuestionIndex < questions.length - 1) {
        showQuestion(currentQuestionIndex + 1);
    }
}

async function submitSurvey() {
    // Validate all questions are answered
    const unanswered = questions.filter(q => {
        const answer = answers[q.id];
        return answer === null || answer === '';
    });
    
    if (unanswered.length > 0) {
        alert('Please answer all questions before submitting');
        return;
    }
    
    // Hide survey section, show loading
    document.getElementById('survey-section').style.display = 'none';
    document.getElementById('loading-section').style.display = 'block';
    
    // Start fake progress bar animation
    const progressBar = document.getElementById('loading-progress-fill');
    let progress = 0;
    const targetProgress = 95; // Target 95%
    const duration = 20000; // 20 seconds
    const interval = 50; // Update every 50ms
    const increment = (targetProgress / duration) * interval;
    
    const progressInterval = setInterval(() => {
        progress += increment;
        if (progress >= targetProgress) {
            progress = targetProgress;
            clearInterval(progressInterval);
        }
        progressBar.style.width = progress + '%';
    }, interval);
    
    try {
        // Submit answers to backend
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(answers)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to generate report');
        }
        
        const data = await response.json();
        const reportContent = data.report;
        
        // Ensure progress bar reaches 100%
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        
        // Slight delay before showing report so user sees 100%
        setTimeout(() => {
            showReport(reportContent);
        }, 300);
        
    } catch (error) {
        console.error('Submission failed:', error);
        clearInterval(progressInterval);
        alert('Failed to generate report: ' + error.message);
        // Restore survey display
        document.getElementById('survey-section').style.display = 'block';
        document.getElementById('loading-section').style.display = 'none';
    }
}

// Show report
function showReport(markdownContent) {
    // Hide loading, show report
    document.getElementById('loading-section').style.display = 'none';
    document.getElementById('report-section').style.display = 'block';
    
    // Convert Markdown to HTML
    const htmlContent = marked.parse(markdownContent);
    document.getElementById('report-content').innerHTML = htmlContent;
    
    // Scroll to report section
    document.getElementById('report-section').scrollIntoView({ behavior: 'smooth' });
}

// Bind event listeners
document.addEventListener('DOMContentLoaded', () => {
    init();
    
    document.getElementById('prev-btn').addEventListener('click', prevQuestion);
    document.getElementById('next-btn').addEventListener('click', nextQuestion);
    document.getElementById('submit-btn').addEventListener('click', submitSurvey);
});
