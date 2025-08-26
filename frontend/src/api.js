import axios from 'axios';

export const BASE_URL = import.meta.env?.VITE_API_URL || '/api';

function authHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function apiRequest(method, url, data = null, config = {}) {
  try {
    const res = await axios({
      method,
      url: BASE_URL + url,
      data,
      withCredentials: true,
      headers: { ...(config.headers || {}), ...authHeaders() },
      ...config,
    });
    return res.data;
  } catch (err) {
    // Extract error message and trace_id if available
    const detail = err.response?.data?.detail || err.message;
    const traceId = err.response?.data?.trace_id;
    throw { detail, traceId, status: err.response?.status };
  }
}

// Gesture API functions
export const getGestures = () => apiRequest('get', '/gestures');
export const createGesture = (payload) => apiRequest('post', '/gestures/', payload);
export const deleteGesture = (sessionId) => apiRequest('delete', `/gestures/${sessionId}`);
export const updateGesture = (sessionId, label) => apiRequest('put', `/gestures/${sessionId}?label=${label}`);

// Training API functions
export const getTrainingResults = () => apiRequest('get', '/training/');
export const getLatestTrainingResult = () => apiRequest('get', '/training/latest');
export const getTrainingMetrics = () => apiRequest('get', '/training/metrics/latest');
export const triggerTraining = (dualHand = false) => apiRequest('post', `/training/trigger?dual_hand=${dualHand}`);
export const runTraining = (file, dualHand = false) => {
  const formData = new FormData();
  formData.append('file', file);
  return apiRequest('post', `/training/run?dual_hand=${dualHand}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

// Dual-hand specific training functions
export const triggerDualHandTraining = () => apiRequest('post', '/training/dual-hand/trigger');
export const runDualHandTraining = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return apiRequest('post', '/training/dual-hand/run', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};
export const getDualHandData = () => apiRequest('get', '/training/dual-hand/data');
export const getDataInfo = () => apiRequest('get', '/training/data/info');

// Gesture conversion functions
export const convertGestureToDualHand = (sessionId) => apiRequest('post', `/training/convert-to-dual-hand/${sessionId}`);
export const checkConversionStatus = (sessionId) => apiRequest('get', `/training/conversion-status/${sessionId}`);

// Audio API functions
export const getAudioFiles = () => apiRequest('get', '/audio-files/');
export const uploadAudioFile = (file, uploader = 'unknown') => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('uploader', uploader);
  return apiRequest('post', '/audio-files/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};
export const deleteAudioFile = (filename) => apiRequest('delete', `/audio-files/${filename}`);
export const playAudioOnESP32 = (filename) => apiRequest('post', `/audio-files/${filename}/play`);
export const playAudioOnLaptop = (filename) => apiRequest('post', `/audio-files/${filename}/play-laptop`); 

export const api = {
  // Gestures
  getGestures,
  createGesture,
  deleteGesture,
  updateGesture,
  // Training
  getTrainingResults,
  getLatestTrainingResult,
  getTrainingMetrics,
  triggerTraining,
  runTraining,
  // Dual-hand training
  triggerDualHandTraining,
  runDualHandTraining,
  getDualHandData,
  getDataInfo,
  // Gesture conversion
  convertGestureToDualHand,
  checkConversionStatus,
  // Audio
  getAudioFiles,
  uploadAudioFile,
  deleteAudioFile,
  playAudioOnESP32,
  playAudioOnLaptop,
  // Core
  request: apiRequest,
};