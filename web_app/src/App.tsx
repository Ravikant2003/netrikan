import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from '@theme/ThemeContext'
import { HomeScreen } from '@pages/HomeScreen'
import { RouteMapScreen } from '@pages/RouteMapScreen'
import { LiveTrackingScreen } from '@pages/LiveTrackingScreen'
import { EmergencyScreen } from '@pages/EmergencyScreen'
import { SafetyScoreScreen } from '@pages/SafetyScoreScreen'

/**
 * Main App Component
 * Routes all pages and manages global state
 */
const App: React.FC = () => {
  return (
    <ThemeProvider>
      <Router>
        <Routes>
          <Route path="/" element={<HomeScreen />} />
          <Route path="/route" element={<RouteMapScreen />} />
          <Route path="/tracking" element={<LiveTrackingScreen />} />
          <Route path="/emergency" element={<EmergencyScreen />} />
          <Route path="/safety" element={<SafetyScoreScreen />} />
        </Routes>
      </Router>
    </ThemeProvider>
  )
}

export default App
