// TikTok Live Monitor - Frontend JavaScript

class TikTokMonitor {
    constructor() {
        this.ws = null;
        this.currentPage = 1;
        this.pageSize = 20;
        this.totalStreamers = 0;
        this.charts = {};
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;

        this.init();
    }

    init() {
        this.connectWebSocket();
        this.setupEventListeners();
        this.loadInitialData();
        this.startAutoRefresh();
    }

    // WebSocket Connection
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        try {
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                console.log('WebSocket connected');
                this.updateConnectionStatus(true);
                this.reconnectAttempts = 0;
                this.showToast('Conectado al servidor', 'success');
            };

            this.ws.onmessage = (event) => {
                const message = JSON.parse(event.data);
                this.handleWebSocketMessage(message);
            };

            this.ws.onclose = () => {
                console.log('WebSocket disconnected');
                this.updateConnectionStatus(false);
                this.attemptReconnect();
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus(false);
            };

        } catch (error) {
            console.error('Failed to create WebSocket:', error);
            this.updateConnectionStatus(false);
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 10000);

            this.showToast(`Reconectando en ${delay/1000}s...`, 'warning');

            setTimeout(() => {
                console.log(`Reconnect attempt ${this.reconnectAttempts}`);
                this.connectWebSocket();
            }, delay);
        } else {
            this.showToast('No se pudo reconectar. Recarga la página.', 'error');
        }
    }

    handleWebSocketMessage(message) {
        console.log('WebSocket message:', message);

        switch (message.type) {
            case 'scan_complete':
                this.showToast('Escaneo completado', 'success');
                this.loadStreamers();
                this.loadStatistics();
                break;
            case 'new_streamer':
                this.showToast(`Nuevo streamer: @${message.data.username}`, 'info');
                this.loadStreamers();
                break;
            case 'pong':
                // Heartbeat response
                break;
            default:
                console.log('Unknown message type:', message.type);
        }
    }

    updateConnectionStatus(connected) {
        const indicator = document.getElementById('status-indicator');
        const text = document.getElementById('status-text');

        if (connected) {
            indicator.classList.remove('offline');
            indicator.classList.add('online');
            text.textContent = 'Conectado';
        } else {
            indicator.classList.remove('online');
            indicator.classList.add('offline');
            text.textContent = 'Desconectado';
        }
    }

    // Event Listeners
    setupEventListeners() {
        document.getElementById('refresh-btn').addEventListener('click', () => {
            this.loadStreamers();
            this.loadStatistics();
        });

        document.getElementById('filter-query').addEventListener('change', () => {
            this.currentPage = 1;
            this.loadStreamers();
        });

        document.getElementById('filter-status').addEventListener('change', () => {
            this.currentPage = 1;
            this.loadStreamers();
        });

        document.getElementById('prev-page').addEventListener('click', () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                this.loadStreamers();
            }
        });

        document.getElementById('next-page').addEventListener('click', () => {
            const maxPage = Math.ceil(this.totalStreamers / this.pageSize);
            if (this.currentPage < maxPage) {
                this.currentPage++;
                this.loadStreamers();
            }
        });
    }

    // Data Loading
    async loadInitialData() {
        await this.loadQueries();
        await this.loadStreamers();
        await this.loadStatistics();
        await this.loadScanHistory();
    }

    async loadQueries() {
        try {
            const response = await fetch('/api/queries');
            const data = await response.json();

            if (data.success) {
                const select = document.getElementById('filter-query');
                data.data.forEach(query => {
                    const option = document.createElement('option');
                    option.value = query;
                    option.textContent = query;
                    select.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error loading queries:', error);
        }
    }

    async loadStreamers() {
        try {
            const query = document.getElementById('filter-query').value;
            const status = document.getElementById('filter-status').value;
            const offset = (this.currentPage - 1) * this.pageSize;

            let url = `/api/streamers?limit=${this.pageSize}&offset=${offset}`;
            if (query) url += `&query=${encodeURIComponent(query)}`;
            if (status) url += `&is_live=${status}`;

            const response = await fetch(url);
            const data = await response.json();

            if (data.success) {
                this.totalStreamers = data.total;
                this.renderStreamers(data.data);
                this.updatePagination();
            }
        } catch (error) {
            console.error('Error loading streamers:', error);
            this.showToast('Error cargando streamers', 'error');
        }
    }

    renderStreamers(streamers) {
        const tbody = document.getElementById('streamers-tbody');

        if (streamers.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="loading">No se encontraron streamers</td></tr>';
            return;
        }

        tbody.innerHTML = streamers.map(s => `
            <tr>
                <td>
                    <a href="https://www.tiktok.com/@${s.username}" target="_blank" class="username-link">
                        @${s.username}
                    </a>
                </td>
                <td><span class="badge">${s.query}</span></td>
                <td>
                    <span class="status-badge ${s.is_live ? 'live' : 'offline'}">
                        ${s.is_live ? '🔴 En Vivo' : '⚫ Offline'}
                    </span>
                </td>
                <td>${s.times_seen}</td>
                <td>${this.formatDate(s.first_seen)}</td>
                <td>${this.formatDate(s.last_seen)}</td>
                <td>
                    <button onclick="monitor.viewStreamer('${s.username}')" class="btn-small">
                        Ver
                    </button>
                </td>
            </tr>
        `).join('');

        this.updateLastUpdate();
    }

    async loadStatistics() {
        try {
            const response = await fetch('/api/statistics?hours=24');
            const data = await response.json();

            if (data.success) {
                const stats = data.data;

                // Update stat cards
                document.getElementById('total-streamers').textContent = stats.total_streamers;
                document.getElementById('live-streamers').textContent = stats.live_streamers;
                document.getElementById('total-scans').textContent = stats.recent_scans;

                const successRate = stats.recent_scans > 0
                    ? Math.round((stats.successful_scans / stats.recent_scans) * 100)
                    : 0;
                document.getElementById('success-rate').textContent = `${successRate}%`;

                // Update charts
                this.updateQueryChart(stats.streamers_by_query);
                this.updateScanHistoryChart(stats.scan_history);
            }
        } catch (error) {
            console.error('Error loading statistics:', error);
        }
    }

    async loadScanHistory() {
        try {
            const response = await fetch('/api/scan-history?limit=10');
            const data = await response.json();

            if (data.success) {
                this.renderScanHistory(data.data);
            }
        } catch (error) {
            console.error('Error loading scan history:', error);
        }
    }

    renderScanHistory(scans) {
        const container = document.getElementById('scans-list');

        if (scans.length === 0) {
            container.innerHTML = '<div class="loading">No hay historial de escaneos</div>';
            return;
        }

        container.innerHTML = scans.map(scan => `
            <div class="scan-item ${scan.success ? 'success' : 'failed'}">
                <div class="scan-header">
                    <span class="scan-query">${scan.query}</span>
                    <span class="scan-time">${this.formatDate(scan.timestamp)}</span>
                </div>
                <div class="scan-details">
                    <span>${scan.streamers_found} streamers encontrados</span>
                    ${!scan.success ? `<span class="error-msg">${scan.error_message}</span>` : ''}
                </div>
            </div>
        `).join('');
    }

    // Charts
    updateQueryChart(data) {
        const ctx = document.getElementById('queryChart');

        if (this.charts.queryChart) {
            this.charts.queryChart.destroy();
        }

        this.charts.queryChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.map(d => d.query),
                datasets: [{
                    data: data.map(d => d.count),
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56',
                        '#4BC0C0',
                        '#9966FF',
                        '#FF9F40'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    updateScanHistoryChart(data) {
        const ctx = document.getElementById('scanHistoryChart');

        if (this.charts.scanHistoryChart) {
            this.charts.scanHistoryChart.destroy();
        }

        const sortedData = [...data].reverse();

        this.charts.scanHistoryChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: sortedData.map(d => this.formatTime(d.timestamp)),
                datasets: [{
                    label: 'Streamers Encontrados',
                    data: sortedData.map(d => d.streamers_found),
                    borderColor: '#36A2EB',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }

    // Utility Functions
    updatePagination() {
        const maxPage = Math.ceil(this.totalStreamers / this.pageSize);
        document.getElementById('page-info').textContent =
            `Página ${this.currentPage} de ${maxPage || 1} (${this.totalStreamers} total)`;

        document.getElementById('prev-page').disabled = this.currentPage === 1;
        document.getElementById('next-page').disabled = this.currentPage >= maxPage;
    }

    formatDate(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleString('es-ES', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    formatTime(dateString) {
        if (!dateString) return '-';
        const date = new Date(dateString);
        return date.toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    updateLastUpdate() {
        document.getElementById('last-update-text').textContent =
            `Última actualización: ${new Date().toLocaleString('es-ES')}`;
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;

        container.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('show');
        }, 10);

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    viewStreamer(username) {
        window.open(`https://www.tiktok.com/@${username}`, '_blank');
    }

    startAutoRefresh() {
        // Auto-refresh every 2 minutes
        setInterval(() => {
            this.loadStreamers();
        }, 120000);

        // Send WebSocket ping every 30 seconds
        setInterval(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send('ping');
            }
        }, 30000);
    }
}

// Initialize the monitor when DOM is ready
let monitor;
document.addEventListener('DOMContentLoaded', () => {
    monitor = new TikTokMonitor();
});
