import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 45000, // give a cold Render instance up to 45s to wake up
})

client.interceptors.response.use(
  (response) => response,
  async (error) => {
    // If this looks like a cold-start/network-level failure (no response
    // came back at all) and we haven't retried yet, wait a moment and try
    // once more — covers the case where the backend was just waking up.
    const config = error.config
    if (!error.response && config && !config._retried) {
      config._retried = true
      await new Promise((resolve) => setTimeout(resolve, 3000))
      return client(config)
    }

    const message =
      error.response?.data?.detail ||
      error.message ||
      'Something went wrong. Please try again.'
    return Promise.reject(new Error(typeof message === 'string' ? message : 'Something went wrong.'))
  }
)

export default client