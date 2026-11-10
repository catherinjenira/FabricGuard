import apiClient from './api';

export const inspectionService = {
  // Single Image Inspection
  async inspectSingle(file, options = {}) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('fabric_type', options.fabricType || 'cotton_weave');
    formData.append('enhance_clahe', options.enhanceClahe ?? true);
    formData.append('confidence_threshold', options.confidenceThreshold ?? 0.50);

    return apiClient.post('/inspection/single', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: options.onProgress
    });
  },

  // Batch Inspection
  async inspectBatch(files, options = {}) {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    formData.append('batch_name', options.batchName || 'Fabric Roll Batch');
    formData.append('fabric_type', options.fabricType || 'cotton_weave');
    formData.append('enhance_clahe', options.enhanceClahe ?? true);
    formData.append('confidence_threshold', options.confidenceThreshold ?? 0.50);

    return apiClient.post('/batch/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: options.onProgress
    });
  },

  // Inspection by ID
  async getInspection(id) {
    return apiClient.get(`/inspection/${id}`);
  },

  // Batch by ID
  async getBatch(id) {
    return apiClient.get(`/batch/${id}`);
  },

  // History with pagination & filters
  async getHistory(params = {}) {
    return apiClient.get('/history', { params });
  },

  // Delete an inspection
  async deleteInspection(id) {
    return apiClient.delete(`/history/${id}`);
  },

  // Human Review Queue
  async getReviewQueue() {
    return apiClient.get('/review/queue');
  },

  // Submit Review Decision
  async submitReviewDecision(id, decisionData) {
    return apiClient.post(`/review/${id}/decision`, decisionData);
  },

  // Analytics & Evaluation
  async getDashboardStats() {
    return apiClient.get('/evaluation/stats');
  },

  async getModelMetrics() {
    return apiClient.get('/evaluation/metrics');
  },

  async getDefectDistribution() {
    return apiClient.get('/evaluation/defect-distribution');
  },

  getExportCsvUrl() {
    const base = import.meta.env.VITE_API_BASE_URL || '/api';
    return `${base}/history/export/csv`;
  }
};

export default inspectionService;

