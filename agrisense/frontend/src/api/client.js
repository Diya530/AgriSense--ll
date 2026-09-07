import axios from 'axios'

// Stateless backend: no server-side profile or auth. The farmer profile
// lives in localStorage (see utils/farmerProfile.js) and is sent as part of
// request bodies that need it (chat, irrigation).
//
// baseURL resolution:
// - In production, set VITE_API_URL to your deployed backend's full URL
//   (e.g. https://agrisense-api.onrender.com/api) as a build-time env var.
// - In local dev, this falls back to '/api', which Vite's dev-server proxy
//   (see vite.config.js) forwards to localhost:8000.
const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
})

client.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.message ||
      'Something went wrong. Please try again.'
    return Promise.reject(new Error(typeof message === 'string' ? message : 'Something went wrong.'))
  }
)

export default client