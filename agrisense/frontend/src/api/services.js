import client from './client'

// No backend profile/auth/history endpoints in the stateless architecture —
// the farmer profile lives in localStorage (see utils/farmerProfile.js).
// Chat conversation history also lives in React state per browser tab, sent
// with each request rather than stored server-side.

export const weatherApi = {
  get: (params) => client.get('/weather', { params }),
}

export const chatApi = {
  send: (message, { language, history, farmerProfile } = {}) =>
    client.post('/chat', {
      message,
      language,
      history: history || [],
      farmer_profile: farmerProfile || null,
    }),
}

export const cropApi = {
  recommend: (data) => client.post('/crop/recommend', data),
}

export const soilApi = {
  analyze: (data) => client.post('/soil/analyze', data),
}

export const plantHealthApi = {
  analyze: (file) => {
    const form = new FormData()
    form.append('image', file)
    return client.post('/plant-health/analyze', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

export const irrigationApi = {
  advise: (data) => client.post('/irrigation/advise', data),
}

export const marketApi = {
  search: (q) => client.get('/market/search', { params: { q } }),
}
