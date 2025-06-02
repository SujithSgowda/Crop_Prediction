// Rainfall Prediction Application - Main JavaScript Module
const RainfallPredictionApp = {
    // Configuration
    config: {
        apiEndpoints: {
            predict: '/rainfall-prediction/predict/'
        },
        chartColors: {
            primary: 'rgba(59, 130, 246, 0.2)',
            border: 'rgb(59, 130, 246)',
            success: '#3b82f6',
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
        this.setupFormSubmission();
        this.setupEventListeners();
    },

    // Chart management
    setupCharts() {
        const chartContainer = this.createChartContainer();
        if (!document.getElementById('rainfallHistoryChart')) {
            document.querySelector('.max-w-3xl')?.appendChild(chartContainer);
        }
    },

    createChartContainer() {
        const container = document.createElement('div');
        container.className = 'mt-8 p-6 bg-white rounded-lg shadow-sm';
        container.innerHTML = `
            <h3 class="text-xl font-semibold text-gray-900 mb-4">Rainfall History</h3>
            <div class="relative">
                <canvas id="rainfallHistoryChart"></canvas>
                <div id="chartLoader" class="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75 hidden">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                </div>
            </div>
        `;
        return container;
    },

    // Form submission
    setupFormSubmission() {
        const form = document.getElementById('rainfallForm');
        if (!form) return;

        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitForm(form);
        });
    },

    submitForm(form) {
        if (this.state.isLoading) return;

        // Show loading state
        this.showLoading();

        // Get form data
        const formData = new FormData(form);

        // Send request to the server
        fetch(this.config.apiEndpoints.predict, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            this.hideLoading();
            this.displayPredictionResult(data);
        })
        .catch(error => {
            console.error('Error:', error);
            this.hideLoading();
            this.showError('An error occurred while processing your request. Please try again.');
        });
    },

    // Loading state management
    showLoading() {
        this.state.isLoading = true;
        document.querySelector('button[type="submit"]').disabled = true;
        document.querySelector('button[type="submit"]').innerHTML = 'Processing...';
    },

    hideLoading() {
        this.state.isLoading = false;
        document.querySelector('button[type="submit"]').disabled = false;
        document.querySelector('button[type="submit"]').innerHTML = 'Get Prediction';
    },

    // Display prediction result
    displayPredictionResult(data) {
        const resultContainer = document.getElementById('result');
        if (!resultContainer) return;

        // Update result values
        document.getElementById('prediction-text').textContent = `${data.prediction} mm`;
        document.getElementById('classification-text').textContent = data.classification;
        document.getElementById('historical-text').textContent = `${data.historical_avg} mm`;

        // Show result container
        resultContainer.classList.remove('hidden');

        // Scroll to result
        this.scrollToResult(resultContainer);
    },

    // Error handling
    showError(message) {
        const errorContainer = this.getOrCreateErrorContainer();
        errorContainer.textContent = message;
        errorContainer.classList.remove('hidden');
    },

    getOrCreateErrorContainer() {
        let errorContainer = document.getElementById('error-message');
        if (!errorContainer) {
            errorContainer = document.createElement('div');
            errorContainer.id = 'error-message';
            errorContainer.className = 'mt-4 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg hidden';
            const form = document.getElementById('rainfallForm');
            form.parentNode.insertBefore(errorContainer, form.nextSibling);
        }
        return errorContainer;
    },

    // Utility functions
    scrollToResult(element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    },

    setupEventListeners() {
        // Add any additional event listeners here
    }
};

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    RainfallPredictionApp.init();
});

// Export the application to the window object
window.RainfallPredictionApp = RainfallPredictionApp;