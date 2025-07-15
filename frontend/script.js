// Global variables
let statusCheckInterval;
let recordingsCheckInterval;

// DOM elements
const videoFeed = document.getElementById('videoFeed');
const recordBtn = document.getElementById('recordBtn');
const viewRecordingsBtn = document.getElementById('viewRecordingsBtn');
const recordingsPanel = document.getElementById('recordingsPanel');
const closeRecordingsBtn = document.getElementById('closeRecordingsBtn');
const recordingsList = document.getElementById('recordingsList');
const statusIndicator = document.getElementById('statusIndicator');
const statusDot = statusIndicator.querySelector('.status-dot');
const statusText = statusIndicator.querySelector('.status-text');
const motionIndicator = document.getElementById('motionIndicator');
const notifications = document.getElementById('notifications');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Set up event listeners
    recordBtn.addEventListener('click', handleManualRecord);
    viewRecordingsBtn.addEventListener('click', toggleRecordingsPanel);
    closeRecordingsBtn.addEventListener('click', toggleRecordingsPanel);
    
    // Start status monitoring
    startStatusMonitoring();
    
    // Load initial recordings
    loadRecordings();
    
    // Set up periodic updates
    setInterval(loadRecordings, 10000); // Update recordings every 10 seconds
    setInterval(checkStatus, 5000); // Check status every 5 seconds
    
    // Handle video feed errors
    videoFeed.addEventListener('error', handleVideoError);
    videoFeed.addEventListener('load', handleVideoLoad);
}

async function handleManualRecord() {
    try {
        recordBtn.disabled = true;
        recordBtn.innerHTML = '<span class="btn-icon">⏳</span> Recording...';
        
        const response = await fetch('/record', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Recording started successfully!', 'success');
            // Refresh recordings after a short delay
            setTimeout(loadRecordings, 2000);
        } else {
            showNotification(data.detail || 'Failed to start recording', 'error');
        }
    } catch (error) {
        console.error('Error starting recording:', error);
        showNotification('Failed to start recording. Please try again.', 'error');
    } finally {
        recordBtn.disabled = false;
        recordBtn.innerHTML = '<span class="btn-icon">📹</span> Record Now';
    }
}

function toggleRecordingsPanel() {
    const isVisible = recordingsPanel.style.display !== 'none';
    
    if (isVisible) {
        recordingsPanel.style.display = 'none';
        viewRecordingsBtn.innerHTML = '<span class="btn-icon">📁</span> View Recordings';
    } else {
        recordingsPanel.style.display = 'block';
        viewRecordingsBtn.innerHTML = '<span class="btn-icon">📁</span> Hide Recordings';
        loadRecordings();
    }
}

async function loadRecordings() {
    try {
        const response = await fetch('/recordings');
        const data = await response.json();
        
        if (response.ok) {
            displayRecordings(data.recordings);
        } else {
            console.error('Failed to load recordings:', data);
        }
    } catch (error) {
        console.error('Error loading recordings:', error);
    }
}

function displayRecordings(recordings) {
    if (recordings.length === 0) {
        recordingsList.innerHTML = '<div style="text-align: center; color: rgba(255,255,255,0.7); padding: 20px;">No recordings found</div>';
        return;
    }
    
    recordingsList.innerHTML = recordings.map(recording => {
        const date = new Date(recording.created);
        const formattedDate = date.toLocaleString();
        const sizeMB = (recording.size / (1024 * 1024)).toFixed(2);
        
        return `
            <div class="recording-item">
                <div class="recording-info">
                    <div class="recording-name">${recording.filename}</div>
                    <div class="recording-details">
                        ${formattedDate} • ${sizeMB} MB
                    </div>
                </div>
                <div class="recording-actions">
                    <button class="btn-play" onclick="playRecording('${recording.filename}')">
                        ▶️ Play
                    </button>
                    <button class="btn-download" onclick="downloadRecording('${recording.filename}')">
                        📥 Download
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

function playRecording(filename) {
    const videoUrl = `/recordings/${filename}`;
    showModal(videoUrl);
}

function showModal(videoUrl) {
    const modal = document.getElementById('modal');
    const modalVideo = document.getElementById('modalVideo');
    const modalClose = document.getElementById('modalClose');

    modalVideo.src = videoUrl;
    modal.style.display = 'block';

    modalClose.onclick = () => {
        modal.style.display = 'none';
        modalVideo.pause();
    };

    window.onclick = (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
            modalVideo.pause();
        }
    };
}

function downloadRecording(filename) {
    const link = document.createElement('a');
    link.href = `/recordings/${filename}`;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showNotification('Download started!', 'success');
}

async function checkStatus() {
    try {
        const response = await fetch('/status');
        const data = await response.json();
        
        if (response.ok) {
            updateStatusIndicator(data);
            updateMotionIndicator(data.motion_detected);
        } else {
            updateStatusIndicator({ status: 'error' });
        }
    } catch (error) {
        console.error('Error checking status:', error);
        updateStatusIndicator({ status: 'error' });
    }
}

function updateStatusIndicator(data) {
    if (data.status === 'active') {
        statusDot.classList.add('connected');
        statusText.textContent = 'Connected';
        
        if (data.is_recording) {
            statusText.textContent = 'Recording...';
        }
    } else {
        statusDot.classList.remove('connected');
        statusText.textContent = 'Disconnected';
    }
}

function updateMotionIndicator(motionDetected) {
    if (motionDetected) {
        motionIndicator.classList.add('active');
    } else {
        motionIndicator.classList.remove('active');
    }
}

function startStatusMonitoring() {
    // Initial status check
    checkStatus();
    
    // Set up periodic status checks
    statusCheckInterval = setInterval(checkStatus, 5000);
}

function handleVideoError() {
    showNotification('Failed to load video feed. Please check camera connection.', 'error');
    statusText.textContent = 'Camera Error';
    statusDot.classList.remove('connected');
}

function handleVideoLoad() {
    statusText.textContent = 'Connected';
    statusDot.classList.add('connected');
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    notifications.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// Handle page visibility changes
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Page is hidden, reduce polling
        if (statusCheckInterval) {
            clearInterval(statusCheckInterval);
        }
    } else {
        // Page is visible, restart polling
        startStatusMonitoring();
    }
});

// Handle window resize for responsive design
window.addEventListener('resize', function() {
    // Adjust video feed size if needed
    if (videoFeed) {
        videoFeed.style.width = '100%';
    }
});

// Error handling for network issues
window.addEventListener('online', function() {
    showNotification('Connection restored!', 'success');
    checkStatus();
});

window.addEventListener('offline', function() {
    showNotification('Connection lost. Please check your network.', 'error');
    statusText.textContent = 'Offline';
    statusDot.classList.remove('connected');
});