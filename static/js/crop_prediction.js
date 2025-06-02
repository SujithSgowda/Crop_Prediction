// Crop Prediction Application - Main JavaScript Module
const CropPredictionApp = {
    // Configuration
    config: {
        apiEndpoints: {
            predict: '/crop-prediction/predict/',
            recentPredictions: '/crop-prediction/api/recent_predictions/'
        },
        chartColors: {
            primary: 'rgba(34, 197, 94, 0.2)',
            border: 'rgb(34, 197, 94)',
            success: '#10b981',
            error: '#ef4444'
        }
    },

    // Application state
    state: {
        chart: null,
        isLoading: false
    },

    // Initialize the application
    init() {
        this.setupCharts();
        this.loadRecentPredictions();
        this.setupFormSubmission();
        this.setupEventListeners();
    },

    // Chart management
    setupCharts() {
        const chartContainer = this.createChartContainer();
        if (!document.getElementById('confidenceChart')) {
            document.querySelector('.max-w-3xl')?.appendChild(chartContainer);
        }
    },

    createChartContainer() {
        const container = document.createElement('div');
        container.className = 'mt-8 p-6 bg-white rounded-lg shadow-sm';
        container.innerHTML = `
            <h3 class="text-xl font-semibold text-gray-900 mb-4">Prediction History</h3>
            <div class="relative">
                <canvas id="confidenceChart"></canvas>
                <div id="chartLoader" class="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75 hidden">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500"></div>
                </div>
            </div>
        `;
        return container;
    },

    updateChart(predictions) {
        const canvas = document.getElementById('confidenceChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        // Destroy existing chart
        if (this.state.chart) {
            this.state.chart.destroy();
        }

        // Prepare data
        const labels = predictions.map(p => this.formatCropName(p.predicted_crop));
        const confidences = predictions.map(p => Math.round(parseFloat(p.confidence) || 0));

        // Create new chart
        this.state.chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Prediction Confidence (%)',
                    data: confidences,
                    backgroundColor: this.config.chartColors.primary,
                    borderColor: this.config.chartColors.border,
                    borderWidth: 2,
                    borderRadius: 4,
                    borderSkipped: false,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    title: {
                        display: true,
                        text: 'Recent Predictions Confidence Levels',
                        font: {
                            size: 16,
                            weight: 'bold'
                        },
                        padding: 20
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: 'white',
                        bodyColor: 'white',
                        borderColor: this.config.chartColors.border,
                        borderWidth: 1,
                        callbacks: {
                            label: (context) => `Confidence: ${context.parsed.y}%`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: (value) => value + '%'
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                }
            }
        });
    },

    // API interactions
    async loadRecentPredictions() {
        try {
            this.showChartLoader(true);
            const response = await fetch(this.config.apiEndpoints.recentPredictions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.updateChart(data);
        } catch (error) {
            console.error('Error loading predictions:', error);
            this.showChartError('Failed to load prediction history');
        } finally {
            this.showChartLoader(false);
        }
    },

    async submitPrediction(formData) {
        try {
            const data = this.prepareFormData(formData);
            
            const response = await fetch(this.config.apiEndpoints.predict, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.error) {
                throw new Error(result.error);
            }

            return result;
        } catch (error) {
            console.error('Prediction error:', error);
            throw error;
        }
    },

    // Form handling
    setupFormSubmission() {
        const form = document.querySelector('#predictionForm');
        if (!form) return;

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleFormSubmission(form);
        });
    },

    async handleFormSubmission(form) {
        const submitBtn = document.querySelector('#submitBtn');
        if (!submitBtn) return;

        try {
            this.setLoadingState(true, submitBtn);
            this.clearMessages();

            const formData = new FormData(form);
            const result = await this.submitPrediction(formData);

            this.displayPrediction(result);
            this.scrollToResult();
            
            // Refresh chart with new data
            await this.loadRecentPredictions();

        } catch (error) {
            this.showError(error.message || 'An error occurred while making the prediction. Please try again.');
        } finally {
            this.setLoadingState(false, submitBtn);
        }
    },

    prepareFormData(formData) {
        const data = {};
        formData.forEach((value, key) => {
            if (key !== 'csrfmiddlewaretoken') {
                const numValue = parseFloat(value);
                data[key] = isNaN(numValue) ? 0 : numValue;
            }
        });
        return data;
    },

    // UI state management
    setLoadingState(loading, submitBtn) {
        this.state.isLoading = loading;
        
        if (loading) {
            this.showLoading();
            submitBtn.disabled = true;
            submitBtn.innerHTML = `
                <div class="flex items-center justify-center">
                    <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Predicting...
                </div>
            `;
        } else {
            this.hideLoading();
            submitBtn.disabled = false;
            submitBtn.innerHTML = `
                <div class="flex items-center justify-center">
                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                    </svg>
                    Get Prediction
                </div>
            `;
        }
    },

    showLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'flex';
        }
    },

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    },

    showChartLoader(show) {
        const loader = document.getElementById('chartLoader');
        if (loader) {
            loader.classList.toggle('hidden', !show);
        }
    },

    // Display functions
    displayPrediction(result) {
        const container = this.getOrCreateResultContainer();
        
        container.innerHTML = `
            <div class="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl shadow-lg p-6 border border-gray-100 transform transition-all duration-300 hover:shadow-xl">
                <div class="flex items-center justify-between mb-6">
                    <h3 class="text-2xl font-bold text-gray-900 flex items-center">
                        <svg class="w-6 h-6 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        Prediction Result
                    </h3>
                    <span class="px-4 py-2 text-sm font-semibold text-green-800 bg-green-100 rounded-full">
                        ${result.confidence.toFixed(1)}% Confidence
                    </span>
                </div>
                
                <div class="space-y-6">
                    <div class="flex items-center justify-between p-6 bg-white rounded-lg shadow-sm border-l-4 border-green-500">
                        <div>
                            <p class="text-sm font-medium text-gray-500 mb-1">Recommended Crop</p>
                            <h4 class="text-2xl font-bold text-gray-900">${this.formatCropName(result.predicted_crop)}</h4>
                        </div>
                        <div class="text-green-500">
                            <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path>
                            </svg>
                        </div>
                    </div>

                    ${this.createConfidenceBar(result.confidence)}
                    ${this.createGrowingTipsSection(result.predicted_crop)}
                </div>
            </div>
        `;

        container.classList.remove('hidden');
        this.animateResult(container);
    },

    createConfidenceBar(confidence) {
        const confidenceClass = confidence >= 80 ? 'bg-green-500' : confidence >= 60 ? 'bg-yellow-500' : 'bg-red-500';
        
        return `
            <div class="bg-white rounded-lg p-4 shadow-sm">
                <div class="flex mb-2 items-center justify-between">
                    <span class="text-sm font-semibold text-gray-700">Prediction Confidence</span>
                    <span class="text-sm font-semibold text-gray-700">${confidence.toFixed(1)}%</span>
                </div>
                <div class="overflow-hidden h-3 text-xs flex rounded-full bg-gray-200">
                    <div style="width:${confidence}%" 
                         class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center ${confidenceClass} transition-all duration-1000 ease-out">
                    </div>
                </div>
            </div>
        `;
    },

    createGrowingTipsSection(crop) {
        const tips = this.getGrowingTips(crop);
        
        return `
            <div class="bg-white rounded-lg p-6 shadow-sm">
                <h4 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <svg class="w-5 h-5 text-green-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    Growing Tips for ${this.formatCropName(crop)}
                </h4>
                <ul class="space-y-3">
                    ${tips}
                </ul>
            </div>
        `;
    },

    getGrowingTips(crop) {
        const tips = {
            'rice': [
                'Best grown in flooded fields with temperatures between 21-37°C',
                'Requires continuous water supply and good drainage system',
                'Plant spacing should be 20×15 cm for optimal growth and yield',
                'Apply organic fertilizers during land preparation'
            ],
            'wheat': [
                'Ideal temperature range is 15-25°C during growing season',
                'Requires well-draining soil with good moisture retention',
                'Apply nitrogen fertilizer in split doses during growth stages',
                'Harvest when grain moisture is around 12-14%'
            ],
            'maize': [
                'Plant in full sun with soil temperature above 16°C',
                'Space plants 30-60 cm apart in rows for proper development',
                'Ensure regular watering especially during tasseling and silking',
                'Side-dress with nitrogen fertilizer when plants are knee-high'
            ],
            'cotton': [
                'Requires warm climate with temperatures between 18-35°C',
                'Plant in well-drained, fertile soil with pH 5.8-8.0',
                'Maintain consistent moisture during flowering and boll development',
                'Monitor for bollworm and other common pests regularly'
            ],
            'default': [
                'Ensure proper soil preparation and testing before planting',
                'Maintain consistent watering schedule based on crop needs',
                'Monitor for pests and diseases regularly throughout growing season',
                'Follow recommended fertilization program for optimal yield'
            ]
        };

        const cropTips = tips[crop.toLowerCase()] || tips['default'];
        return cropTips.map(tip => `
            <li class="flex items-start">
                <svg class="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <span class="text-gray-700">${tip}</span>
            </li>
        `).join('');
    },

    showError(message) {
        const container = this.getOrCreateErrorContainer();
        
        container.innerHTML = `
            <div class="bg-red-50 border-l-4 border-red-400 p-4 rounded-r-lg shadow-sm">
                <div class="flex items-center">
                    <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm text-red-700 font-medium">${message}</p>
                    </div>
                    <div class="ml-auto pl-3">
                        <button onclick="this.parentElement.parentElement.parentElement.remove()" 
                                class="text-red-400 hover:text-red-600 transition-colors">
                            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;

        container.classList.remove('hidden');
        
        // Auto-hide error after 8 seconds
        setTimeout(() => {
            if (container.parentNode) {
                container.classList.add('hidden');
            }
        }, 8000);
    },

    showChartError(message) {
        const chartContainer = document.getElementById('confidenceChart')?.parentElement;
        if (chartContainer) {
            chartContainer.innerHTML = `
                <div class="text-center py-8 text-gray-500">
                    <svg class="w-12 h-12 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <p>${message}</p>
                    <button onclick="CropPredictionApp.loadRecentPredictions()" 
                            class="mt-2 px-4 py-2 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors">
                        Try Again
                    </button>
                </div>
            `;
        }
    },

    // Utility functions
    getOrCreateResultContainer() {
        let container = document.getElementById('predictionResult');
        if (!container) {
            container = document.createElement('div');
            container.id = 'predictionResult';
            container.className = 'mt-8 hidden';
            document.querySelector('.max-w-3xl')?.appendChild(container);
        }
        return container;
    },

    getOrCreateErrorContainer() {
        let container = document.getElementById('errorMessage');
        if (!container) {
            container = document.createElement('div');
            container.id = 'errorMessage';
            container.className = 'mt-4 hidden';
            document.querySelector('#predictionForm')?.insertAdjacentElement('afterend', container);
        }
        return container;
    },

    clearMessages() {
        const errorContainer = document.getElementById('errorMessage');
        if (errorContainer) {
            errorContainer.classList.add('hidden');
        }
    },

    scrollToResult() {
        const resultContainer = document.getElementById('predictionResult');
        if (resultContainer) {
            setTimeout(() => {
                resultContainer.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start',
                    inline: 'nearest'
                });
            }, 100);
        }
    },

    animateResult(container) {
        container.style.opacity = '0';
        container.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            container.style.transition = 'opacity 0.5s ease-out, transform 0.5s ease-out';
            container.style.opacity = '1';
            container.style.transform = 'translateY(0)';
        }, 50);
    },

    formatCropName(crop) {
        return crop.charAt(0).toUpperCase() + crop.slice(1).toLowerCase();
    },

    // Event listeners
    setupEventListeners() {
        // Handle form input validation
        const form = document.querySelector('#predictionForm');
        if (form) {
            const inputs = form.querySelectorAll('input[type="number"]');
            inputs.forEach(input => {
                input.addEventListener('input', this.validateInput.bind(this));
            });
        }

        // Handle window resize for chart responsiveness
        window.addEventListener('resize', this.debounce(() => {
            if (this.state.chart) {
                this.state.chart.resize();
            }
        }, 250));
    },

    validateInput(event) {
        const input = event.target;
        const value = parseFloat(input.value);
        
        // Remove any existing validation messages
        const existingError = input.parentElement.querySelector('.validation-error');
        if (existingError) {
            existingError.remove();
        }

        // Basic validation
        if (input.hasAttribute('min') && value < parseFloat(input.min)) {
            this.showInputError(input, `Value must be at least ${input.min}`);
        } else if (input.hasAttribute('max') && value > parseFloat(input.max)) {
            this.showInputError(input, `Value must be at most ${input.max}`);
        }
    },

    showInputError(input, message) {
        const errorElement = document.createElement('p');
        errorElement.className = 'validation-error text-xs text-red-500 mt-1';
        errorElement.textContent = message;
        input.parentElement.appendChild(errorElement);
    },

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    CropPredictionApp.init();
});

// Export for global access if needed
window.CropPredictionApp = CropPredictionApp;