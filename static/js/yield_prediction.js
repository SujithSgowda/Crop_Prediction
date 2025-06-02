// Yield Prediction Application - Main JavaScript Module
const YieldPredictionApp = {
    // Configuration
    config: {
        apiEndpoints: {
            predict: '/yield-prediction/predict/'
        },
        chartColors: {
            primary: 'rgba(245, 158, 11, 0.2)',
            border: 'rgb(245, 158, 11)',
            success: '#f59e0b',
            error: '#ef4444'
        }
    },

    // Application state
    state: {
        chart: null,
        isLoading: false,
        districts: {
            'Karnataka': ['Bangalore', 'Mysore', 'Belgaum', 'Gulbarga'],
            'Maharashtra': ['Pune', 'Nagpur', 'Nashik', 'Aurangabad'],
            'Tamil Nadu': ['Chennai', 'Coimbatore', 'Madurai', 'Trichy'],
            'Andhra Pradesh': ['Hyderabad', 'Visakhapatnam', 'Vijayawada', 'Guntur'],
            'Bihar': ['Patna', 'Gaya', 'Muzaffarpur', 'Bhagalpur'],
            'Gujarat': ['Ahmedabad', 'Surat', 'Vadodara', 'Rajkot'],
            'Madhya Pradesh': ['Bhopal', 'Indore', 'Jabalpur', 'Gwalior'],
            'Punjab': ['Ludhiana', 'Amritsar', 'Jalandhar', 'Patiala'],
            'Uttar Pradesh': ['Lucknow', 'Kanpur', 'Agra', 'Varanasi'],
            'West Bengal': ['Kolkata', 'Howrah', 'Durgapur', 'Asansol']
        }
    },

    // Initialize the application
    init() {
        this.setupCharts();
        this.setupFormSubmission();
        this.setupEventListeners();
        this.setupDistrictDropdown();
    },

    // Chart management
    setupCharts() {
        const chartContainer = this.createChartContainer();
        if (!document.getElementById('yieldHistoryChart')) {
            document.querySelector('.max-w-3xl')?.appendChild(chartContainer);
        }
    },

    createChartContainer() {
        const container = document.createElement('div');
        container.className = 'mt-8 p-6 bg-white rounded-lg shadow-sm';
        container.innerHTML = `
            <h3 class="text-xl font-semibold text-gray-900 mb-4">Yield History</h3>
            <div class="relative">
                <canvas id="yieldHistoryChart"></canvas>
                <div id="chartLoader" class="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75 hidden">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-500"></div>
                </div>
            </div>
        `;
        return container;
    },

    // District dropdown setup
    setupDistrictDropdown() {
        const stateSelect = document.getElementById('state');
        if (!stateSelect) return;

        stateSelect.addEventListener('change', () => {
            const state = stateSelect.value;
            const districtSelect = document.getElementById('district');
            districtSelect.innerHTML = '<option value="">Select District</option>';
            
            if (this.state.districts[state]) {
                this.state.districts[state].forEach(district => {
                    const option = document.createElement('option');
                    option.value = district;
                    option.textContent = district;
                    districtSelect.appendChild(option);
                });
            }
        });
    },

    // Form submission
    setupFormSubmission() {
        const form = document.getElementById('yieldForm');
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
            if (data.status === 'success') {
                this.displayPredictionResult(data);
            } else {
                this.showError(data.message || 'An error occurred while processing your request.');
            }
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
        document.querySelector('button[type="submit"]').innerHTML = 'Predict Yield';
    },

    // Display prediction result
    displayPredictionResult(data) {
        const resultContainer = document.getElementById('result');
        if (!resultContainer) return;

        // Update result values
        document.getElementById('yield-text').textContent = `${data.predicted_yield} quintal/hectare`;
        document.getElementById('production-text').textContent = `${data.predicted_production} quintals`;
        document.getElementById('historical-text').textContent = `${data.historical_avg_yield} quintal/hectare`;

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
            const form = document.getElementById('yieldForm');
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
    YieldPredictionApp.init();
});

// Export the application to the window object
window.YieldPredictionApp = YieldPredictionApp;