import './App.css';
import './styles/theme.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import ProtectedRoute from './components/ProtectedRoute';
import { ThemeProvider } from './context/ThemeContext';
import Home from './pages/Home';
import AudioRecognition from './pages/AudioRecognition';
import VideoRecognition from './pages/VideoRecognition';
import MultimodalRecognition from './pages/MultimodalRecognition';
import Login from './pages/Login';
import Signup from './pages/Signup';
import PatientDashboard from './pages/PatientDashboard';
import { healthCheck } from './services/api';

function App() {
  const [apiStatus, setApiStatus] = useState('checking');

  useEffect(() => {
    // Check API status on mount
    const checkStatus = async () => {
      try {
        await healthCheck();
        setApiStatus('connected');
      } catch (error) {
        setApiStatus('disconnected');
      }
    };

    checkStatus();
    // Check every 30 seconds
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <ThemeProvider>
      <Router>
        <div className="App">
          <Header apiStatus={apiStatus} />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />
              <Route path="/dashboard" element={
                <ProtectedRoute>
                  <PatientDashboard />
                </ProtectedRoute>
              } />
              <Route path="/audio" element={<AudioRecognition />} />
              <Route path="/video" element={<VideoRecognition />} />
              <Route path="/multimodal" element={<MultimodalRecognition />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
