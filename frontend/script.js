const API_BASE_URL = 'http://127.0.0.1:8000';

// In-memory data store for client-side filtering
let allLogs = [];
let allAnomalies = [];
let currentAnomalyFilter = 'all';

function showSection(sectionName) {
    // Hide all sections
    const sections = document.querySelectorAll('.section-view');
    sections.forEach(section => {
        section.classList.remove('active');
    });

    // Show target
    const target = document.getElementById('section-' + sectionName);
    if (target) {
        target.classList.add('active');
    }

    // Update nav styling
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        const text = item.innerText.trim();
        if (text.toLowerCase().includes(sectionName.toLowerCase())) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}

// LOGS FILTERING
function applyLogsFilters() {
    const searchText = document.getElementById('logs-search').value.toLowerCase();
    const dateText = document.getElementById('logs-date-filter').value.toLowerCase();

    const filteredLogs = allLogs.filter(log => {
        const process = Array.isArray(log.processes) ? log.processes.join(', ') : (log.process || 'N/A');
        const matchesSearch = process.toLowerCase().includes(searchText);
        const matchesDate = (log.timestamp || '').toLowerCase().includes(dateText);
        return matchesSearch && matchesDate;
    });

    renderLogs(filteredLogs);
}

function resetLogsFilters() {
    document.getElementById('logs-search').value = '';
    document.getElementById('logs-date-filter').value = '';
    renderLogs(allLogs);
}

function renderLogs(logs) {
    const logsTableBody = document.getElementById('logs-table-body');
    logsTableBody.innerHTML = '';

    logs.forEach(log => {
        const row = document.createElement('tr');

        const timestampCell = document.createElement('td');
        timestampCell.className = 'code-font';
        timestampCell.innerText = log.timestamp || 'N/A';

        const processCell = document.createElement('td');
        processCell.innerText = Array.isArray(log.processes) ? log.processes.join(', ') : (log.process || 'N/A');

        const cpuCell = document.createElement('td');
        cpuCell.innerText = log.cpu !== undefined ? `${log.cpu}%` : 'N/A';

        row.appendChild(timestampCell);
        row.appendChild(processCell);
        row.appendChild(cpuCell);
        logsTableBody.appendChild(row);
    });
}

// ANOMALIES FILTERING
function setAnomalyFilter(filter) {
    currentAnomalyFilter = filter;

    // Update UI buttons
    document.querySelectorAll('.btn-filter').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById('filter-' + filter).classList.add('active');

    applyAnomalyFilters();
}

function applyAnomalyFilters() {
    const searchText = document.getElementById('anomalies-search').value.toLowerCase();

    const filteredAnomalies = allAnomalies.filter(anomaly => {
        const status = (anomaly.status || 'pending').toLowerCase();
        const type = (anomaly.type || '').toLowerCase();
        const process = (anomaly.process || '').toLowerCase();
        const reason = (anomaly.reason || '').toLowerCase();

        const matchesStatus = currentAnomalyFilter === 'all' || status === currentAnomalyFilter;
        const matchesSearch = type.includes(searchText) || process.includes(searchText) || reason.includes(searchText);

        return matchesStatus && matchesSearch;
    });

    renderAnomalies(filteredAnomalies);
}

function resetAnomalyFilters() {
    document.getElementById('anomalies-search').value = '';
    setAnomalyFilter('all');
}

