const API_BASE_URL = 'http://127.0.0.1:8000';

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

async function fetchData() {
    try {
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
            const logs = await logsRes.json();
            const logsTableBody = document.getElementById('logs-table-body');
            logsTableBody.innerHTML = '';

            logs.forEach(log => {
                const row = document.createElement('tr');

                const timestampCell = document.createElement('td');
                timestampCell.className = 'code-font';
                timestampCell.innerText = log.timestamp || 'N/A';

                const processCell = document.createElement('td');
                // If processes is an array, join them; otherwise use as is
                processCell.innerText = Array.isArray(log.processes) ? log.processes.join(', ') : (log.process || 'N/A');

                const cpuCell = document.createElement('td');
                cpuCell.innerText = log.cpu !== undefined ? `${log.cpu}%` : 'N/A';

                row.appendChild(timestampCell);
                row.appendChild(processCell);
                row.appendChild(cpuCell);
                logsTableBody.appendChild(row);
            });
        }

        // Fetch anomalies
        const anomaliesRes = await fetch(`${API_BASE_URL}/anomalies`);
        if (anomaliesRes.ok) {
            const anomalies = await anomaliesRes.json();
            const anomalyContainer = document.getElementById('anomaly-list-container');
            anomalyContainer.innerHTML = '';

            anomalies.forEach(anomaly => {
                const item = document.createElement('div');
                item.className = 'anomaly-item';

                // Risk level styling - check both 'risk' and 'risk_level' fields
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

                item.innerHTML = `
                    <div class="anomaly-info">
                        <div class="anomaly-icon" style="${risk === 'low' || risk === 'resolved' ? 'background: rgba(16, 185, 129, 0.1); color: #10b981;' : ''}">
                            <span class="material-symbols-outlined">${icon}</span>
                        </div>
                        <div>
                            <p style="font-weight: 600;">${anomaly.type || 'Anomaly detected'}</p>
                            <p style="font-size: 12px; color: var(--on-surface-variant);">${anomaly.reason || 'N/A'} • ${anomaly.timestamp || ''}</p>
                        </div>
                    </div>
                    <span class="badge ${risk === 'critical' || risk === 'high' ? 'badge-error' : (risk === 'low' || risk === 'resolved' ? 'badge-success' : '')}">${riskRaw}</span>
                `;
                anomalyContainer.appendChild(item);
            });
        }

    } catch (error) {
        console.error('Error fetching data from API:', error);
    }
}

// Load data on page load
window.addEventListener('DOMContentLoaded', fetchData);
