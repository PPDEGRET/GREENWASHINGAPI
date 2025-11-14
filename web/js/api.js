// web/js/api.js

const API_BASE_URL = "http://localhost:8000/api/v1";

export const apiFetch = async (endpoint, options = {}) => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        credentials: "include",
        ...options,
    });

    const contentType = response.headers.get("content-type") || "";

    if (!response.ok) {
        let errorBody = null;
        try {
            if (contentType.includes("application/json")) {
                errorBody = await response.json();
            } else {
                errorBody = await response.text();
            }
        } catch (e) {
            errorBody = null;
        }

        const error = new Error(`API request failed (${response.status})`);
        error.status = response.status;
        error.body = errorBody;
        throw error;
    }

    if (response.status === 204) return; // No content

    if (contentType.includes("application/json")) {
        return response.json();
    }
    return response;
};
