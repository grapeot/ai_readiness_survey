// 问卷应用主逻辑
let questions = [];
let currentQuestionIndex = 0;
let answers = {};

// 初始化应用
async function init() {
    try {
        // 加载问题列表
        const response = await fetch('/api/questions');
        const data = await response.json();
        questions = data.questions;
        
        // 初始化答案对象
        questions.forEach(q => {
            if (q.is_open) {
                answers[q.id] = '';
            } else {
                answers[q.id] = null;
            }
        });
        
        // 显示第一个问题
        showQuestion(0);
    } catch (error) {
        console.error('初始化失败:', error);
        alert('加载问卷失败，请刷新页面重试');
    }
}

// 显示问题
function showQuestion(index) {
    if (index < 0 || index >= questions.length) return;
    
    currentQuestionIndex = index;
    const question = questions[index];
    const container = document.getElementById('question-container');
    
    // 更新进度条
    const progress = ((index + 1) / questions.length) * 100;
    document.getElementById('progress-fill').style.width = progress + '%';
    
    // 构建问题HTML
    let html = `
        <div class="question-number">问题 ${index + 1} / ${questions.length}</div>
        <div class="question-text">${question.text}</div>
    `;
    
    if (question.is_open) {
        // 开放性问题
        html += `
            <div class="option-item">
                <label class="option-label">
                    <textarea 
                        id="answer-${question.id}" 
                        class="option-text" 
                        rows="4" 
                        placeholder="请在此输入你的回答..."
                        style="width: 100%; padding: 1rem; border: 2px solid var(--border-color); border-radius: 8px; font-family: inherit; font-size: 1rem; resize: vertical;"
                    >${answers[question.id] || ''}</textarea>
                </label>
            </div>
        `;
    } else {
        // 选择题
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
    
    // 如果是开放性问题，绑定输入事件
    if (question.is_open) {
        const textarea = document.getElementById(`answer-${question.id}`);
        if (textarea) {
            textarea.addEventListener('input', (e) => {
                answers[question.id] = e.target.value;
            });
            // 恢复之前的值
            if (answers[question.id]) {
                textarea.value = answers[question.id];
            }
        }
    }
    
    // 更新按钮状态
    updateButtons();
    
    // 滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// 选择选项
function selectOption(questionId, option) {
    answers[questionId] = option;
    
    // 更新UI选中状态
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

// 更新按钮状态
function updateButtons() {
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const submitBtn = document.getElementById('submit-btn');
    
    // 上一题按钮
    prevBtn.style.display = currentQuestionIndex > 0 ? 'block' : 'none';
    
    // 下一题/提交按钮
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
    
    // 禁用下一题按钮如果没有答案
    if (!isLastQuestion) {
        nextBtn.disabled = !hasAnswer;
    }
}

// 上一题
function prevQuestion() {
    if (currentQuestionIndex > 0) {
        showQuestion(currentQuestionIndex - 1);
    }
}

// 下一题
function nextQuestion() {
    const currentAnswer = answers[questions[currentQuestionIndex].id];
    if (currentAnswer === null || currentAnswer === '') {
        alert('请先回答当前问题');
        return;
    }
    
    if (currentQuestionIndex < questions.length - 1) {
        showQuestion(currentQuestionIndex + 1);
    }
}

// 提交问卷
async function submitSurvey() {
    // 验证所有问题都已回答
    const unanswered = questions.filter(q => {
        const answer = answers[q.id];
        return answer === null || answer === '';
    });
    
    if (unanswered.length > 0) {
        alert('请回答所有问题后再提交');
        return;
    }
    
    // 隐藏问卷区域，显示加载中
    document.getElementById('survey-section').style.display = 'none';
    document.getElementById('loading-section').style.display = 'block';
    
    // 启动假的进度条动画
    const progressBar = document.getElementById('loading-progress-fill');
    let progress = 0;
    const targetProgress = 95; // 目标进度95%
    const duration = 30000; // 30秒
    const interval = 50; // 每50ms更新一次
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
        // 提交答案到后端
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(answers)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '生成报告失败');
        }
        
        const data = await response.json();
        const reportContent = data.report;
        
        // 确保进度条到达100%
        clearInterval(progressInterval);
        progressBar.style.width = '100%';
        
        // 稍微延迟一下再显示报告，让用户看到100%
        setTimeout(() => {
            showReport(reportContent);
        }, 300);
        
    } catch (error) {
        console.error('提交失败:', error);
        clearInterval(progressInterval);
        alert('生成报告失败: ' + error.message);
        // 恢复问卷显示
        document.getElementById('survey-section').style.display = 'block';
        document.getElementById('loading-section').style.display = 'none';
    }
}

// 显示报告
function showReport(markdownContent) {
    // 隐藏加载中，显示报告
    document.getElementById('loading-section').style.display = 'none';
    document.getElementById('report-section').style.display = 'block';
    
    // 将Markdown转换为HTML
    const htmlContent = marked.parse(markdownContent);
    document.getElementById('report-content').innerHTML = htmlContent;
    
    // 滚动到报告区域
    document.getElementById('report-section').scrollIntoView({ behavior: 'smooth' });
}

// 绑定事件监听器
document.addEventListener('DOMContentLoaded', () => {
    init();
    
    document.getElementById('prev-btn').addEventListener('click', prevQuestion);
    document.getElementById('next-btn').addEventListener('click', nextQuestion);
    document.getElementById('submit-btn').addEventListener('click', submitSurvey);
});

