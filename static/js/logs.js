// Initialize Lucide icons
lucide.createIcons();

// Auto-refresh variables
let autoRefreshInterval = null;

// Initial logs load
refreshLogs();

// Setup auto-refresh toggle
document.getElementById('auto-refresh').addEventListener('change', function() {
    if (this.checked) {
        startAutoRefresh();
    } else {
        stopAutoRefresh();
    }
});

async function refreshLogs() {
    const linesSelect = document.getElementById('lines-select');
    const lines = linesSelect.value;
    const logStatus = document.getElementById('log-status');
    const logsContent = document.getElementById('logs-content');
    
    logStatus.textContent = 'Loading...';
    
    try {
        const response = await fetch(`/api/logs?lines=${lines}`);
        const result = await response.json();
        
        if (result.success) {
            logsContent.textContent = result.logs;
            logStatus.textContent = `Last ${lines} lines`;
            
            // Scroll to bottom
            logsContent.scrollTop = logsContent.scrollHeight;
        } else {
            logsContent.textContent = `Error: ${result.message}`;
            logStatus.textContent = 'Error';
        }
    } catch (error) {
        logsContent.textContent = `Error fetching logs: ${error.message}`;
        logStatus.textContent = 'Error';
    }
}

function startAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    
    autoRefreshInterval = setInterval(refreshLogs, 5000);
    console.log('Auto-refresh started');
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
        console.log('Auto-refresh stopped');
    }
}

function clearLogs() {
    const logsContent = document.getElementById('logs-content');
    logsContent.textContent = 'Logs cleared. Click Refresh to reload.';
}

function downloadLogs() {
    const logsContent = document.getElementById('logs-content');
    const logsText = logsContent.textContent;
    
    if (!logsText || logsText.includes('Error')) {
        alert('No logs to download');
        return;
    }
    
    // Create blob and download
    const blob = new Blob([logsText], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `bot-logs-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}