function renderAnomalies(anomalies) {
    const anomalyContainer = document.getElementById('anomaly-list-container');
    anomalyContainer.innerHTML = '';

    anomalies.forEach(anomaly => {
        const item = document.createElement('div');
        const status = (anomaly.status || 'pending').toLowerCase();
        const anomalyId = anomaly.id || anomaly.timestamp;

        item.className = `anomaly-item ${status === 'reviewed' ? 'status-reviewed' : ''}`;

        const riskRaw = anomaly.risk || anomaly.risk_level || 'Low';
        const risk = riskRaw.toLowerCase();

        if (risk === 'critical' || risk === 'high') {
            item.style.borderLeftColor = 'var(--error)';
        } else if (risk === 'warning' || risk === 'medium') {
            item.style.borderLeftColor = 'var(--secondary)';
        } else {
            item.style.borderLeftColor = '#10b981';
        }

        const iconMap = {
            'critical': 'priority_high',
            'high': 'priority_high',
            'warning': 'speed',
            'medium': 'speed',
            'low': 'schedule',
            'resolved': 'schedule'
        };
        const icon = iconMap[risk] || 'warning';

        const statusBadgeClass = status === 'reviewed' ? 'badge-success' : 'badge-warning';
        const actionText = status === 'reviewed' ? 'Mark as Pending' : 'Mark as Reviewed';

        item.innerHTML = `
            <div class="anomaly-info">
                <div class="anomaly-icon" style="${risk === 'low' || risk === 'resolved' ? 'background: rgba(16, 185, 129, 0.1); color: #10b981;' : ''}">
                    <span class="material-symbols-outlined">${icon}</span>
                </div>
                <div>
                    <p style="font-weight: 600;">${anomaly.type || 'Anomaly detected'}</p>
                    <p style="font-size: 12px; color: var(--on-surface-variant);">${anomaly.reason || 'N/A'} • ${anomaly.timestamp || ''}</p>
                    <div style="margin-top: 8px; display: flex; gap: 8px; align-items: center;">
                        <span class="badge ${statusBadgeClass}">${status}</span>
                        <span class="badge ${risk === 'critical' || risk === 'high' ? 'badge-error' : (risk === 'low' || risk === 'resolved' ? 'badge-success' : '')}">${riskRaw}</span>
                    </div>
                </div>
            </div>
            <button class="btn btn-outline btn-sm" onclick="updateAnomalyStatus('${anomalyId}', '${status}', this)">
                ${actionText}
            </button>
        `;
        anomalyContainer.appendChild(item);
    });
}

async function updateAnomalyStatus(anomalyId, currentStatus, button) {
    const newStatus = currentStatus === 'reviewed' ? 'pending' : 'reviewed';

    button.disabled = true;
    button.innerText = 'Updating...';

    try {
        const response = await fetch(`${API_BASE_URL}/anomalies/${anomalyId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status: newStatus }),
        });

        if (response.ok) {
            await fetchData();
        } else {
            console.error('Failed to update anomaly status');
            button.disabled = false;
            button.innerText = currentStatus === 'reviewed' ? 'Mark as Pending' : 'Mark as Reviewed';
        }
    } catch (error) {
        console.error('Error updating anomaly status:', error);
        button.disabled = false;
        button.innerText = currentStatus === 'reviewed' ? 'Mark as Pending' : 'Mark as Reviewed';
    }
}

async function fetchData() {
    try {
        let updateSuccessful = false;

        // Fetch summary
        const summaryRes = await fetch(`${API_BASE_URL}/summary`);
        if (summaryRes.ok) {
            const summary = await summaryRes.json();
            document.getElementById('stat-total-events').innerText = summary.total_events?.toLocaleString() || 0;
            document.getElementById('stat-anomalies-detected').innerText = summary.total_anomalies?.toLocaleString() || 0;
            document.getElementById('stat-active-processes').innerText = summary.unique_processes?.toLocaleString() || 0;
        }

        // Fetch logs
        const logsRes = await fetch(`${API_BASE_URL}/logs`);
        if (logsRes.ok) {
            allLogs = await logsRes.json();
            applyLogsFilters(); // Render with current filters
        }

        // Fetch anomalies
        const anomaliesRes = await fetch(`${API_BASE_URL}/anomalies`);
        if (anomaliesRes.ok) {
            allAnomalies = await anomaliesRes.json();
            applyAnomalyFilters(); // Render with current filters
            updateSuccessful = true;
        }

        if (updateSuccessful) {
            const now = new Date();
            const timeStr = now.toLocaleTimeString();
            const lastUpdatedElem = document.getElementById('last-updated');
            if (lastUpdatedElem) {
                lastUpdatedElem.innerText = `Last updated: ${timeStr}`;
            }
        }

    } catch (error) {
        console.error('Error fetching data from API:', error);
    }
}

// Initial fetch and set interval for auto-refresh
window.addEventListener('DOMContentLoaded', () => {
    fetchData();
    setInterval(fetchData, 7000);
});
