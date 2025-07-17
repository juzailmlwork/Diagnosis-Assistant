// API Configuration
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

// API Endpoints
export const API_ENDPOINTS = {
  LOGIN: `${API_BASE_URL}/login`,
  CASES: (user_id: string) => `${API_BASE_URL}/cases/${user_id}`,
  SEARCH: `${API_BASE_URL}/search`,
  CASE: (case_id?: string) => (case_id ? `${API_BASE_URL}/case/${case_id}` : `${API_BASE_URL}/case`),
  UPLOAD_PDF: `${API_BASE_URL}/upload-pdf`,
}
