import axios from 'axios'

// Stateless backend: no server-side profile or auth. The farmer profile
// lives in localStorage (see utils/farmerProfile.js) and is sent as part of
// request bodies that need it (chat, irrigation).
const client = axios.create({
  baseURL: '/api',
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
