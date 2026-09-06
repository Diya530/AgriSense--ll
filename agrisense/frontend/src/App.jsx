import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'

import Landing from './pages/Landing'
import Dashboard from './pages/Dashboard'
import Chatbot from './pages/Chatbot'
import Weather from './pages/Weather'
import CropRecommendation from './pages/CropRecommendation'
import SoilAnalysis from './pages/SoilAnalysis'
import PlantHealth from './pages/PlantHealth'
import Irrigation from './pages/Irrigation'
import Market from './pages/Market'
import Profile from './pages/Profile'
import Settings from './pages/Settings'

// No-login MVP: every app page is open, wrapped only in the sidebar Layout —
// no ProtectedRoute/auth check. The Landing page is a standalone entry point
// with its own "Open AgriSense" call to action straight into /dashboard.
function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />

      <Route path="/dashboard" element={<Layout><Dashboard /></Layout>} />
      <Route path="/chat" element={<Layout><Chatbot /></Layout>} />
      <Route path="/weather" element={<Layout><Weather /></Layout>} />
      <Route path="/crop-recommendation" element={<Layout><CropRecommendation /></Layout>} />
      <Route path="/soil-analysis" element={<Layout><SoilAnalysis /></Layout>} />
      <Route path="/plant-health" element={<Layout><PlantHealth /></Layout>} />
      <Route path="/irrigation" element={<Layout><Irrigation /></Layout>} />
      <Route path="/market" element={<Layout><Market /></Layout>} />
      <Route path="/profile" element={<Layout><Profile /></Layout>} />
      <Route path="/settings" element={<Layout><Settings /></Layout>} />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
