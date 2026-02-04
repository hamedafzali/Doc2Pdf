// Initialize Lucide icons
lucide.createIcons();

// Auto-refresh status every 5 seconds
setInterval(updateStatus, 5000);

// Initial status load
updateStatus();

async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();
        
        updateStatusDisplay(status);
    } catch (error) {
        console.error('Error fetching status:', error);
    }
}

function updateStatusDisplay(status) {
    const statusContent = document.getElementById('status-content');
    const containerStatus = document.getElementById('container-status');
    const containerId = document.getElementById('container-id');
    const containerImage = document.getElementById('container-image');
    
    let statusHtml = '';
    let statusText = 'Unknown';
    let statusColor = 'gray';
    
    if (status.status === 'running') {
        statusHtml = `
            <div class="flex items-center space-x-3">
                <div class="w-3 h-3 bg-green-500 rounded-full animate-pulse-green"></div>
                <span class="text-green-600 font-medium">Bot is running</span>
            </div>
            <div class="text-sm text-gray-600">
                <p>Container ID: ${status.container_id}</p>
                <p>Created: ${new Date(status.created).toLocaleString()}</p>
            </div>
        `;
        statusText = 'Running';
        statusColor = 'green';
        containerId.textContent = status.container_id;
        containerImage.textContent = status.image;
    } else if (status.status === 'exited') {
        statusHtml = `
            <div class="flex items-center space-x-3">
                <div class="w-3 h-3 bg-red-500 rounded-full"></div>
                <span class="text-red-600 font-medium">Bot is stopped</span>
            </div>
            <div class="text-sm text-gray-600">
                <p>Container ID: ${status.container_id}</p>
                <p>Click "Start Bot" to restart</p>
            </div>
        `;
        statusText = 'Stopped';
        statusColor = 'red';
        containerId.textContent = status.container_id;
        containerImage.textContent = status.image;
    } else if (status.status === 'not_found') {
        statusHtml = `
            <div class="flex items-center space-x-3">
                <div class="w-3 h-3 bg-gray-500 rounded-full"></div>
                <span class="text-gray-600 font-medium">Container not found</span>
            </div>
            <div class="text-sm text-gray-600">
                <p>Click "Start Bot" to create and start the container</p>
            </div>
        `;
        statusText = 'Not Found';
        statusColor = 'gray';
        containerId.textContent = '-';
        containerImage.textContent = '-';
    } else if (status.status === 'docker_unavailable') {
        statusHtml = `
            <div class="flex items-center space-x-3">
                <div class="w-3 h-3 bg-red-500 rounded-full"></div>
                <span class="text-red-600 font-medium">Docker not available</span>
            </div>
            <div class="text-sm text-gray-600">
                <p>${status.message}</p>
            </div>
        `;
        statusText = 'Docker Error';
        statusColor = 'red';
        containerId.textContent = '-';
        containerImage.textContent = '-';
    } else {
        statusHtml = `
            <div class="flex items-center space-x-3">
                <div class="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <span class="text-yellow-600 font-medium">Error</span>
            </div>
            <div class="text-sm text-gray-600">
                <p>${status.message}</p>
            </div>
        `;
        statusText = 'Error';
        statusColor = 'yellow';
        containerId.textContent = '-';
        containerImage.textContent = '-';
    }
    
    statusContent.innerHTML = statusHtml;
    containerStatus.textContent = statusText;
    containerStatus.className = `text-2xl font-bold text-${statusColor}-600`;
}

async function startBot() {
    showNotification('Starting bot...', 'info');
    try {
        const response = await fetch('/api/start', { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
            showNotification(result.message, 'success');
        } else {
            showNotification(result.message, 'error');
        }
        updateStatus();
    } catch (error) {
        showNotification('Error starting bot', 'error');
    }
}

async function stopBot() {
    showNotification('Stopping bot...', 'info');
    try {
        const response = await fetch('/api/stop', { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
            showNotification(result.message, 'success');
        } else {
            showNotification(result.message, 'error');
        }
        updateStatus();
    } catch (error) {
        showNotification('Error stopping bot', 'error');
    }
}

async function restartBot() {
    showNotification('Restarting bot...', 'info');
    try {
        const response = await fetch('/api/restart', { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
            showNotification(result.message, 'success');
        } else {
            showNotification(result.message, 'error');
        }
        updateStatus();
    } catch (error) {
        showNotification('Error restarting bot', 'error');
    }
}

async function rebuildImage() {
    if (!confirm('This will rebuild the Docker image and restart the bot. Continue?')) {
        return;
    }
    
    showNotification('Rebuilding image...', 'info');
    try {
        const response = await fetch('/api/rebuild', { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
            showNotification(result.message, 'success');
        } else {
            showNotification(result.message, 'error');
        }
        updateStatus();
    } catch (error) {
        showNotification('Error rebuilding image', 'error');
    }
}

function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    const notificationText = document.getElementById('notification-text');
    const notificationIcon = document.getElementById('notification-icon');
    
    notificationText.textContent = message;
    
    // Set icon and color based on type
    if (type === 'success') {
        notificationIcon.setAttribute('data-lucide', 'check-circle');
        notification.className = 'fixed bottom-4 right-4 bg-green-100 border border-green-400 text-green-700 rounded-lg shadow-lg p-4 max-w-sm';
    } else if (type === 'error') {
        notificationIcon.setAttribute('data-lucide', 'x-circle');
        notification.className = 'fixed bottom-4 right-4 bg-red-100 border border-red-400 text-red-700 rounded-lg shadow-lg p-4 max-w-sm';
    } else {
        notificationIcon.setAttribute('data-lucide', 'info');
        notification.className = 'fixed bottom-4 right-4 bg-blue-100 border border-blue-400 text-blue-700 rounded-lg shadow-lg p-4 max-w-sm';
    }
    
    // Re-create icon
    lucide.createIcons();
    
    // Show notification
    notification.classList.remove('hidden');
    
    // Hide after 3 seconds
    setTimeout(() => {
        notification.classList.add('hidden');
    }, 3000);
}
