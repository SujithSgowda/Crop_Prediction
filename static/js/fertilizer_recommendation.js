// Fertilizer Recommendation Application - Main JavaScript Module
const FertilizerRecommendationApp = {
    // Configuration
    config: {
        apiEndpoints: {
            predict: '/fertilizer-recommendation/predict/'
        },
        chartColors: {
            primary: 'rgba(16, 185, 129, 0.2)',
            border: 'rgb(16, 185, 129)',
            success: '#10b981',
            error: '#ef4444'
        }
    },

    // Application state
    state: {
        isLoading: false
    },

    // Initialize the application
    init() {
        this.setupFormSubmission();
        this.setupEventListeners();
    },

    // Form submission
    setupFormSubmission() {
        const form = document.getElementById('fertilizerForm');
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
                this.displayRecommendationResult(data);
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
        document.querySelector('button[type="submit"]').innerHTML = 'Get Recommendation';
    },

    // Display recommendation result
    displayRecommendationResult(data) {
        // Show the result container
        const resultContainer = document.getElementById('result');
        if (!resultContainer) return;

        // Update the recommendation text
        const predictionElement = document.getElementById('prediction-text');
        if (predictionElement) {
            predictionElement.textContent = `Recommended Fertilizer: ${data.prediction}`;
        }

        const recommendationElement = document.getElementById('recommendation-text');
        if (recommendationElement) {
            recommendationElement.textContent = data.recommendation || '';
        }

        // Show the result container
        resultContainer.classList.remove('hidden');

        // Scroll to the result
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
            const form = document.getElementById('fertilizerForm');
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
    FertilizerRecommendationApp.init();
});

// Export the application to the window object
window.FertilizerRecommendationApp = FertilizerRecommendationApp;