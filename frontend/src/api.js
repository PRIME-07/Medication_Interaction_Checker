import axios from 'axios';

const API_URL = 'https://95a17939b18b.ngrok-free.app';

export const searchDrugs = async (query) => {
  try {
    const response = await axios.get(`${API_URL}/search`, { params: { q: query } });
    return response.data;
  } catch (error) {
    console.error("API Error:", error);
    return [];
  }
};

export const analyzeInteractions = async (medications, patient) => {
  // 1. Get Interactions & Resolved IDs
  const interRes = await axios.post(`${API_URL}/analyze/interactions`, { medications });
  const resolvedMap = interRes.data.resolved_medications;
  const drugIds = [...new Set(Object.values(resolvedMap))]; 
  
  // 2. Get Food Warnings (Parallel)
  const foodPromise = axios.post(`${API_URL}/analyze/food`, { drug_ids: drugIds });
  
  // 3. Get References (Parallel)
  const refPromise = axios.post(`${API_URL}/analyze/references`, { drug_ids: drugIds });
  
  // 4. Get AI Report (Sequential - Needs interaction data)
  // Updated to handle the new structured response format
  let reportData = { clinical_analysis: "No interactions found.", analysis_cards: [] };
  
  if (interRes.data.interactions_found.length > 0) {
      const reportRes = await axios.post(`${API_URL}/analyze/report`, {
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
};