/**
 * Quiz Application - Kiểm tra kiến thức Tư tưởng Hồ Chí Minh
 */

class QuizApp {
    constructor() {
        this.API_BASE = window.PYTHON_AI_API || 'http://localhost:8000';
        this.currentQuiz = null;
        this.currentQuestionIndex = 0;
        this.userAnswers = {};
        this.startTime = null;
        this.timerInterval = null;
        this.user = null;

        this.init();
    }

    async init() {
        // Check authentication
        const userStr = localStorage.getItem('user');
        const token = localStorage.getItem('token');

        if (!userStr || !token) {
            alert('Vui lòng đăng nhập trước');
            window.location.href = 'auth.html';
            return;
        }

        this.user = JSON.parse(userStr);
        document.getElementById('username').textContent = this.user.fullName || this.user.username;

        // Setup event listeners
        this.setupEventListeners();

        // Check if quiz_id in URL (opened from chat)
        const urlParams = new URLSearchParams(window.location.search);
        const quizId = urlParams.get('quiz_id') || urlParams.get('quizid'); // Support both formats
        
        if (quizId) {
            // Load and start quiz directly
            this.loadQuizById(quizId);
        }
    }

    async loadQuizById(quizId) {
        try {
            // Show loading
            document.getElementById('premadeQuizzes').style.display = 'none';
            document.getElementById('loadingContainer').style.display = 'block';

            const response = await fetch(`${this.API_BASE}/quiz/${quizId}`);
            if (!response.ok) throw new Error('Không tìm thấy bài kiểm tra');

            const quiz = await response.json();
            this.currentQuiz = quiz;

            // Hide loading and start quiz directly
            document.getElementById('loadingContainer').style.display = 'none';
            this.startQuiz();

        } catch (error) {
            console.error('Error loading quiz:', error);
            alert('Không thể tải bài kiểm tra. Vui lòng thử lại.');
            window.location.href = 'quiz.html';
        }
    }

