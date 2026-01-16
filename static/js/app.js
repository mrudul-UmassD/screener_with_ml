// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// State Management
let currentJobs = [];
let currentResumes = [];

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    initializeTabs();
    initializeForms();
    loadStats();
    loadJobs();
});

// Tab Navigation
function initializeTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.getAttribute('data-tab');

            // Update active states
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            button.classList.add('active');
            document.getElementById(`${tabName}-tab`).classList.add('active');

            // Load data when switching tabs
            if (tabName === 'screen' || tabName === 'results') {
                loadJobs();
            }
        });
    });
}

// Form Handlers
function initializeForms() {
    // Resume Form
    document.getElementById('resumeForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await uploadResume();
    });

    // Job Form
    document.getElementById('jobForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await uploadJob();
    });

    // Screen Form
    document.getElementById('screenForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await screenCandidates();
    });

    // Results Job Select
    document.getElementById('resultsJobSelect').addEventListener('change', (e) => {
        if (e.target.value) {
            loadResults(e.target.value);
        }
    });
}

// API Functions
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || 'API request failed');
        }

        return result;
    } catch (error) {
        console.error('API Error:', error);
        showToast(error.message, 'error');
        throw error;
    }
}

// Load Statistics
async function loadStats() {
    try {
        const result = await apiCall('/stats');
        const stats = result.data;

        document.getElementById('totalJobs').textContent = stats.total_jobs;
        document.getElementById('totalResumes').textContent = stats.total_resumes;
        document.getElementById('totalScreenings').textContent = stats.total_screenings;
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

// Upload Resume
async function uploadResume() {
    const form = document.getElementById('resumeForm');
    const resultBox = document.getElementById('resumeResult');

    const data = {
        candidate_name: document.getElementById('candidateName').value,
        email: document.getElementById('candidateEmail').value,
        phone: document.getElementById('candidatePhone').value,
        content: document.getElementById('resumeContent').value,
    };

    try {
        resultBox.className = 'result-box';
        resultBox.style.display = 'none';

        const result = await apiCall('/upload/resume', 'POST', data);

        resultBox.className = 'result-box success';
        resultBox.innerHTML = `
            <h4>✓ Resume Uploaded Successfully!</h4>
            <p><strong>Candidate:</strong> ${result.data.candidate_name}</p>
            <p><strong>Skills Extracted:</strong> ${result.data.skills_extracted}</p>
            <p><strong>Experience:</strong> ${result.data.experience_years} years</p>
            <p><strong>Top Skills:</strong> ${result.data.skills.slice(0, 5).join(', ')}</p>
        `;

        form.reset();
        showToast('Resume uploaded successfully!', 'success');
        loadStats();
    } catch (error) {
        resultBox.className = 'result-box error';
        resultBox.innerHTML = `<h4>✗ Upload Failed</h4><p>${error.message}</p>`;
    }
}

// Upload Job
async function uploadJob() {
    const form = document.getElementById('jobForm');
    const resultBox = document.getElementById('jobResult');

    const data = {
        title: document.getElementById('jobTitle').value,
        description: document.getElementById('jobDescription').value,
    };

    try {
        resultBox.className = 'result-box';
        resultBox.style.display = 'none';

        const result = await apiCall('/upload/job', 'POST', data);

        resultBox.className = 'result-box success';
        resultBox.innerHTML = `
            <h4>✓ Job Posted Successfully!</h4>
            <p><strong>Position:</strong> ${result.data.title}</p>
            <p><strong>Skills Required:</strong> ${result.data.skills_required}</p>
            <p><strong>Key Skills:</strong> ${result.data.skills.slice(0, 5).join(', ')}</p>
        `;

        form.reset();
        showToast('Job description uploaded successfully!', 'success');
        loadStats();
        loadJobs();
    } catch (error) {
        resultBox.className = 'result-box error';
        resultBox.innerHTML = `<h4>✗ Upload Failed</h4><p>${error.message}</p>`;
    }
}

// Load Jobs
async function loadJobs() {
    try {
        const result = await apiCall('/stats');
        // Note: We'd need an endpoint to list all jobs. For now, we'll store job IDs when they're created
        // This is a simplified version
    } catch (error) {
        console.error('Failed to load jobs:', error);
    }
}

// Screen Candidates
async function screenCandidates() {
    const jobId = document.getElementById('jobSelect').value;
    const resultBox = document.getElementById('screenResult');
    const progressBox = document.getElementById('screenProgress');

    if (!jobId) {
        showToast('Please select a job', 'error');
        return;
    }

    try {
        resultBox.style.display = 'none';
        progressBox.style.display = 'block';

        const result = await apiCall('/screen', 'POST', { job_id: jobId });

        progressBox.style.display = 'none';
        resultBox.className = 'result-box success';
        resultBox.innerHTML = `
            <h4>✓ Screening Complete!</h4>
            <p><strong>Candidates Screened:</strong> ${result.data.candidates_screened}</p>
            <p>View detailed results in the "View Results" tab.</p>
        `;

        showToast(`Successfully screened ${result.data.candidates_screened} candidates!`, 'success');
        loadStats();
        
        // Auto-switch to results tab
        setTimeout(() => {
            document.querySelector('[data-tab="results"]').click();
            document.getElementById('resultsJobSelect').value = jobId;
            loadResults(jobId);
        }, 2000);
    } catch (error) {
        progressBox.style.display = 'none';
        resultBox.className = 'result-box error';
        resultBox.innerHTML = `<h4>✗ Screening Failed</h4><p>${error.message}</p>`;
    }
}

// Load Results
async function loadResults(jobId) {
    const container = document.getElementById('resultsContainer');

    try {
        container.innerHTML = '<div class="progress-box"><div class="spinner"></div><p>Loading results...</p></div>';

        const result = await apiCall(`/results/${jobId}`);
        const candidates = result.data.results;

        if (candidates.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                        <rect x="12" y="20" width="40" height="32" stroke="#D1D5DB" stroke-width="2" fill="none"/>
                    </svg>
                    <p>No candidates found for this job.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = candidates.map(candidate => createCandidateCard(candidate)).join('');
    } catch (error) {
        container.innerHTML = `
            <div class="empty-state">
                <p style="color: var(--danger);">Failed to load results: ${error.message}</p>
            </div>
        `;
    }
}

// Create Candidate Card
function createCandidateCard(candidate) {
    const overallScore = (candidate.overall_score * 100).toFixed(1);
    const skillScore = (candidate.skill_match_score * 100).toFixed(1);
    const semanticScore = (candidate.semantic_similarity_score * 100).toFixed(1);
    const expScore = (candidate.experience_score * 100).toFixed(1);

    const matchedSkills = typeof candidate.matched_skills === 'string' 
        ? JSON.parse(candidate.matched_skills) 
        : candidate.matched_skills || [];

    const rankClass = candidate.rank <= 3 ? 'top' : '';

    return `
        <div class="candidate-card">
            <div class="candidate-header">
                <div class="candidate-info">
                    <h3>${candidate.candidate_name}</h3>
                    <div class="candidate-contact">
                        ${candidate.email ? `📧 ${candidate.email}` : ''}
                        ${candidate.phone ? `📱 ${candidate.phone}` : ''}
                        ${candidate.experience_years ? `💼 ${candidate.experience_years} years exp.` : ''}
                    </div>
                </div>
                <div class="rank-badge ${rankClass}">
                    #${candidate.rank}
                </div>
            </div>

            <div class="candidate-scores">
                <div class="score-item">
                    <div class="score-label">Overall</div>
                    <div class="score-value">${overallScore}%</div>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${overallScore}%"></div>
                    </div>
                </div>
                <div class="score-item">
                    <div class="score-label">Skills</div>
                    <div class="score-value">${skillScore}%</div>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${skillScore}%"></div>
                    </div>
                </div>
                <div class="score-item">
                    <div class="score-label">Semantic</div>
                    <div class="score-value">${semanticScore}%</div>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${semanticScore}%"></div>
                    </div>
                </div>
                <div class="score-item">
                    <div class="score-label">Experience</div>
                    <div class="score-value">${expScore}%</div>
                    <div class="score-bar">
                        <div class="score-fill" style="width: ${expScore}%"></div>
                    </div>
                </div>
            </div>

            ${matchedSkills.length > 0 ? `
                <div class="candidate-skills">
                    <h4>Matched Skills</h4>
                    <div class="skill-tags">
                        ${matchedSkills.slice(0, 10).map(skill => 
                            `<span class="skill-tag">${skill}</span>`
                        ).join('')}
                        ${matchedSkills.length > 10 ? 
                            `<span class="skill-tag">+${matchedSkills.length - 10} more</span>` : 
                            ''
                        }
                    </div>
                </div>
            ` : ''}
        </div>
    `;
}

// Toast Notifications
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: '✓',
        error: '✗',
        info: 'ℹ'
    };

    toast.innerHTML = `
        <span style="font-size: 20px;">${icons[type]}</span>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Sample Data for Testing (Remove in production)
function populateSampleData() {
    // Add sample job IDs to select dropdowns
    const jobSelects = [document.getElementById('jobSelect'), document.getElementById('resultsJobSelect')];
    
    jobSelects.forEach(select => {
        const option = document.createElement('option');
        option.value = 'sample-job-1';
        option.textContent = 'Senior Python Developer';
        select.appendChild(option);
    });
}

// Call this for demo purposes
// populateSampleData();
