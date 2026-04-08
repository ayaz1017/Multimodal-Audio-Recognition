import axios from 'axios';

const DEFAULT_API_BASE_URL =
  process.env.NODE_ENV === 'production' ? '/api' : 'http://localhost:5002/api';

const API_BASE_URL = process.env.REACT_APP_API_URL || DEFAULT_API_BASE_URL;

const API_ORIGIN = API_BASE_URL.replace(/\/api\/?$/, '');

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const buildAnalysisFormData = (file, patientId, notes) => {
  const formData = new FormData();
  formData.append('file', file);

  if (patientId) {
    formData.append('patient_id', patientId);
  }

  if (notes) {
    formData.append('notes', notes);
  }

  return formData;
};

// Audio recognition
export const recognizeAudio = async (audioFile, patientId = null, notes = '') => {
  const formData = buildAnalysisFormData(audioFile, patientId, notes);

  return apiClient.post('/recognize_audio', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
      ...getAuthHeaders(),
    },
  });
};

// Video recognition (facial expressions)
export const recognizeVideo = async (videoFile, patientId = null, notes = '') => {
  const formData = buildAnalysisFormData(videoFile, patientId, notes);

  return apiClient.post('/recognize_video', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
      ...getAuthHeaders(),
    },
  });
};

// Multimodal recognition
export const recognizeMultimodal = async (videoFile, patientId = null, notes = '') => {
  const formData = buildAnalysisFormData(videoFile, patientId, notes);

  return apiClient.post('/recognize_multimodal', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
      ...getAuthHeaders(),
    },
  });
};

// Patients
export const getPatients = async () => {
  return apiClient.get('/patients', {
    headers: {
      ...getAuthHeaders(),
    },
  });
};

export const createPatient = async (payload) => {
  return apiClient.post('/patients', payload, {
    headers: {
      ...getAuthHeaders(),
    },
  });
};

export const getPatientAnalysis = async (patientId) => {
  return apiClient.get(`/patients/${patientId}/analysis`, {
    headers: {
      ...getAuthHeaders(),
    },
  });
};

// Reports
export const getPatientReports = async (patientId) => {
  return apiClient.get(`/reports/${patientId}`, {
    headers: {
      ...getAuthHeaders(),
    },
  });
};

export const getReportDetail = async (reportId) => {
  return apiClient.get(`/reports/detail/${reportId}`, {
    headers: {
      ...getAuthHeaders(),
    },
  });
};

// Health check
export const healthCheck = async () => {
  try {
    return await axios.get(`${API_ORIGIN}/health`);
  } catch (primaryError) {
    // Fallback for local setups still using the legacy default backend port.
    if (!process.env.REACT_APP_API_URL) {
      return axios.get('http://localhost:5000/health');
    }
    throw primaryError;
  }
};

export default apiClient;