    setupEventListeners() {
        // Difficulty buttons
        document.querySelectorAll('.diff-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.diff-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
            });
        });
    }




    renderQuestions() {
        const container = document.getElementById('questionContainer');
        container.innerHTML = '';

        this.currentQuiz.questions.forEach((q, index) => {
            const questionDiv = document.createElement('div');
            questionDiv.className = 'question';
            questionDiv.id = `question-${index}`;
            
            questionDiv.innerHTML = `
                <h3>Câu ${index + 1}: ${q.question}</h3>
                <div class="options">
                    ${q.options.map((option, optionIndex) => {
                        const letter = String.fromCharCode(65 + optionIndex); // A, B, C, D
                        return `
                            <div class="option" onclick="quizApp.selectAnswer(${index}, '${letter}')">
                                <input type="radio" name="q${index}" id="q${index}_${letter}" value="${letter}">
                                <label for="q${index}_${letter}">
                                    <strong>${letter}.</strong> ${option}
                            </label>
                        </div>
                        `;
                    }).join('')}
                </div>
            `;
            
            container.appendChild(questionDiv);
        });
    }

    renderQuestionMap() {
        const mapContainer = document.getElementById('questionMap');
        mapContainer.innerHTML = '';

        this.currentQuiz.questions.forEach((_, index) => {
            const btn = document.createElement('button');
            btn.className = 'q-btn';
            btn.textContent = index + 1;
            btn.onclick = () => this.showQuestion(index);
            btn.id = `qmap-${index}`;
            mapContainer.appendChild(btn);
        });
    }

    selectAnswer(questionIndex, answer) {
        // Convert answer to index (A=0, B=1, C=2, D=3)
        const answerIndex = answer.charCodeAt(0) - 65; // A=0, B=1, C=2, D=3
        
        // Save answer as index
        const questionId = this.currentQuiz.questions[questionIndex].id;
        this.userAnswers[questionId] = answerIndex;
        
        // Debug log
        console.log(`Selected answer:`, {
            questionIndex: questionIndex,
            answer: answer,
            answerIndex: answerIndex,
            questionId: questionId,
            userAnswers: this.userAnswers
        });

        // Update UI
        const options = document.querySelectorAll(`#question-${questionIndex} .option`);
        options.forEach(opt => opt.classList.remove('selected'));
        
        const selectedOption = document.querySelector(`#q${questionIndex}_${answer}`);
        if (selectedOption) {
            selectedOption.checked = true;
            selectedOption.parentElement.classList.add('selected');
        }

        // Update question map
        document.getElementById(`qmap-${questionIndex}`).classList.add('answered');

        // Update progress
        this.updateProgress();

        // Auto advance to next question after a short delay
        setTimeout(() => {
            const nextIndex = questionIndex + 1;
            if (nextIndex < this.currentQuiz.questions.length) {
                this.showQuestion(nextIndex);
            }
        }, 800); // 0.8 second delay to show selection feedback
    }

    showQuestion(index) {
        if (index < 0 || index >= this.currentQuiz.questions.length) return;

        this.currentQuestionIndex = index;

        // Hide all questions
        document.querySelectorAll('.question').forEach(q => {
            q.classList.remove('active');
        });

        // Show selected question
        document.getElementById(`question-${index}`).classList.add('active');

        // Update navigation
        document.getElementById('btnPrev').disabled = index === 0;
        document.getElementById('btnNext').disabled = index === this.currentQuiz.questions.length - 1;
        document.getElementById('questionNumber').textContent = 
            `Câu ${index + 1}/${this.currentQuiz.questions.length}`;

        // Update question map
        document.querySelectorAll('.q-btn').forEach(btn => {
            btn.classList.remove('current');
        });
        document.getElementById(`qmap-${index}`).classList.add('current');

        // Restore selected answer if any
        const questionId = this.currentQuiz.questions[index].id;
        if (this.userAnswers[questionId]) {
            const answer = this.userAnswers[questionId];
            document.getElementById(`q${index}_${answer}`).checked = true;
            document.querySelector(`#q${index}_${answer}`).parentElement.classList.add('selected');
        }
    }

    prevQuestion() {
        if (this.currentQuestionIndex > 0) {
            this.showQuestion(this.currentQuestionIndex - 1);
        }
    }

    nextQuestion() {
        if (this.currentQuestionIndex < this.currentQuiz.questions.length - 1) {
            this.showQuestion(this.currentQuestionIndex + 1);
        }
    }

    updateProgress() {
        const answered = Object.keys(this.userAnswers).length;
        const total = this.currentQuiz.questions.length;
        const percentage = (answered / total) * 100;

        document.getElementById('progressFill').style.width = percentage + '%';
        document.getElementById('progressText').textContent = `${answered}/${total}`;
    }

    startTimer(timeLimit = null) {
        this.startTime = Date.now();
        this.timeLimit = timeLimit;
        
        this.timerInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            
            // Check if time limit reached
            if (this.timeLimit && elapsed >= this.timeLimit) {
                this.submitQuiz();
                return;
            }
            
            document.getElementById('timer').textContent = 
                `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }, 1000);
    }

    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }

    async submitQuiz() {
        const answered = Object.keys(this.userAnswers).length;
        const total = this.currentQuiz.questions.length;

        if (answered < total) {
            if (!confirm(`Bạn mới trả lời ${answered}/${total} câu. Bạn có chắc muốn nộp bài không?`)) {
                return;
            }
        }

        this.stopTimer();

        try {
            // Check if this is a pre-made quiz (local JSON file)
            if (this.currentQuiz.id && this.currentQuiz.id.startsWith('chuong3_quiz_')) {
                // Calculate result locally for pre-made quizzes
                const result = this.calculateLocalResult();
                this.showResult(result);
            } else {
                // Submit quiz to server for generated quizzes
            const response = await fetch(`${this.API_BASE}/quiz/submit`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    quiz_id: this.currentQuiz.id,
                    username: this.user.username,
                    answers: this.userAnswers
                })
            });

            if (!response.ok) {
                throw new Error('Không thể nộp bài');
            }

            const result = await response.json();
            this.showResult(result);
            }

        } catch (error) {
            console.error('Error submitting quiz:', error);
            alert('Lỗi khi nộp bài: ' + error.message);
        }
    }

    calculateLocalResult() {
        const totalQuestions = this.currentQuiz.questions.length;
        let correctCount = 0;
        const details = [];
        
        // Debug log
        console.log('Calculating result:', {
            totalQuestions: totalQuestions,
            userAnswers: this.userAnswers,
            currentQuiz: this.currentQuiz
        });

        this.currentQuiz.questions.forEach((question, index) => {
            const userAnswer = this.userAnswers[question.id];
            const isCorrect = userAnswer === question.correct_answer;
            
            // Debug log
            console.log(`Question ${index + 1}:`, {
                question: question.question,
                userAnswer: userAnswer,
                correctAnswer: question.correct_answer,
                isCorrect: isCorrect
            });
            
            if (isCorrect) {
                correctCount++;
            }

            details.push({
                question: question.question,
                user_answer: userAnswer,
                correct_answer: question.correct_answer,
                is_correct: isCorrect,
                explanation: question.explanation
            });
        });

        const score = (correctCount / totalQuestions) * 10; // Convert to 10-point scale
        const percentage = (correctCount / totalQuestions) * 100;

        const result = {
            score: score,
            correct_count: correctCount,
            total_questions: totalQuestions,
            percentage: percentage,
            details: details
        };

        // Save quiz result to localStorage
        console.log('Saving quiz result:', result);
        this.saveQuizResult(result);

        return result;
    }

    saveQuizResult(result) {
        try {
            // Get existing results
            const existingResults = JSON.parse(localStorage.getItem('quizResults') || '[]');
            
            // Create new result entry
            const newResult = {
                id: Date.now().toString(),
                quiz_id: this.currentQuiz.id,
                quiz_title: this.currentQuiz.title,
                username: this.user?.username || 'Guest',
                score: result.score,
                correct_count: result.correct_count,
                total_questions: result.total_questions,
                percentage: result.percentage,
                completed_at: new Date().toISOString(),
                details: result.details
            };

            // Add to beginning of array (most recent first)
            existingResults.unshift(newResult);

            // Keep only last 50 results
            if (existingResults.length > 50) {
                existingResults.splice(50);
            }

            // Save back to localStorage
            localStorage.setItem('quizResults', JSON.stringify(existingResults));
            
            console.log('Quiz result saved:', newResult);
        } catch (error) {
            console.error('Error saving quiz result:', error);
        }
    }

    showResult(result) {
        // Hide taking section, show result section
        document.getElementById('quizTaking').style.display = 'none';
        document.getElementById('premadeQuizzes').style.display = 'none';
        document.getElementById('quizResult').style.display = 'block';

        // Animate score circle
        const scorePercentage = (result.score / 10) * 100;
        setTimeout(() => {
            const circle = document.getElementById('scoreCircle');
            const offset = 565 - (565 * scorePercentage) / 100;
            circle.style.strokeDashoffset = offset;
        }, 100);

        // Display score
        document.getElementById('scoreNumber').textContent = result.score.toFixed(1);
        document.getElementById('correctCount').textContent = result.correct_count;
        document.getElementById('wrongCount').textContent = result.total_questions - result.correct_count;
        document.getElementById('percentage').textContent = result.percentage.toFixed(1) + '%';

        // Display message based on score
        let message = '';
        let description = '';
        
        if (result.score >= 9) {
            message = 'Xuất sắc!';
            description = 'Bạn có kiến thức rất tốt về tư tưởng Hồ Chí Minh!';
        } else if (result.score >= 7) {
            message = 'Tốt!';
            description = 'Bạn nắm vững kiến thức cơ bản. Hãy tiếp tục học tập!';
        } else if (result.score >= 5) {
            message = 'Khá!';
            description = 'Bạn cần ôn tập thêm một số phần kiến thức.';
        } else {
            message = 'Cần cải thiện!';
            description = 'Hãy dành thời gian ôn tập lại kiến thức nhé!';
        }

        document.getElementById('resultMessage').textContent = message;
        document.getElementById('resultDescription').textContent = description;

        // Display answer details
        this.displayAnswerDetails(result.details);
    }

    displayAnswerDetails(details) {
        const container = document.getElementById('answerDetails');
        container.innerHTML = '';

        details.forEach((detail, index) => {
            const div = document.createElement('div');
            div.className = `answer-detail ${detail.is_correct ? 'correct' : 'wrong'}`;
            
            // Convert index to letter (0=A, 1=B, 2=C, 3=D)
            const userAnswerLetter = detail.user_answer !== undefined ? String.fromCharCode(65 + detail.user_answer) : 'Chưa trả lời';
            const correctAnswerLetter = String.fromCharCode(65 + detail.correct_answer);
            
            div.innerHTML = `
                <h4>Câu ${index + 1}: ${detail.question}</h4>
                <p>Đáp án của bạn: 
                    <span class="${detail.is_correct ? 'correct-answer' : 'wrong-answer'}">
                        ${userAnswerLetter}
                    </span>
                </p>
                ${!detail.is_correct ? `
                    <p>Đáp án đúng: 
                        <span class="correct-answer">${correctAnswerLetter}</span>
                    </p>
                ` : ''}
                ${detail.explanation ? `
                    <div class="explanation">
                        <strong>Giải thích:</strong> ${detail.explanation}
                    </div>
                ` : ''}
            `;
            
            container.appendChild(div);
        });
    }

    async showHistory() {
        // Hide all sections
        document.getElementById('premadeQuizzes').style.display = 'none';
        document.getElementById('quizTaking').style.display = 'none';
        document.getElementById('quizResult').style.display = 'none';
        document.getElementById('historySection').style.display = 'block';

        // Load history from localStorage
        this.loadHistory();
    }

    loadHistory() {
        try {
            const results = JSON.parse(localStorage.getItem('quizResults') || '[]');
            const historyContainer = document.getElementById('historyContent');
            
            if (results.length === 0) {
                historyContainer.innerHTML = `
                    <div class="no-history">
                        <i class="fas fa-history"></i>
                        <h3>Chưa có lịch sử làm bài</h3>
                        <p>Hãy tham gia các bài quiz để xem lịch sử của bạn!</p>
                    </div>
                `;
                return;
            }

            historyContainer.innerHTML = results.map(result => `
                <div class="history-item">
                    <div class="history-header">
                        <h4>${result.quiz_title}</h4>
                        <span class="history-date">${new Date(result.completed_at).toLocaleString('vi-VN')}</span>
                    </div>
                    <div class="history-stats">
                        <div class="stat">
                            <span class="stat-label">Điểm:</span>
                            <span class="stat-value ${result.percentage >= 80 ? 'excellent' : result.percentage >= 60 ? 'good' : 'poor'}">${result.score.toFixed(1)}/10</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Tỷ lệ:</span>
                            <span class="stat-value">${result.percentage.toFixed(1)}%</span>
                        </div>
                        <div class="stat">
                            <span class="stat-label">Đúng:</span>
                            <span class="stat-value">${result.correct_count}/${result.total_questions}</span>
                        </div>
                    </div>
                    <div class="history-actions">
                        <button class="btn-view-detail" onclick="quizApp.viewHistoryDetail('${result.id}')">
                            <i class="fas fa-eye"></i> Xem chi tiết
                        </button>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading history:', error);
            document.getElementById('historyContent').innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Có lỗi khi tải lịch sử. Vui lòng thử lại!</p>
                </div>
            `;
        }
    }

    viewHistoryDetail(resultId) {
        try {
            const results = JSON.parse(localStorage.getItem('quizResults') || '[]');
            const result = results.find(r => r.id === resultId);
            
            if (!result) {
                alert('Không tìm thấy kết quả quiz!');
                return;
            }

            // Show detailed result
            this.showResult(result);
        } catch (error) {
            console.error('Error viewing history detail:', error);
            alert('Có lỗi khi xem chi tiết kết quả!');
        }
    }

    debugLocalStorage() {
        try {
            const results = JSON.parse(localStorage.getItem('quizResults') || '[]');
            console.log('LocalStorage quizResults:', results);
            alert(`Có ${results.length} kết quả quiz trong localStorage. Xem console để chi tiết.`);
        } catch (error) {
            console.error('Error reading localStorage:', error);
            alert('Lỗi khi đọc localStorage: ' + error.message);
        }
    }

    displayHistory(history) {
        const container = document.getElementById('historyContent');
        
        if (!history || history.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #666;">Chưa có lịch sử làm bài</p>';
            return;
        }

        container.innerHTML = history.map(item => `
            <div class="history-item" onclick="quizApp.viewHistoryDetail('${item.id}')">
                <div class="history-info">
                    <h4>${item.quiz_title || 'Bài kiểm tra'}</h4>
                    <div class="history-meta">
                        <span><i class="fas fa-clock"></i> ${new Date(item.submitted_at).toLocaleString('vi-VN')}</span>
                        <span><i class="fas fa-check"></i> ${item.correct_count}/${item.total_questions} câu</span>
                    </div>
                </div>
                <div class="history-score">
                    <div class="score-badge">${item.score.toFixed(1)}</div>
                </div>
            </div>
        `).join('');
    }

    async viewHistoryDetail(resultId) {
        try {
            const response = await fetch(`${this.API_BASE}/quiz/result/${this.user.username}/${resultId}`);
            if (!response.ok) throw new Error('Không thể tải chi tiết');

            const result = await response.json();
            
            // Show result section with historical data
            document.getElementById('historySection').style.display = 'none';
            document.getElementById('premadeQuizzes').style.display = 'none';
            this.showResult(result);

        } catch (error) {
            console.error('Error loading result detail:', error);
            alert('Không thể tải chi tiết bài làm');
        }
    }

    backToQuizCreation() {
        document.getElementById('historySection').style.display = 'none';
        document.getElementById('quizTaking').style.display = 'none';
        document.getElementById('quizResult').style.display = 'none';
        document.getElementById('premadeQuizzes').style.display = 'block';
    }
}

// Global functions for HTML events
let quizApp;

window.addEventListener('DOMContentLoaded', () => {
    quizApp = new QuizApp();
});


function prevQuestion() {
    quizApp.prevQuestion();
}

function nextQuestion() {
    quizApp.nextQuestion();
}

function submitQuiz() {
    quizApp.submitQuiz();
}

function showHistory() {
    quizApp.showHistory();
}

function backToQuizCreation() {
    quizApp.backToQuizCreation();
}

// Function to start pre-made quiz
async function startPreMadeQuiz(quizId) {
    try {
        // Show loading
        document.getElementById('premadeQuizzes').style.display = 'none';
        document.getElementById('loadingContainer').style.display = 'block';

        // Load quiz data from local JSON files
        const response = await fetch(`quiz_data/quizzes/${quizId}.json`);
        if (!response.ok) {
            throw new Error('Không thể tải quiz');
        }

        const quizData = await response.json();
        
        // Set current quiz
        quizApp.currentQuiz = quizData;
        quizApp.currentQuestionIndex = 0;
        quizApp.userAnswers = {};
        quizApp.startTime = new Date();

        // Hide loading and show quiz
        document.getElementById('loadingContainer').style.display = 'none';
        document.getElementById('quizTaking').style.display = 'block';

        // Update quiz title and meta
        document.getElementById('quizTitle').textContent = quizData.title;
        document.getElementById('quizMeta').textContent = `${quizData.questions.length} câu hỏi • ${quizData.difficulty} • ${Math.floor(quizData.time_limit / 60)} phút`;

        // Render questions and question map
        quizApp.renderQuestions();
        quizApp.renderQuestionMap();

        // Start timer
        quizApp.startTimer(quizData.time_limit);

        // Show first question
        quizApp.showQuestion(0);

    } catch (error) {
        console.error('Error loading pre-made quiz:', error);
        alert('Không thể tải quiz. Vui lòng thử lại.');
        
        // Show quiz creation section again
        document.getElementById('loadingContainer').style.display = 'none';
        document.getElementById('premadeQuizzes').style.display = 'block';
    }
}
