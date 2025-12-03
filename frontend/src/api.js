import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';    // For localhost: http://127.0.0.1:8000

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    // Add ngrok-skip-browser-warning header if using ngrok
    ...(API_URL.includes('ngrok') && { 'ngrok-skip-browser-warning': 'true' })
  }
});

// Response interceptor to handle HTML responses (e.g., ngrok warning pages)
apiClient.interceptors.response.use(
  (response) => {
    // Check if response is HTML instead of JSON
    const contentType = response.headers['content-type'] || '';
    if (contentType.includes('text/html')) {
      console.error('Received HTML instead of JSON. This might be an ngrok warning page.');
      return Promise.reject(new Error('Server returned HTML instead of JSON. Check API URL and CORS settings.'));
    }
    return response;
  },
  (error) => {
    return Promise.reject(error);
  }
);


export const searchDrugs = async (query) => {
  try {
    const response = await apiClient.get('/search', { 
      params: { q: query }
    });
    
    // Validate response data
    if (!response.data) {
      console.error("Empty response from API");
      return [];
    }
    
    // Ensure response is an array
    if (Array.isArray(response.data)) {
      return response.data;
    } else {
      console.error("API returned non-array response:", typeof response.data, response.data);
      return [];
    }
  } catch (error) {
    // Handle different error types
    if (error.response) {
      // Server responded with error status
      console.error("API Error Response:", error.response.status, error.response.data);
    } else if (error.request) {
      // Request made but no response
      console.error("API Error: No response received", error.request);
    } else {
      // Error in request setup
      console.error("API Error:", error.message);
    }
    // Always return empty array on error to prevent crashes
    return [];
  }
};

export const analyzeInteractions = async (medications, patient) => {
  try {
    // 1. Get Interactions & Resolved IDs
    const interRes = await apiClient.post('/analyze/interactions', { medications });
    const resolvedMap = interRes.data.resolved_medications;
    const drugIds = [...new Set(Object.values(resolvedMap))]; 
    
    // 2. Get Food Warnings (Parallel)
    const foodPromise = apiClient.post('/analyze/food', { drug_ids: drugIds });
    
    // 3. Get References (Parallel)
    const refPromise = apiClient.post('/analyze/references', { drug_ids: drugIds });
    
    // 4. Get AI Report (Sequential - Needs interaction data)
    // Updated to handle the new structured response format
    let reportData = { clinical_analysis: "No interactions found.", analysis_cards: [] };
    
    if (interRes.data.interactions_found && interRes.data.interactions_found.length > 0) {
        const reportRes = await apiClient.post('/analyze/report', {
          interactions: interRes.data.interactions_found,
          patient: patient,
          drug_ids: drugIds
        });
        reportData = reportRes.data;
    }

    const [foodRes, refRes] = await Promise.all([foodPromise, refPromise]);

    return {
      interactions: interRes.data,
      food: foodRes.data,
      references: refRes.data,
      report: reportData
    };
  } catch (error) {
    console.error("Analysis Error:", error);
    throw error; // Re-throw to let component handle it
  }
};