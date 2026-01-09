const API_BASE = '/api/workers';

/**
 * Helper to Convert JS Dates to backend-friendly ISO strings
 */
const formatDate = (date) => {
    if (!date) return '';
    return date.toISOString(); // Format: 2023-12-25T12:00:00.000Z
};

export const workerApi = {
    // GET /api/workers
    getAll: async () => {
        const res = await fetch(API_BASE);
        if (!res.ok) throw new Error('Failed to fetch workers');
        return res.json();
    },

    // POST /api/workers
    create: async (name, expirationDate, file) => {
        const formData = new FormData();
        formData.append('name', name);
        formData.append('expiration_date', formatDate(expirationDate));
        formData.append('file', file); // Required by backend

        const res = await fetch(API_BASE, {
            method: 'POST',
            body: formData, // No 'Content-Type' header needed; browser adds it automatically
        });
        
        if (!res.ok) {
            const txt = await res.text();
            throw new Error(txt || 'Failed to create worker');
        }
        return res.json();
    },

    // PUT /api/workers/<id>
    update: async (id, name, expirationDate, file) => {
        const formData = new FormData();
        if (name) formData.append('name', name);
        if (expirationDate) formData.append('expiration_date', formatDate(expirationDate));
        if (file) formData.append('file', file);

        const res = await fetch(`${API_BASE}/${id}`, {
            method: 'PUT',
            body: formData,
        });

        if (!res.ok) throw new Error('Failed to update worker');
        return res.json();
    },

    // PUT /api/workers/invalidate/<id>
    invalidate: async (id) => {
        const res = await fetch(`${API_BASE}/invalidate/${id}`, {
            method: 'PUT'
        });
        if (!res.ok) throw new Error('Failed to invalidate worker');
        return res.json();
    }
};